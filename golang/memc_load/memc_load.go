package main

import (
	"bufio"
	"compress/gzip"
	"errors"
	"flag"
	"fmt"
	"github.com/bradfitz/gomemcache/memcache"
	"github.com/golang/protobuf/proto"
	"log"
	"os"
	"path/filepath"
	"reflect"
	"strconv"
	"strings"
)

const NormalErrRate = 0.01

type AppsInstalled struct {
	devType string
	devId   string
	lat     float64
	lon     float64
	apps    []uint32
}

type Options struct {
	dry     bool
	pattern string
	idfa    string
	gaid    string
	adid    string
	dvid    string
}

func insertAppsInstalled(memcPool map[string]*memcache.Client, memcAddr string, appsInstalled *AppsInstalled, dryRun bool) bool {
	ua := &UserApps{
		Lat:  proto.Float64(appsInstalled.lat),
		Lon:  proto.Float64(appsInstalled.lon),
		Apps: appsInstalled.apps,
	}
	key := fmt.Sprintf("%s:%s", appsInstalled.devType, appsInstalled.devId)
	packed, _ := proto.Marshal(ua)
	if dryRun {
		log.Printf("%s - %s -> %s", memcAddr, key, ua.String())
	} else {
		mc, ok := memcPool[memcAddr]
		if !ok {
			mc = memcache.New(memcAddr)
			memcPool[memcAddr] = mc
		}
		err := mc.Set(&memcache.Item{
			Key:   key,
			Value: packed,
		})
		if err != nil {
			log.Printf("Cannot write to memc %s: %v", memcAddr, err)
			return false
		}
	}
	return true
}

func parseAppsInstalled(line string) (*AppsInstalled, error) {
	lineParts := strings.Split(line, "\t")
	if len(lineParts) < 5 {
		return nil, errors.New("")
	}

	devType := lineParts[0]
	devId := lineParts[1]
	if devType == "" || devId == "" {
		return nil, errors.New("dev_type or dev_id was missed")
	}

	lat, err := strconv.ParseFloat(lineParts[2], 64)
	if err != nil {
		return nil, err
	}

	lon, err := strconv.ParseFloat(lineParts[3], 64)
	if err != nil {
		return nil, err
	}

	rawApps := lineParts[4]
	apps := make([]uint32, 0)
	for _, app := range strings.Split(rawApps, ",") {
		appId, _ := strconv.Atoi(app)
		apps = append(apps, uint32(appId))
	}

	return &AppsInstalled{
		devType: devType,
		devId:   devId,
		lat:     lat,
		lon:     lon,
		apps:    apps,
	}, nil
}

func processFile(fname string, options Options) {
	log.Println("Processing:", fname)
	f, err := os.Open(fname)
	if err != nil {
		log.Println(err)
	}
	defer f.Close()

	gz, err := gzip.NewReader(f)
	if err != nil {
		log.Println(err)
	}
	defer gz.Close()

	deviceMemc := map[string]string{
		"idfa": options.idfa,
		"gaid": options.gaid,
		"adid": options.adid,
		"dvid": options.dvid,
	}

	processed, errorsCount := 0, 0
	memcPool := map[string]*memcache.Client{}
	scanner := bufio.NewScanner(gz)
	for scanner.Scan() {
		line := scanner.Text()
		line = strings.Trim(line, " ")

		if line == "" {
			continue
		}

		appsInstalled, err := parseAppsInstalled(line)
		if err != nil {
			errorsCount += 1
			continue
		}

		memcAddr, ok := deviceMemc[appsInstalled.devType]
		if !ok {
			errorsCount += 1
			log.Println("Unknow device type:", appsInstalled.devType)
			continue
		}

		ok = insertAppsInstalled(memcPool, memcAddr, appsInstalled, options.dry)
		if ok {
			processed += 1
		} else {
			errorsCount += 1
		}
	}

	errRate := float32(errorsCount) / float32(processed)
	if errRate < NormalErrRate {
		log.Printf("Acceptable error rate (%g). Successfull load\n", errRate)
	} else {
		log.Printf("High error rate (%g > %g). Failed load\n", errRate, NormalErrRate)
	}
}

func prototest() {
	sample := "idfa\t1rfw452y52g2gq4g\t55.55\t42.42\t1423,43,567,3,7,23\ngaid\t7rfw452y52g2gq4g\t55.55\t42.42\t7423,424"
	for _, line := range strings.Split(sample, "\n") {
		appsInstalled, _ := parseAppsInstalled(line)
		ua := &UserApps{
			Lat:  proto.Float64(appsInstalled.lat),
			Lon:  proto.Float64(appsInstalled.lon),
			Apps: appsInstalled.apps,
		}
		packed, err := proto.Marshal(ua)
		if err != nil {
			log.Println(err)
		}

		unpacked := &UserApps{}
		err = proto.Unmarshal(packed, unpacked)
		if err != nil {
			log.Println(err)
		}

		if ua.GetLat() != unpacked.GetLat() || !reflect.DeepEqual(ua.GetApps(), unpacked.GetApps()) {
			os.Exit(1)
		}
	}
}

func dotRename(path string) {
	head := filepath.Dir(path)
	fn := filepath.Base(path)
	if err := os.Rename(path, filepath.Join(head, "."+fn)); err != nil {
		log.Fatalf("Can't rename a file: %s", path)
	}
}

func processFiles(options Options) {
	files, err := filepath.Glob(options.pattern)
	if err != nil {
		log.Fatalf("Could not find files for the given pattern: %s", options.pattern)
	}
	for _, fname := range files {
		processFile(fname, options)
		dotRename(fname)
	}
}

func main() {
	dry := flag.Bool("dry", false, "")
	test := flag.Bool("test", false, "")
	pattern := flag.String("pattern", "/data/appsinstalled/*.tsv.gz", "")
	logfile := flag.String("log", "", "")
	idfa := flag.String("idfa", "127.0.0.1:33013", "")
	gaid := flag.String("gaid", "127.0.0.1:33014", "")
	adid := flag.String("adid", "127.0.0.1:33015", "")
	dvid := flag.String("dvid", "127.0.0.1:33016", "")
	flag.Parse()

	options := Options{
		dry:     *dry,
		pattern: *pattern,
		idfa:    *idfa,
		gaid:    *gaid,
		adid:    *adid,
		dvid:    *dvid,
	}

	if *logfile != "" {
		f, err := os.OpenFile(*logfile, os.O_WRONLY|os.O_CREATE|os.O_APPEND, 0644)
		if err != nil {
			log.Fatalf("Cannot open log file: %s", logfile)
		}
		defer f.Close()
		log.SetOutput(f)
	}

	if *test {
		prototest()
		os.Exit(0)
	}

	log.Println("Memc loader started with options:", options)
	processFiles(options)
}

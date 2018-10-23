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

type Config struct {
	logfile    string
	nworkers   int
	bufsize    int
	pattern    string
	deviceMemc map[string]string
}

type MemcacheItem struct {
	key  string
	data []byte
}

type Stat struct {
	errors    int
	processed int
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

func SerializeAppsInstalled(appsInstalled *AppsInstalled) (*MemcacheItem, error) {
	ua := &UserApps{
		Lat:  proto.Float64(appsInstalled.lat),
		Lon:  proto.Float64(appsInstalled.lon),
		Apps: appsInstalled.apps,
	}
	key := fmt.Sprintf("%s:%s", appsInstalled.devType, appsInstalled.devId)
	packed, err := proto.Marshal(ua)
	if err != nil {
		log.Println(err)
		return nil, err
	}
	return &MemcacheItem{key, packed}, nil
}

func MemcacheWorker(mc *memcache.Client, items chan *MemcacheItem, resultsQueue chan Stat) {
	processed, errorsCount := 0, 0
	for item := range items {
		err := mc.Set(&memcache.Item{
			Key:   item.key,
			Value: item.data,
		})
		if err != nil {
			errorsCount += 1
		} else {
			processed += 1
		}
	}
	resultsQueue <- Stat{errorsCount, processed}
}

func LineParser(lines chan string, memcQueues map[string]chan *MemcacheItem, resultsQueue chan Stat) {
	errorsCount := 0
	for line := range lines {
		appsInstalled, err := parseAppsInstalled(line)
		if err != nil {
			errorsCount += 1
			continue
		}
		item, err := SerializeAppsInstalled(appsInstalled)
		if err != nil {
			errorsCount += 1
			continue
		}
		queue, ok := memcQueues[appsInstalled.devType]
		if !ok {
			log.Println("Unknow device type:", appsInstalled.devType)
			errorsCount += 1
			continue
		}
		queue <- item
	}
	resultsQueue <- Stat{errors: errorsCount}
}

func dotRename(path string) error {
	head := filepath.Dir(path)
	fn := filepath.Base(path)
	if err := os.Rename(path, filepath.Join(head, "."+fn)); err != nil {
		log.Printf("Can't rename a file: %s", path)
		return err
	}
	return nil
}

func fileReader(filename string, linesQueue chan string) error {
	log.Println("Processing:", filename)
	f, err := os.Open(filename)
	if err != nil {
		log.Printf("Can't open file: %s", filename)
		return err
	}
	defer f.Close()

	gz, err := gzip.NewReader(f)
	if err != nil {
		log.Printf("Can't create a new Reader %v", err)
		return err
	}
	defer gz.Close()

	scanner := bufio.NewScanner(gz)
	for scanner.Scan() {
		line := scanner.Text()
		line = strings.Trim(line, " ")
		if line == "" {
			continue
		}
		linesQueue <- line
	}

	if err := scanner.Err(); err != nil {
		log.Printf("Scanner error: %v", err)
		return err
	}

	return nil
}

func processFiles(config *Config) error {
	files, err := filepath.Glob(config.pattern)
	if err != nil {
		log.Printf("Could not find files for the given pattern: %s", config.pattern)
		return err
	}

	resultsQueue := make(chan Stat)

	memcQueues := make(map[string]chan *MemcacheItem)
	for devType, memcAddr := range config.deviceMemc {
		memcQueues[devType] = make(chan *MemcacheItem, config.bufsize)
		mc := memcache.New(memcAddr)
		go MemcacheWorker(mc, memcQueues[devType], resultsQueue)
	}

	linesQueue := make(chan string, config.bufsize)
	for i := 0; i < config.nworkers; i++ {
		go LineParser(linesQueue, memcQueues, resultsQueue)
	}

	for _, filename := range files {
		fileReader(filename, linesQueue)
		dotRename(filename)
	}
	close(linesQueue)

	processed, errorsCount := 0, 0
	for i := 0; i < config.nworkers; i++ {
		results := <-resultsQueue
		processed += results.processed
		errorsCount += results.errors
	}

	for _, queue := range memcQueues {
		close(queue)
		results := <-resultsQueue
		processed += results.processed
		errorsCount += results.errors
	}

	errRate := float32(errorsCount) / float32(processed)
	if errRate < NormalErrRate {
		log.Printf("Acceptable error rate (%g). Successfull load\n", errRate)
	} else {
		log.Printf("High error rate (%g > %g). Failed load\n", errRate, NormalErrRate)
	}

	return nil
}

var (
	logfile  string
	pattern  string
	nworkers int
	bufsize  int
	idfa     string
	gaid     string
	adid     string
	dvid     string
)

func init() {
	flag.StringVar(&pattern, "pattern", "/data/appsinstalled/*.tsv.gz", "")
	flag.StringVar(&logfile, "log", "", "")
	flag.IntVar(&nworkers, "workers", 5, "")
	flag.IntVar(&bufsize, "bufsize", 10, "")
	flag.StringVar(&idfa, "idfa", "127.0.0.1:33013", "")
	flag.StringVar(&gaid, "gaid", "127.0.0.1:33014", "")
	flag.StringVar(&adid, "adid", "127.0.0.1:33015", "")
	flag.StringVar(&dvid, "dvid", "127.0.0.1:33016", "")
}

func newConfig() *Config {
	return &Config{
		logfile:  logfile,
		pattern:  pattern,
		nworkers: nworkers,
		bufsize:  bufsize,
		deviceMemc: map[string]string{
			"idfa": idfa,
			"gaid": gaid,
			"adid": adid,
			"dvid": dvid,
		},
	}
}

func main() {
	flag.Parse()
	config := newConfig()
	if config.logfile != "" {
		f, err := os.OpenFile(config.logfile, os.O_WRONLY|os.O_CREATE|os.O_APPEND, 0644)
		if err != nil {
			log.Fatalf("Cannot open log file: %s", config.logfile)
		}
		defer f.Close()
		log.SetOutput(f)
	}
	log.Println("Memc loader started with config:", config)
	processFiles(config)
}

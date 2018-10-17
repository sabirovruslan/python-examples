package main

import (
	"fmt"
	"github.com/jessevdk/go-flags"
	"log"
)

var options struct {
	dry     bool   `long:dry default:false`
	test    bool   `long:test default:false`
	pattern string `long:pattern default:"/data/appsinstalled/*.tsv.gz"`
	logfile string `long:log default:""`
	idfa    string `long:idfa default:"127.0.0.1:33013"`
	gaid    string `long:gaid default:"127.0.0.1:33014"`
	adid    string `long:adid default:"127.0.0.1:33015"`
	dvid    string `long:dvid default:"127.0.0.1:33016"`
}

func main() {
	flags.Parse(&options)
	log.Println("Memc loader started with options:")
	fmt.Println("Test flag dry: ", options.dry)
	fmt.Println("Test flag pattern: ", options.pattern)
}

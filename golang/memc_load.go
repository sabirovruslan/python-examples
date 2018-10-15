package main

import (
	"fmt"
	"time"
)

func printCount(c chan int) {
	v := 0
	for v >=0 {
		v = <-c
		fmt.Println("Чтение из канала: ", v)
	}
}

func main() {
	ch := make(chan int)
	go printCount(ch)
	a :=[]int{9, 8, 7, 6, 5, 4, 3, 2, 1, 0, -1, -2}
	for _, i := range a {
		ch<-i
	}
	time.Sleep(time.Millisecond + 1)
	fmt.Println("Ура работает!")
}
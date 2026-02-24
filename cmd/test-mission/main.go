package main

import (
	"fmt"
	"time"
)

func main() {
	for i := 1; i <= 5; i++ {
		fmt.Printf("Test mission tick %d\n", i)
		time.Sleep(time.Second)
	}
	fmt.Println("Test mission complete.")
}

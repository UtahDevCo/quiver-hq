package main

import (
	"bufio"
	"fmt"
	"os"
	"strings"
)

func main() {
	reader := bufio.NewReader(os.Stdin)
	fmt.Println("QUIVER_SIGNAL:NEED_INPUT")
	fmt.Println("Agent: Hello! I need your name to proceed. Please type it below:")

	text, _ := reader.ReadString('\n')
	name := strings.TrimSpace(text)

	fmt.Printf("Agent: Thank you, %s! I am now continuing with the mission...\n", name)
	fmt.Println("Agent: Mission complete.")
}

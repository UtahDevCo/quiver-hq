package main

import (
	"bufio"
	"fmt"
	"os"
	"strings"
)

func main() {
	reader := bufio.NewReader(os.Stdin)
	
	fmt.Println("Agent: I am about to perform a risky action: 'DELETE ALL COPIES OF THE INTERNET'.")
	fmt.Println("QUIVER_SIGNAL:REQUEST_APPROVAL Should I delete the internet?")

	text, _ := reader.ReadString('\n')
	response := strings.TrimSpace(text)

	if response == "APPROVED" {
		fmt.Println("Agent: Action approved. Deleting the internet... [just kidding]")
	} else {
		fmt.Println("Agent: Action denied. Aborting risky operation.")
	}
	fmt.Println("Agent: Mission complete.")
}

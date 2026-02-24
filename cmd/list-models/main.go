package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"bytes"
	"os/exec"

	"github.com/google/generative-ai-go/genai"
	"google.golang.org/api/iterator"
	"google.golang.org/api/option"
)

func main() {
	ctx := context.Background()
	apiKey := os.Getenv("GEMINI_API_KEY")
	if apiKey == "" {
		fmt.Println("GEMINI_API_KEY empty, reading from 1Password...")
		cmd := exec.Command("op", "read", "op://Personal/quiver-hq/GEMINI_API_KEY")
		var stderr bytes.Buffer
		cmd.Stderr = &stderr
		out, err := cmd.Output()
		if err != nil {
			log.Fatalf("failed to read from 1Password: %v\nStderr: %s", err, stderr.String())
		}
		apiKey = string(bytes.TrimSpace(out))
	}

	if apiKey == "" {
		log.Fatal("API Key is still empty")
	}
	fmt.Printf("Using API Key of length: %d\n", len(apiKey))

	client, err := genai.NewClient(ctx, option.WithAPIKey(apiKey))
	if err != nil {
		log.Fatal(err)
	}
	defer client.Close()

	iter := client.ListModels(ctx)
	for {
		m, err := iter.Next()
		if err == iterator.Done {
			break
		}
		if err != nil {
			log.Fatal(err)
		}
		fmt.Printf("Model: %s\n", m.Name)
	}
}

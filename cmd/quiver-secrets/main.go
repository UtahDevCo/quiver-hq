package main

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"os/exec"
	"path/filepath"
	"strings"

	"github.com/joho/godotenv"
)

func main() {
	if len(os.Args) < 2 {
		fmt.Println("Usage: quiver-secrets [ingest|hydrate] [path]")
		os.Exit(1)
	}

	command := os.Args[1]
	path := "."
	if len(os.Args) > 2 {
		path = os.Args[2]
	}

	switch command {
	case "ingest":
		if err := ingest(path); err != nil {
			log.Fatalf("ingest failed: %v", err)
		}
	case "hydrate":
		if err := hydrate(path); err != nil {
			log.Fatalf("hydrate failed: %v", err)
		}
	default:
		fmt.Printf("Unknown command: %s\n", command)
		os.Exit(1)
	}
}

func ingest(path string) error {
	envFiles := []string{".env", ".env.local", ".env.development"}
	var envPath string
	for _, f := range envFiles {
		p := filepath.Join(path, f)
		if _, err := os.Stat(p); err == nil {
			envPath = p
			break
		}
	}

	if envPath == "" {
		return fmt.Errorf("no .env file found in %s", path)
	}

	env, err := godotenv.Read(envPath)
	if err != nil {
		return err
	}

	itemName := filepath.Base(filepath.Dir(envPath))
	if itemName == "." || itemName == "/" {
		wd, _ := os.Getwd()
		itemName = filepath.Base(wd)
	}

	fmt.Printf("Ingesting %s into 1Password item '%s'...\n", envPath, itemName)

	// Build 'op' command to create/edit item
	// For simplicity, we'll use 'op item create --template' or similar.
	// Actually, 'op item create --category "Secure Note" --title itemName'
	// and then add fields.
	
	// Check if item exists
	checkCmd := exec.Command("op", "item", "get", itemName, "--format", "json")
	exists := checkCmd.Run() == nil

	args := []string{"item"}
	if exists {
		args = append(args, "edit", itemName)
	} else {
		args = append(args, "create", "--category", "Secure Note", "--title", itemName)
	}

	for k, v := range env {
		args = append(args, fmt.Sprintf("%s=%s", k, v))
	}

	cmd := exec.Command("op", args...)
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	if err := cmd.Run(); err != nil {
		return fmt.Errorf("failed to run 'op': %v", err)
	}

	// Create .env.tmpl
	tmplPath := filepath.Join(path, ".env.tmpl")
	tmplFile, err := os.Create(tmplPath)
	if err != nil {
		return err
	}
	defer tmplFile.Close()

	for k := range env {
		fmt.Fprintf(tmplFile, "%s={{ .%s }}\n", k, k)
	}

	fmt.Printf("Created template at %s\n", tmplPath)
	return nil
}

type OpItem struct {
	Fields []struct {
		Label string `json:"label"`
		Value string `json:"value"`
	} `json:"fields"`
}

func hydrate(path string) error {
	tmplPath := filepath.Join(path, ".env.tmpl")
	if _, err := os.Stat(tmplPath); err != nil {
		return fmt.Errorf(".env.tmpl not found at %s", tmplPath)
	}

	itemName := filepath.Base(filepath.Dir(tmplPath))
	if itemName == "." || itemName == "/" {
		wd, _ := os.Getwd()
		itemName = filepath.Base(wd)
	}

	fmt.Printf("Hydrating .env from 1Password item '%s'...\n", itemName)

	cmd := exec.Command("op", "item", "get", itemName, "--format", "json")
	output, err := cmd.Output()
	if err != nil {
		return fmt.Errorf("failed to get item from 1Password: %v", err)
	}

	var item OpItem
	if err := json.Unmarshal(output, &item); err != nil {
		return err
	}

	secrets := make(map[string]string)
	for _, f := range item.Fields {
		secrets[f.Label] = f.Value
	}

	tmplContent, err := os.ReadFile(tmplPath)
	if err != nil {
		return err
	}

	lines := strings.Split(string(tmplContent), "\n")
	var envLines []string
	for _, line := range lines {
		if strings.TrimSpace(line) == "" {
			continue
		}
		parts := strings.SplitN(line, "=", 2)
		if len(parts) != 2 {
			continue
		}
		key := parts[0]
		valTmpl := parts[1]

		// Simple replacement for {{ .KEY }}
		secretKey := strings.TrimSpace(strings.TrimSuffix(strings.TrimPrefix(valTmpl, "{{ ."), " }}"))
		if val, ok := secrets[secretKey]; ok {
			envLines = append(envLines, fmt.Sprintf("%s=%s", key, val))
		} else {
			fmt.Printf("Warning: Secret %s not found in 1Password\n", secretKey)
			envLines = append(envLines, line) // Keep template if not found? Or leave empty?
		}
	}

	envPath := filepath.Join(path, ".env")
	if err := os.WriteFile(envPath, []byte(strings.Join(envLines, "\n")), 0600); err != nil {
		return err
	}

	fmt.Printf("Hydrated %s\n", envPath)
	return nil
}

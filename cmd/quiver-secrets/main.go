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

const itemName = "quiver-hq"

func main() {
	if len(os.Args) < 2 {
		fmt.Println("Usage: quiver-secrets [ingest|hydrate] [path1] [path2] ...")
		os.Exit(1)
	}

	command := os.Args[1]
	paths := os.Args[2:]
	if len(paths) == 0 {
		paths = []string{"."}
	}

	for _, path := range paths {
		absPath, err := filepath.Abs(path)
		if err != nil {
			log.Fatalf("failed to get absolute path for %s: %v", path, err)
		}

		switch command {
		case "ingest":
			if err := ingestBatch(absPath); err != nil {
				log.Fatalf("ingest failed for %s: %v", path, err)
			}
		case "hydrate":
			if err := hydrateRecursive(absPath); err != nil {
				log.Fatalf("hydrate failed for %s: %v", path, err)
			}
		default:
			fmt.Printf("Unknown command: %s\n", command)
			os.Exit(1)
		}
	}
}

func ingestBatch(rootPath string) error {
	var envFiles []string
	err := filepath.Walk(rootPath, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		if !info.IsDir() && info.Name() == ".env.local" {
			envFiles = append(envFiles, path)
		}
		return nil
	})
	if err != nil {
		return err
	}

	if len(envFiles) == 0 {
		fmt.Printf("No .env.local files found in %s\n", rootPath)
		return nil
	}

	// Ensure item exists
	checkCmd := exec.Command("op", "item", "get", itemName, "--format", "json")
	checkOut, err := checkCmd.CombinedOutput()
	if err != nil {
		// Only create the item if it genuinely doesn't exist. Any other error
		// (e.g. duplicate items, auth failure) should be surfaced to the user
		// rather than silently creating yet another duplicate.
		outStr := string(checkOut)
		if !strings.Contains(outStr, "isn't an item") && !strings.Contains(outStr, "not found") {
			return fmt.Errorf("unexpected error checking 1Password item '%s': %v\nOutput: %s", itemName, err, outStr)
		}
		fmt.Printf("Creating 1Password item '%s' as API Credential...\n", itemName)
		createCmd := exec.Command("op", "item", "create", "--category", "API Credential", "--title", itemName)
		if out, err := createCmd.CombinedOutput(); err != nil {
			return fmt.Errorf("failed to create 1Password item: %v\nOutput: %s", err, string(out))
		}
	}

	for _, envPath := range envFiles {
		if err := ingestFile(rootPath, envPath); err != nil {
			fmt.Printf("Warning: failed to ingest %s: %v\n", envPath, err)
		}
	}

	return nil
}

func ingestFile(rootPath, envPath string) error {
	env, err := godotenv.Read(envPath)
	if err != nil {
		return err
	}

	// Calculate relative path for the section name
	relPath, err := filepath.Rel(rootPath, filepath.Dir(envPath))
	if err != nil {
		return err
	}

	// Include the base of the root path for more context (e.g., "tools/apps/gtd" instead of "apps/gtd")
	sectionName := filepath.Join(filepath.Base(rootPath), relPath)
	// Clean up the path (remove trailing slashes, dots)
	sectionName = filepath.Clean(sectionName)
	// Normalize path separators to forward slashes (Windows uses backslashes which 'op' treats as escape chars)
	sectionName = filepath.ToSlash(sectionName)
	// Replace periods with underscores to avoid 'op' syntax errors (e.g., "utahdevco.com" -> "utahdevco_com")
	sectionName = strings.ReplaceAll(sectionName, ".", "_")

	fmt.Printf("Ingesting %s into 1Password item '%s' section '%s'...\n", envPath, itemName, sectionName)

	args := []string{"item", "edit", itemName}
	for k, v := range env {
		// Syntax: [section.]field=value
		args = append(args, fmt.Sprintf("%s.%s=%s", sectionName, k, v))
	}

	cmd := exec.Command("op", args...)
	if out, err := cmd.CombinedOutput(); err != nil {
		return fmt.Errorf("failed to run 'op item edit': %v\nOutput: %s", err, string(out))
	}

	// Create/Update .env.tmpl
	tmplPath := filepath.Join(filepath.Dir(envPath), ".env.tmpl")
	tmplFile, err := os.Create(tmplPath)
	if err != nil {
		return err
	}
	defer tmplFile.Close()

	for k := range env {
		// New format: KEY={{ .SectionName.KEY }}
		fmt.Fprintf(tmplFile, "%s={{ .%s.%s }}\n", k, sectionName, k)
	}

	fmt.Printf("Created/Updated template at %s\n", tmplPath)
	return nil
}

type OpItem struct {
	Fields []struct {
		Label   string `json:"label"`
		Value   string `json:"value"`
		Section struct {
			Label string `json:"label"`
		} `json:"section"`
	} `json:"fields"`
}

func hydrateRecursive(rootPath string) error {
        // Fetch 1Password item once
        fmt.Printf("Fetching 1Password item '%s'...\n", itemName)
        cmd := exec.Command("op", "item", "get", itemName, "--format", "json")
        output, err := cmd.CombinedOutput()
        if err != nil {
                return fmt.Errorf("failed to get item from 1Password: %v\nOutput: %s", err, string(output))
        }

                var item OpItem

                if err := json.Unmarshal(output, &item); err != nil {
		return err
	}

	// Map of section -> key -> value
	secrets := make(map[string]map[string]string)
	for _, f := range item.Fields {
		section := f.Section.Label
		if section == "" {
			section = "unsectioned"
		}
		if _, ok := secrets[section]; !ok {
			secrets[section] = make(map[string]string)
		}
		secrets[section][f.Label] = f.Value
	}

	// Find all .env.tmpl files
	return filepath.Walk(rootPath, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		if !info.IsDir() && info.Name() == ".env.tmpl" {
			if err := hydrateFile(path, secrets); err != nil {
				fmt.Printf("Warning: failed to hydrate %s: %v\n", path, err)
			}
		}
		return nil
	})
}

func hydrateFile(tmplPath string, secrets map[string]map[string]string) error {
	fmt.Printf("Hydrating %s...\n", tmplPath)
	tmplContent, err := os.ReadFile(tmplPath)
	if err != nil {
		return err
	}

	lines := strings.Split(string(tmplContent), "\n")
	var envLines []string
	for _, line := range lines {
		line = strings.TrimSpace(line)
		if line == "" {
			continue
		}
		parts := strings.SplitN(line, "=", 2)
		if len(parts) != 2 {
			continue
		}
		key := parts[0]
		valTmpl := parts[1]

		// Format: {{ .SectionName.KEY }}
		// Remove {{ . and }}
		content := strings.TrimSpace(strings.TrimSuffix(strings.TrimPrefix(valTmpl, "{{ ."), " }}"))
		
		// Split into Section and Key
		dotParts := strings.SplitN(content, ".", 2)
		var section, secretKey string
		if len(dotParts) == 2 {
			section = dotParts[0]
			secretKey = dotParts[1]
		} else {
			// Backward compatibility or unsectioned
			section = "unsectioned"
			secretKey = content
		}

		if sec, ok := secrets[section]; ok {
			if val, ok := sec[secretKey]; ok {
				envLines = append(envLines, fmt.Sprintf("%s=%s", key, val))
				continue
			}
		}

		fmt.Printf("Warning: Secret %s.%s not found in 1Password\n", section, secretKey)
		envLines = append(envLines, line) // Keep template if not found
	}

	envPath := filepath.Join(filepath.Dir(tmplPath), ".env.local")
	if err := os.WriteFile(envPath, []byte(strings.Join(envLines, "\n")), 0600); err != nil {
		return err
	}

	fmt.Printf("Hydrated %s\n", envPath)
	return nil
}

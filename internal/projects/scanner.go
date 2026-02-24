package projects

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"gopkg.in/ini.v1"
)

type Scanner struct {
	RootDir string
}

func NewScanner(rootDir string) *Scanner {
	return &Scanner{RootDir: rootDir}
}

func (s *Scanner) ListSubmodules() (map[string]string, error) {
	gitModulesPath := filepath.Join(s.RootDir, ".gitmodules")
	if _, err := os.Stat(gitModulesPath); os.IsNotExist(err) {
		return make(map[string]string), nil
	}

	cfg, err := ini.Load(gitModulesPath)
	if err != nil {
		return nil, fmt.Errorf("failed to load .gitmodules: %v", err)
	}

	submodules := make(map[string]string)
	for _, section := range cfg.Sections() {
		name := section.Name()
		if strings.HasPrefix(name, "submodule \"") {
			// Extract name from: submodule "submodules/project-x"
			subName := strings.TrimSuffix(strings.TrimPrefix(name, "submodule \""), "\"")
			// Submodules are often named by their path, but we can also use the last part of the path as a friendly name
			friendlyName := filepath.Base(subName)
			
			path := section.Key("path").String()
			submodules[friendlyName] = path
		}
	}

	return submodules, nil
}

func (s *Scanner) GetProjectPath(name string) (string, error) {
	submodules, err := s.ListSubmodules()
	if err != nil {
		return "", err
	}

	path, ok := submodules[name]
	if !ok {
		// If not a submodule, check if it's a top-level directory (like 'nixos')
		fullPath := filepath.Join(s.RootDir, name)
		if info, err := os.Stat(fullPath); err == nil && info.IsDir() {
			return fullPath, nil
		}
		return "", fmt.Errorf("project %s not found", name)
	}

	return filepath.Join(s.RootDir, path), nil
}

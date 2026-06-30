package main

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
)

const (
	remoteHost = "nix"
	nixosPath  = "/home/chris/dev/quiver-hq/"
	macOSPath  = "/Users/chris/dev/quiver-hq/"
)

func main() {
	if len(os.Args) < 2 {
		printUsage()
		os.Exit(1)
	}

	cmd := os.Args[1]
	switch cmd {
	case "push":
		if err := runSync(true); err != nil {
			fmt.Printf("Error during push sync: %v\n", err)
			os.Exit(1)
		}
	case "pull":
		if err := runSync(false); err != nil {
			fmt.Printf("Error during pull sync: %v\n", err)
			os.Exit(1)
		}
	case "help", "-h", "--help":
		printUsage()
	default:
		fmt.Printf("Unknown command: %s\n", cmd)
		printUsage()
		os.Exit(1)
	}
}

func printUsage() {
	fmt.Println("Usage: quiver-sync <push|pull>")
	fmt.Println()
	fmt.Println("Commands:")
	fmt.Println("  push    Sync files from local machine to NixOS remote desktop (nix)")
	fmt.Println("  pull    Sync files from NixOS remote desktop (nix) to local machine")
}

func runSync(isPush bool) error {
	// If we are running on Linux (which is the NixOS remote desktop), print a warning.
	if runtime.GOOS == "linux" {
		return fmt.Errorf("quiver-sync is designed to be run from your local macOS machine to pull/push files from/to the NixOS desktop (nix)")
	}

	// First, check if rsync exists
	if _, err := exec.LookPath("rsync"); err != nil {
		return fmt.Errorf("rsync command not found in PATH; please install rsync first")
	}

	// Determine local path. Default to macOSPath.
	localPath := macOSPath

	// Try to find repository root dynamically if we are currently inside it.
	if cwd, err := os.Getwd(); err == nil {
		if root, found := findRepoRoot(cwd); found {
			localPath = root
		}
	}

	// Ensure localPath has a trailing slash for rsync
	if localPath[len(localPath)-1] != '/' {
		localPath += "/"
	}

	remotePathSpec := fmt.Sprintf("%s:%s", remoteHost, nixosPath)

	var src, dest string
	if isPush {
		src = localPath
		dest = remotePathSpec
		fmt.Printf("🚀 Starting Push Sync: Local (%s) -> Remote NixOS (%s)\n", src, dest)
	} else {
		src = remotePathSpec
		dest = localPath
		fmt.Printf("🚀 Starting Pull Sync: Remote NixOS (%s) -> Local (%s)\n", src, dest)
	}

	// Define rsync arguments.
	// We want to sync:
	// - Any directory named 'temp' and all its contents recursively.
	// - Any *.local.md files.
	// We exclude version control, dependencies, and build outputs to keep it fast.
	args := []string{
		"-avzu",                  // archive, verbose, compress, update (only newer files over receiver)
		"--prune-empty-dirs",     // Do not create empty directories on the receiving side
		"--no-owner",             // Do not preserve owner (prevents mapping/permission issues)
		"--no-group",             // Do not preserve group (prevents GID mapping issues like _lpoperator)
		"--exclude=.git/",        // Exclude git metadata
		"--exclude=node_modules/",// Exclude dependencies
		"--exclude=.direnv/",     // Exclude local dev environment cache
		"--exclude=.next/",       // Exclude Next.js build cache
		"--exclude=dist/",        // Exclude production build folders
		"--include=**/temp/",     // Include all folders named 'temp'
		"--include=**/temp/**",   // Include everything inside folders named 'temp'
		"--include=**/scratch/",  // Include all folders named 'scratch'
		"--include=**/scratch/**",// Include everything inside folders named 'scratch'
		"--include=**/*.local.md",// Include any *.local.md files
		"--include=*/",           // Include all directory structures so we can traverse them
		"--exclude=*",            // Exclude everything else not matched by rules above
		src,
		dest,
	}

	// Log command to be executed
	fmt.Printf("Running command: rsync %s\n\n", formatArgs(args))

	runCmd := exec.Command("rsync", args...)
	runCmd.Stdout = os.Stdout
	runCmd.Stderr = os.Stderr
	runCmd.Stdin = os.Stdin

	return runCmd.Run()
}

func findRepoRoot(startDir string) (string, bool) {
	dir := filepath.Clean(startDir)
	for {
		// Check for flake.nix or .git
		if _, err := os.Stat(filepath.Join(dir, "flake.nix")); err == nil {
			return dir, true
		}
		if _, err := os.Stat(filepath.Join(dir, ".git")); err == nil {
			return dir, true
		}
		parent := filepath.Dir(dir)
		if parent == dir {
			break
		}
		dir = parent
	}
	return "", false
}

func formatArgs(args []string) string {
	var res string
	for _, arg := range args {
		// Pretty-print flags without quotes, quote paths/patterns
		if len(arg) > 0 && (arg[0] == '-' || arg[len(arg)-1] == '*') {
			res += arg + " "
		} else {
			res += fmt.Sprintf("%q ", arg)
		}
	}
	return res
}

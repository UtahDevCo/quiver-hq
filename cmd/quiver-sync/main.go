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
)

func main() {
	if len(os.Args) < 2 {
		printUsage()
		os.Exit(1)
	}

	cmd := os.Args[1]
	dryRun := false
	for _, a := range os.Args[2:] {
		if a == "--dry-run" || a == "-n" {
			dryRun = true
		}
	}

	switch cmd {
	case "push":
		if err := runSync(true, dryRun); err != nil {
			fmt.Printf("Error during push sync: %v\n", err)
			os.Exit(1)
		}
	case "pull":
		if err := runSync(false, dryRun); err != nil {
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
	fmt.Println("Usage: quiver-sync <push|pull> [--dry-run]")
	fmt.Println()
	fmt.Println("Commands:")
	fmt.Println("  push    Sync files from local machine to NixOS remote desktop (nix)")
	fmt.Println("  pull    Sync files from NixOS remote desktop (nix) to local machine")
	fmt.Println()
	fmt.Println("Flags:")
	fmt.Println("  --dry-run, -n   List what would transfer without writing anything")
	fmt.Println()
	fmt.Println("Carries temp/ and scratch/ only. *.local.md travels by git in")
	fmt.Println("quiver-hq/local/ instead. Additive: nothing is ever deleted.")
}

func getDefaultLocalPath() string {
	if home, err := os.UserHomeDir(); err == nil {
		return filepath.Join(home, "dev", "quiver-hq")
	}
	return "/Users/christopher/dev/quiver-hq"
}

func runSync(isPush, dryRun bool) error {
	// If we are running on Linux (which is the NixOS remote desktop), print a warning.
	if runtime.GOOS == "linux" {
		return fmt.Errorf("quiver-sync is designed to be run from your local macOS machine to pull/push files from/to the NixOS desktop (nix)")
	}

	// First, check if rsync exists
	if _, err := exec.LookPath("rsync"); err != nil {
		return fmt.Errorf("rsync command not found in PATH; please install rsync first")
	}

	// Determine local path.
	localPath := getDefaultLocalPath()

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

	label := ""
	if dryRun {
		label = " [DRY RUN — nothing will be written]"
	}

	var src, dest string
	if isPush {
		src = localPath
		dest = remotePathSpec
		fmt.Printf("🚀 Starting Push Sync%s: Local (%s) -> Remote NixOS (%s)\n", label, src, dest)
	} else {
		src = remotePathSpec
		dest = localPath
		fmt.Printf("🚀 Starting Pull Sync%s: Remote NixOS (%s) -> Local (%s)\n", label, src, dest)
	}

	// Define rsync arguments.
	//
	// Scope: the working data in temp/ and scratch/ directories. These are
	// deliberately NOT committed to git, so rsync remains their transport.
	//
	// *.local.md is explicitly excluded: those now live in quiver-hq/local/ and
	// travel by git, symlinked into each project. Letting rsync touch them would
	// overwrite the symlinks with plain files and break that setup.
	//
	// Sync is additive by design (no --delete): deletions are done by hand on
	// each machine. -u also keeps a newer file on the receiver from being
	// clobbered by an older one from the sender.
	//
	// Text and images are carried; video, browser profiles, and the local-only
	// photo library never are.
	args := []string{
		"-avzu",              // archive, verbose, compress, update (only newer files over receiver)
		"--prune-empty-dirs", // Do not create empty directories on the receiving side
		"--no-owner",         // Do not preserve owner (prevents mapping/permission issues)
		"--no-group",         // Do not preserve group (prevents GID mapping issues like _lpoperator)
		"--max-size=25m",     // Backstop against anything unexpectedly huge

		// --- Hard denies. First match wins in rsync, so these precede the includes. ---
		"--exclude=.git/",         // Exclude git metadata
		"--exclude=node_modules/", // Exclude dependencies
		"--exclude=.direnv/",      // Exclude local dev environment cache
		"--exclude=.next/",        // Exclude Next.js build cache
		"--exclude=dist/",         // Exclude production build folders

		"--exclude=*.local.md", // Owned by git via quiver-hq/local/, never by rsync

		// Chrome profiles turn up under several names (chrome/, chrome-profile/,
		// chrome-profile-codex-env-test/). They are machine-local state, never shared.
		"--exclude=chrome/",
		"--exclude=chrome-profile*/",

		"--exclude=/projects/quiver-photos-v2/temp/", // Local-only photo library, not for sharing

		// Foundation is a former employer; these projects are being removed.
		"--exclude=/projects/foundation-web/",
		"--exclude=/projects/foundation-integrations/",

		// Video is never worth the transfer.
		"--exclude=*.mp4", "--exclude=*.MP4",
		"--exclude=*.mov", "--exclude=*.MOV",
		"--exclude=*.mkv", "--exclude=*.avi",
		"--exclude=*.webm", "--exclude=*.m4v",

		// Machine-local noise.
		"--exclude=.DS_Store",
		"--exclude=*.pma", // Chrome BrowserMetrics dumps
		"--exclude=*.zip",

		// --- What we actually carry. ---
		"--include=**/temp/",      // Include all folders named 'temp'
		"--include=**/temp/**",    // Include everything inside folders named 'temp'
		"--include=**/scratch/",   // Include all folders named 'scratch'
		"--include=**/scratch/**", // Include everything inside folders named 'scratch'
		"--include=*/",            // Include all directory structures so we can traverse them
		"--exclude=*",             // Exclude everything else not matched by rules above
	}

	if dryRun {
		args = append(args, "--dry-run")
	}
	args = append(args, src, dest)

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

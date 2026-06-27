package main

import (
	"encoding/json"
	"fmt"
	"io"
	"log"
	"os"
	"os/exec"
	"path/filepath"
	"sort"
	"strings"
	"time"
)

// Config represents the user-configurable settings.
type Config struct {
	ExcludeUnits            []string `json:"exclude_units"`
	ExcludeContainers       []string `json:"exclude_containers"`
	PauseDockerContainers   bool     `json:"pause_docker_containers"`
	MonitorIntervalSeconds  int      `json:"monitor_interval_seconds"`
}

// State represents the current sleep state of the system.
type State struct {
	Status           string            `json:"status"` // "awake" or "sleeping"
	SleepStarted     time.Time         `json:"sleep_started"`
	FrozenUnits      []string          `json:"frozen_units"`
	PausedContainers []string          `json:"paused_containers"`
	SavedGovernors   map[string]string `json:"saved_governors"`
}

// HistoryEntry represents a single periodic check logged to the history file.
type HistoryEntry struct {
	Timestamp      time.Time     `json:"timestamp"`
	Event          string        `json:"event,omitempty"` // "sleep_start", "wake" or empty for periodic checks
	CPUUsagePct    float64       `json:"cpu_usage_pct,omitempty"`
	MemoryUsedGB   float64       `json:"memory_used_gb,omitempty"`
	CPUTempC       float64       `json:"cpu_temp_c,omitempty"`
	RxBytes        uint64        `json:"rx_bytes,omitempty"`
	TxBytes        uint64        `json:"tx_bytes,omitempty"`
	TopProcesses   []ProcessStat `json:"top_processes,omitempty"`
}

type ProcessStat struct {
	PID  int     `json:"pid"`
	CPU  float64 `json:"cpu"`
	Name string  `json:"name"`
}

// CPUTick tracks cpu times for delta calculations.
type CPUTick struct {
	User, Nice, System, Idle, Iowait, Irq, Softirq, Steal uint64
}

var (
	defaultExcludeUnits = []string{
		"niri.service",
		"multica-daemon.service",
		"dbus-broker.service",
		"dconf.service",
		"gcr-ssh-agent.service",
		"gnome-keyring.service",
		"gvfs-afc-volume-monitor.service",
		"gvfs-daemon.service",
		"gvfs-goa-volume-monitor.service",
		"gvfs-gphoto2-volume-monitor.service",
		"gvfs-metadata.service",
		"gvfs-mtp-volume-monitor.service",
		"gvfs-udisks2-volume-monitor.service",
		"init.scope",
		"obex.service",
		"pipewire-pulse.service",
		"pipewire.service",
		"polkit-gnome-authentication-agent-1.service",
		"speech-dispatcher.service",
		"waybar.service",
		"wireplumber.service",
		"xdg-desktop-portal-gnome.service",
		"xdg-desktop-portal-gtk.service",
		"xdg-desktop-portal.service",
		"xdg-document-portal.service",
		"xdg-permission-store.service",
	}

	defaultExcludeContainers = []string{
		"fizzy",
	}
)

func getConfigPath() string {
	home, _ := os.UserHomeDir()
	return filepath.Join(home, ".config", "quiver-sleep", "config.json")
}

func getStatePath() string {
	home, _ := os.UserHomeDir()
	return filepath.Join(home, ".local", "share", "quiver-sleep", "state.json")
}

func getHistoryPath() string {
	home, _ := os.UserHomeDir()
	return filepath.Join(home, ".local", "share", "quiver-sleep", "sleep-history.jsonl")
}

// loadConfig reads the config file or returns defaults.
func loadConfig() *Config {
	cfg := &Config{
		ExcludeUnits:           defaultExcludeUnits,
		ExcludeContainers:      defaultExcludeContainers,
		PauseDockerContainers:  true,
		MonitorIntervalSeconds: 30,
	}

	cfgPath := getConfigPath()
	data, err := os.ReadFile(cfgPath)
	if err == nil {
		json.Unmarshal(data, cfg)
	} else {
		// Save default config if not exists
		os.MkdirAll(filepath.Dir(cfgPath), 0755)
		if data, err := json.MarshalIndent(cfg, "", "  "); err == nil {
			os.WriteFile(cfgPath, data, 0644)
		}
	}
	return cfg
}

// loadState reads the current state file.
func loadState() *State {
	state := &State{
		Status: "awake",
	}
	statePath := getStatePath()
	data, err := os.ReadFile(statePath)
	if err == nil {
		json.Unmarshal(data, state)
	}
	return state
}

// saveState writes state to file.
func saveState(state *State) error {
	statePath := getStatePath()
	os.MkdirAll(filepath.Dir(statePath), 0755)
	data, err := json.MarshalIndent(state, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(statePath, data, 0644)
}

func main() {
	if len(os.Args) < 2 {
		fmt.Println("Usage: quiver-sleep [sleep|wake|status|monitor|history]")
		os.Exit(1)
	}

	command := os.Args[1]
	switch command {
	case "sleep":
		handleSleep()
	case "wake":
		handleWake()
	case "status":
		handleStatus()
	case "monitor":
		handleMonitor()
	case "history":
		handleHistory()
	default:
		fmt.Printf("Unknown command: %s\n", command)
		os.Exit(1)
	}
}

func handleSleep() {
	state := loadState()
	if state.Status == "sleeping" {
		fmt.Println("Already in pseudo-sleep state.")
		return
	}

	cfg := loadConfig()
	fmt.Println("Entering pseudo-sleep state...")

	state.Status = "sleeping"
	state.SleepStarted = time.Now()
	state.FrozenUnits = []string{}
	state.PausedContainers = []string{}

	// 1. Detect CPU governors
	govs, err := getCPUGovernors()
	if err != nil {
		log.Printf("Warning: failed to get CPU governors: %v", err)
	} else {
		state.SavedGovernors = govs
	}

	// 2. Find current systemd unit
	currentUnit, err := getCurrentUnit()
	if err != nil {
		log.Printf("Warning: failed to determine current systemd cgroup unit: %v", err)
	}

	// 3. List active systemd units to freeze
	units, err := getActiveUserUnits()
	if err != nil {
		log.Printf("Warning: failed to list user systemd units: %v", err)
	} else {
		for _, u := range units {
			// Skip current unit and whitelisted units
			if u == currentUnit {
				continue
			}
			isExcluded := false
			for _, excl := range cfg.ExcludeUnits {
				if u == excl {
					isExcluded = true
					break
				}
			}
			if isExcluded {
				continue
			}
			// Only freeze app scopes/services and tmux spans
			if strings.HasPrefix(u, "app-") || strings.HasPrefix(u, "tmux-spawn-") {
				state.FrozenUnits = append(state.FrozenUnits, u)
			}
		}
	}

	// 4. Pause Docker containers if configured
	if cfg.PauseDockerContainers {
		containers, err := getRunningContainers()
		if err != nil {
			log.Printf("Warning: failed to list docker containers: %v", err)
		} else {
			for _, c := range containers {
				isExcluded := false
				for _, excl := range cfg.ExcludeContainers {
					if c.Name == excl || c.ID == excl {
						isExcluded = true
						break
					}
				}
				if !isExcluded {
					state.PausedContainers = append(state.PausedContainers, c.ID)
				}
			}
		}
	}

	// Set Niri socket environment variable if not already set, in case we are on SSH
	setupNiriEnv()

	// 5. Execute actions
	// A. Set CPU scaling governor to powersave
	if err := setCPUGovernors("powersave"); err != nil {
		log.Printf("Warning: failed to set CPU governors to powersave: %v", err)
	} else {
		fmt.Println("✓ CPU scaling governor set to powersave.")
	}

	// B. Turn off monitors via Niri
	if err := powerOffMonitors(); err != nil {
		log.Printf("Warning: failed to power off monitors: %v", err)
	} else {
		fmt.Println("✓ Niri displays powered off.")
	}

	// C. Freeze Docker containers
	for _, cID := range state.PausedContainers {
		if err := pauseContainer(cID); err != nil {
			log.Printf("Warning: failed to pause docker container %s: %v", cID, err)
		}
	}
	if len(state.PausedContainers) > 0 {
		fmt.Printf("✓ Paused %d Docker containers.\n", len(state.PausedContainers))
	}

	// D. Freeze user systemd units
	frozenCount := 0
	for _, u := range state.FrozenUnits {
		if err := freezeUnit(u); err != nil {
			log.Printf("Warning: failed to freeze systemd unit %s: %v", u, err)
		} else {
			frozenCount++
		}
	}
	fmt.Printf("✓ Suspended %d user application cgroups.\n", frozenCount)

	// Save state
	if err := saveState(state); err != nil {
		log.Fatalf("Error saving state: %v", err)
	}

	// Start monitor service
	exec.Command("systemctl", "--user", "start", "quiver-sleep-monitor.service").Run()

	// Append sleep start history entry
	logHistory(HistoryEntry{
		Timestamp: time.Now(),
		Event:     "sleep_start",
	})

	fmt.Println("System is now in pseudo-sleep. Actively monitoring usage...")
}

func handleWake() {
	state := loadState()
	if state.Status != "sleeping" {
		fmt.Println("System is not currently in pseudo-sleep state.")
		return
	}

	fmt.Println("Waking up from pseudo-sleep...")

	// Stop monitor service
	exec.Command("systemctl", "--user", "stop", "quiver-sleep-monitor.service").Run()

	setupNiriEnv()

	// 1. Thaw systemd units
	thawedCount := 0
	for _, u := range state.FrozenUnits {
		if err := thawUnit(u); err != nil {
			log.Printf("Warning: failed to thaw systemd unit %s: %v", u, err)
		} else {
			thawedCount++
		}
	}
	fmt.Printf("✓ Resumed %d user application cgroups.\n", thawedCount)

	// 2. Unpause Docker containers
	for _, cID := range state.PausedContainers {
		if err := unpauseContainer(cID); err != nil {
			log.Printf("Warning: failed to unpause docker container %s: %v", cID, err)
		}
	}
	if len(state.PausedContainers) > 0 {
		fmt.Printf("✓ Resumed %d Docker containers.\n", len(state.PausedContainers))
	}

	// 3. Restore CPU governors
	if state.SavedGovernors != nil && len(state.SavedGovernors) > 0 {
		if err := restoreCPUGovernors(state.SavedGovernors); err != nil {
			log.Printf("Warning: failed to restore CPU governors: %v", err)
		} else {
			fmt.Println("✓ CPU scaling governors restored.")
		}
	} else {
		// Fallback to performance/schedutil
		setCPUGovernors("performance")
	}

	// 4. Power on monitors via Niri
	if err := powerOnMonitors(); err != nil {
		log.Printf("Warning: failed to power on monitors: %v", err)
	} else {
		fmt.Println("✓ Niri displays powered on.")
	}

	// Append wake history entry
	logHistory(HistoryEntry{
		Timestamp: time.Now(),
		Event:     "wake",
	})

	sleepDuration := time.Since(state.SleepStarted)

	state.Status = "awake"
	state.FrozenUnits = nil
	state.PausedContainers = nil
	state.SavedGovernors = nil
	saveState(state)

	fmt.Println("✓ System is fully awake.")
	fmt.Printf("\n--- Sleep Session Summary ---\n")
	fmt.Printf("Sleep duration: %s\n", formatDuration(sleepDuration))
	printSleepSummary(state.SleepStarted)
}

func handleStatus() {
	state := loadState()
	fmt.Printf("System Status: %s\n", strings.ToUpper(state.Status))
	if state.Status == "sleeping" {
		fmt.Printf("Asleep since:   %s (%s ago)\n", state.SleepStarted.Format(time.RFC1123), formatDuration(time.Since(state.SleepStarted)))
		fmt.Printf("Frozen Units:   %d\n", len(state.FrozenUnits))
		fmt.Printf("Paused Docker:  %d\n", len(state.PausedContainers))
		if len(state.SavedGovernors) > 0 {
			var govList []string
			for cpu, gov := range state.SavedGovernors {
				govList = append(govList, fmt.Sprintf("%s:%s", cpu, gov))
			}
			sort.Strings(govList)
			fmt.Printf("Saved Govs:     %s\n", strings.Join(govList, ", "))
		}
	}

	// Print current stats
	cpu, _ := getCPUUsageRaw()
	time.Sleep(200 * time.Millisecond)
	cpuVal, _ := getCPUUsage(cpu)
	temp, _ := getCPUTemp()
	memUsed, memTotal, _ := getMemoryStats()
	rx, tx, _ := getNetworkStats()

	fmt.Printf("\nCurrent Resource Stats:\n")
	fmt.Printf("  CPU Usage:    %.1f%%\n", cpuVal)
	fmt.Printf("  Temperature:  %.1f°C\n", temp)
	fmt.Printf("  Memory:       %.2f GB / %.2f GB\n", float64(memUsed)/(1024*1024*1024), float64(memTotal)/(1024*1024*1024))
	fmt.Printf("  Network Tot:  Rx: %s, Tx: %s\n", formatBytes(rx), formatBytes(tx))

	if state.Status == "sleeping" {
		fmt.Println("\nCurrently recording logs to system history. Use 'quiver-sleep wake' to resume normal state.")
	}
}

func handleMonitor() {
	cfg := loadConfig()
	interval := time.Duration(cfg.MonitorIntervalSeconds) * time.Second
	if interval < 5*time.Second {
		interval = 5 * time.Second
	}

	prevCPU, err := getCPUUsageRaw()
	if err != nil {
		log.Printf("Error getting initial CPU tick: %v", err)
	}

	// Track initial network bytes to report delta in periodic logs
	prevRx, prevTx, _ := getNetworkStats()

	for {
		time.Sleep(interval)

		currentCPU, err := getCPUUsageRaw()
		if err != nil {
			continue
		}
		cpuUsage := calculateCPUUsage(prevCPU, currentCPU)
		prevCPU = currentCPU

		temp, _ := getCPUTemp()
		memUsed, _, _ := getMemoryStats()
		rx, tx, _ := getNetworkStats()

		rxDelta := uint64(0)
		txDelta := uint64(0)
		if rx >= prevRx {
			rxDelta = rx - prevRx
		}
		if tx >= prevTx {
			txDelta = tx - prevTx
		}
		prevRx = rx
		prevTx = tx

		topProcs, _ := getTopProcesses(3)

		logHistory(HistoryEntry{
			Timestamp:    time.Now(),
			CPUUsagePct:  cpuUsage,
			MemoryUsedGB: float64(memUsed) / (1024 * 1024 * 1024),
			CPUTempC:     temp,
			RxBytes:      rxDelta,
			TxBytes:      txDelta,
			TopProcesses: topProcs,
		})
	}
}

func handleHistory() {
	histPath := getHistoryPath()
	file, err := os.Open(histPath)
	if err != nil {
		fmt.Printf("No history found at %s\n", histPath)
		return
	}
	defer file.Close()

	dec := json.NewDecoder(file)
	var entries []HistoryEntry
	for {
		var entry HistoryEntry
		if err := dec.Decode(&entry); err == io.EOF {
			break
		} else if err != nil {
			continue
		}
		entries = append(entries, entry)
	}

	if len(entries) == 0 {
		fmt.Println("No sleep history entries recorded.")
		return
	}

	fmt.Println("Recent sleep history sessions:")
	fmt.Printf("%-25s %-25s %-12s %-12s\n", "Started", "Ended", "Duration", "Avg CPU (Max)")
	var start time.Time
	var periodCPU []float64
	for _, entry := range entries {
		if entry.Event == "sleep_start" {
			start = entry.Timestamp
			periodCPU = []float64{}
		} else if entry.Event == "wake" && !start.IsZero() {
			end := entry.Timestamp
			dur := end.Sub(start)
			avgCPU := 0.0
			maxCPU := 0.0
			if len(periodCPU) > 0 {
				sum := 0.0
				for _, c := range periodCPU {
					sum += c
					if c > maxCPU {
						maxCPU = c
					}
				}
				avgCPU = sum / float64(len(periodCPU))
			}
			fmt.Printf("%-25s %-25s %-12s %.1f%% (%.1f%%)\n",
				start.Format("2006-01-02 15:04:02"),
				end.Format("2006-01-02 15:04:02"),
				dur.Round(time.Second),
				avgCPU,
				maxCPU,
			)
			start = time.Time{}
		} else if !start.IsZero() {
			periodCPU = append(periodCPU, entry.CPUUsagePct)
		}
	}
}

// Helpers

func logHistory(entry HistoryEntry) {
	histPath := getHistoryPath()
	os.MkdirAll(filepath.Dir(histPath), 0755)
	file, err := os.OpenFile(histPath, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0644)
	if err != nil {
		return
	}
	defer file.Close()

	data, err := json.Marshal(entry)
	if err == nil {
		file.Write(data)
		file.WriteString("\n")
	}
}

func printSleepSummary(sleepStart time.Time) {
	histPath := getHistoryPath()
	file, err := os.Open(histPath)
	if err != nil {
		return
	}
	defer file.Close()

	dec := json.NewDecoder(file)
	var sessionEntries []HistoryEntry
	inSession := false
	for {
		var entry HistoryEntry
		if err := dec.Decode(&entry); err == io.EOF {
			break
		} else if err != nil {
			continue
		}

		if entry.Event == "sleep_start" && (entry.Timestamp.Equal(sleepStart) || entry.Timestamp.After(sleepStart.Add(-2*time.Second))) {
			inSession = true
			sessionEntries = append(sessionEntries, entry)
		} else if inSession {
			sessionEntries = append(sessionEntries, entry)
			if entry.Event == "wake" {
				break
			}
		}
	}

	if len(sessionEntries) <= 2 {
		fmt.Println("Not enough log data recorded during sleep session to construct resource graphs.")
		return
	}

	var cpuVals, tempVals, memVals []float64
	var totalRx, totalTx uint64
	procCPUCount := make(map[string]float64)
	procTicks := make(map[string]int)

	for _, e := range sessionEntries {
		if e.Event != "" {
			continue
		}
		cpuVals = append(cpuVals, e.CPUUsagePct)
		tempVals = append(tempVals, e.CPUTempC)
		memVals = append(memVals, e.MemoryUsedGB)
		totalRx += e.RxBytes
		totalTx += e.TxBytes

		for _, p := range e.TopProcesses {
			procCPUCount[p.Name] += p.CPU
			procTicks[p.Name]++
		}
	}

	avgCPU, maxCPU := statsSummary(cpuVals)
	avgTemp, maxTemp := statsSummary(tempVals)
	avgMem, maxMem := statsSummary(memVals)

	fmt.Printf("Average CPU Usage:   %.1f%%  (Peak: %.1f%%)\n", avgCPU, maxCPU)
	fmt.Printf("Average Temp:        %.1f°C (Peak: %.1f°C)\n", avgTemp, maxTemp)
	fmt.Printf("Average Memory Used: %.2f GB (Peak: %.2f GB)\n", avgMem, maxMem)
	fmt.Printf("Total Network:       Rx: %s, Tx: %s\n", formatBytes(totalRx), formatBytes(totalTx))

	// Print top active processes during sleep
	type ProcScore struct {
		Name   string
		AvgCPU float64
	}
	var scores []ProcScore
	for name, sumCPU := range procCPUCount {
		ticks := procTicks[name]
		if ticks > 0 {
			scores = append(scores, ProcScore{Name: name, AvgCPU: sumCPU / float64(len(cpuVals))})
		}
	}
	sort.Slice(scores, func(i, j int) bool {
		return scores[i].AvgCPU > scores[j].AvgCPU
	})

	if len(scores) > 0 {
		fmt.Printf("\nTop active processes during sleep:\n")
		limit := 5
		if len(scores) < limit {
			limit = len(scores)
		}
		for i := 0; i < limit; i++ {
			if scores[i].AvgCPU > 0.05 {
				fmt.Printf("  %-20s average %.2f%% CPU\n", scores[i].Name, scores[i].AvgCPU)
			}
		}
	}
}

func statsSummary(vals []float64) (avg, max float64) {
	if len(vals) == 0 {
		return 0, 0
	}
	sum := 0.0
	for _, v := range vals {
		sum += v
		if v > max {
			max = v
		}
	}
	return sum / float64(len(vals)), max
}

func formatBytes(bytes uint64) string {
	const unit = 1024
	if bytes < unit {
		return fmt.Sprintf("%d B", bytes)
	}
	div, exp := uint64(unit), 0
	for n := bytes / unit; n >= unit; n /= unit {
		div *= unit
		exp++
	}
	return fmt.Sprintf("%.2f %cB", float64(bytes)/float64(div), "KMGTPE"[exp])
}

func formatDuration(d time.Duration) string {
	h := d / time.Hour
	d -= h * time.Hour
	m := d / time.Minute
	d -= m * time.Minute
	s := d / time.Second
	if h > 0 {
		return fmt.Sprintf("%dh %dm %ds", h, m, s)
	}
	if m > 0 {
		return fmt.Sprintf("%dm %ds", m, s)
	}
	return fmt.Sprintf("%ds", s)
}

// System interface wrappers

func getCPUGovernors() (map[string]string, error) {
	governors := make(map[string]string)
	files, err := filepath.Glob("/sys/devices/system/cpu/cpu[0-9]*/cpufreq/scaling_governor")
	if err != nil {
		return nil, err
	}
	for _, f := range files {
		content, err := os.ReadFile(f)
		if err != nil {
			continue
		}
		cpuName := filepath.Base(filepath.Dir(filepath.Dir(f)))
		governors[cpuName] = strings.TrimSpace(string(content))
	}
	return governors, nil
}

func setCPUGovernors(governor string) error {
	cmd := exec.Command("sudo", "sh", "-c", fmt.Sprintf("echo %s | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor", governor))
	cmd.Stdout = io.Discard
	cmd.Stderr = io.Discard
	return cmd.Run()
}

func restoreCPUGovernors(saved map[string]string) error {
	for cpu, gov := range saved {
		// Basic sanitization
		if !strings.HasPrefix(cpu, "cpu") || (gov != "powersave" && gov != "performance" && gov != "schedutil" && gov != "ondemand") {
			continue
		}
		path := fmt.Sprintf("/sys/devices/system/cpu/%s/cpufreq/scaling_governor", cpu)
		cmd := exec.Command("sudo", "sh", "-c", fmt.Sprintf("echo %s > %s", gov, path))
		cmd.Run()
	}
	return nil
}

func getCurrentUnit() (string, error) {
	content, err := os.ReadFile("/proc/self/cgroup")
	if err != nil {
		return "", err
	}
	lines := strings.Split(string(content), "\n")
	for _, line := range lines {
		parts := strings.Split(line, ":")
		if len(parts) >= 3 && parts[2] != "" {
			subpath := parts[2]
			segments := strings.Split(subpath, "/")
			for i := len(segments) - 1; i >= 0; i-- {
				seg := segments[i]
				if strings.HasSuffix(seg, ".scope") || strings.HasSuffix(seg, ".service") {
					// URL-decode backslashes systemd uses (like \x2d for -)
					seg = strings.ReplaceAll(seg, "\\x2d", "-")
					return seg, nil
				}
			}
		}
	}
	return "", fmt.Errorf("cgroup unit not found in /proc/self/cgroup")
}

func getActiveUserUnits() ([]string, error) {
	cmd := exec.Command("systemctl", "--user", "list-units", "--type=scope", "--type=service", "--state=running", "--no-legend", "--plain")
	out, err := cmd.Output()
	if err != nil {
		return nil, err
	}
	lines := strings.Split(string(out), "\n")
	var units []string
	for _, line := range lines {
		fields := strings.Fields(line)
		if len(fields) > 0 {
			unit := fields[0]
			// systemctl list-units encodes backslashes as \x2d sometimes, let's decode
			unit = strings.ReplaceAll(unit, "\\x2d", "-")
			unit = strings.ReplaceAll(unit, "\\x5c", "\\")
			units = append(units, unit)
		}
	}
	return units, nil
}

func freezeUnit(unit string) error {
	cmd := exec.Command("systemctl", "--user", "freeze", unit)
	return cmd.Run()
}

func thawUnit(unit string) error {
	cmd := exec.Command("systemctl", "--user", "thaw", unit)
	return cmd.Run()
}

type ContainerInfo struct {
	ID   string
	Name string
}

func getRunningContainers() ([]ContainerInfo, error) {
	cmd := exec.Command("docker", "ps", "--format", "{{.ID}} {{.Names}}")
	out, err := cmd.Output()
	if err != nil {
		return nil, err
	}
	lines := strings.Split(strings.TrimSpace(string(out)), "\n")
	var list []ContainerInfo
	for _, line := range lines {
		fields := strings.Fields(line)
		if len(fields) >= 2 {
			list = append(list, ContainerInfo{ID: fields[0], Name: fields[1]})
		}
	}
	return list, nil
}

func pauseContainer(cID string) error {
	cmd := exec.Command("docker", "pause", cID)
	return cmd.Run()
}

func unpauseContainer(cID string) error {
	cmd := exec.Command("docker", "unpause", cID)
	return cmd.Run()
}

func setupNiriEnv() {
	if os.Getenv("NIRI_SOCKET") != "" {
		return
	}
	// Try to find the Niri socket in /run/user/1000/
	files, err := filepath.Glob("/run/user/1000/niri.wayland-*.sock")
	if err == nil && len(files) > 0 {
		os.Setenv("NIRI_SOCKET", files[0])
	}
}

func powerOffMonitors() error {
	cmd := exec.Command("niri", "msg", "action", "power-off-monitors")
	return cmd.Run()
}

func powerOnMonitors() error {
	cmd := exec.Command("niri", "msg", "action", "power-on-monitors")
	return cmd.Run()
}

func getCPUTemp() (float64, error) {
	files, err := filepath.Glob("/sys/class/hwmon/hwmon*/name")
	if err != nil {
		return 0, err
	}
	for _, f := range files {
		content, err := os.ReadFile(f)
		if err != nil {
			continue
		}
		if strings.TrimSpace(string(content)) == "k10temp" {
			dir := filepath.Dir(f)
			tempFile := filepath.Join(dir, "temp1_input")
			tempContent, err := os.ReadFile(tempFile)
			if err == nil {
				var mCels int
				fmt.Sscanf(string(tempContent), "%d", &mCels)
				return float64(mCels) / 1000.0, nil
			}
		}
	}
	// Fallback to acpitz thermal zone
	tempFile := "/sys/class/thermal/thermal_zone0/temp"
	tempContent, err := os.ReadFile(tempFile)
	if err == nil {
		var mCels int
		fmt.Sscanf(string(tempContent), "%d", &mCels)
		return float64(mCels) / 1000.0, nil
	}
	return 0, fmt.Errorf("temperature sensor not found")
}

func getMemoryStats() (used, total uint64, err error) {
	content, err := os.ReadFile("/proc/meminfo")
	if err != nil {
		return 0, 0, err
	}
	lines := strings.Split(string(content), "\n")
	var memTotal, memAvailable uint64
	for _, line := range lines {
		fields := strings.Fields(line)
		if len(fields) >= 2 {
			name := strings.TrimSuffix(fields[0], ":")
			var val uint64
			fmt.Sscanf(fields[1], "%d", &val)
			if name == "MemTotal" {
				memTotal = val * 1024
			} else if name == "MemAvailable" {
				memAvailable = val * 1024
			}
		}
	}
	if memTotal == 0 {
		return 0, 0, fmt.Errorf("could not parse MemTotal")
	}
	return memTotal - memAvailable, memTotal, nil
}

func getNetworkStats() (rx, tx uint64, err error) {
	content, err := os.ReadFile("/proc/net/dev")
	if err != nil {
		return 0, 0, err
	}
	lines := strings.Split(string(content), "\n")
	for i, line := range lines {
		if i < 2 {
			continue
		}
		parts := strings.Split(line, ":")
		if len(parts) < 2 {
			continue
		}
		iface := strings.TrimSpace(parts[0])
		if iface == "lo" || strings.HasPrefix(iface, "veth") || strings.HasPrefix(iface, "br-") || strings.HasPrefix(iface, "docker") {
			continue
		}
		fields := strings.Fields(parts[1])
		if len(fields) >= 9 {
			var r, t uint64
			fmt.Sscanf(fields[0], "%d", &r)
			fmt.Sscanf(fields[8], "%d", &t)
			rx += r
			tx += t
		}
	}
	return rx, tx, nil
}

func getTopProcesses(n int) ([]ProcessStat, error) {
	cmd := exec.Command("ps", "-eo", "pid,%cpu,comm", "--sort=-%cpu", "--no-headers")
	out, err := cmd.Output()
	if err != nil {
		return nil, err
	}
	lines := strings.Split(string(out), "\n")
	var stats []ProcessStat
	for _, line := range lines {
		fields := strings.Fields(line)
		if len(fields) >= 3 {
			var pid int
			var cpu float64
			fmt.Sscanf(fields[0], "%d", &pid)
			fmt.Sscanf(fields[1], "%f", &cpu)
			name := fields[2]
			if cpu > 0.1 && pid != os.Getpid() {
				stats = append(stats, ProcessStat{PID: pid, CPU: cpu, Name: name})
				if len(stats) >= n {
					break
				}
			}
		}
	}
	return stats, nil
}

func getCPUUsageRaw() (CPUTick, error) {
	content, err := os.ReadFile("/proc/stat")
	if err != nil {
		return CPUTick{}, err
	}
	lines := strings.Split(string(content), "\n")
	if len(lines) == 0 {
		return CPUTick{}, fmt.Errorf("empty /proc/stat")
	}
	fields := strings.Fields(lines[0])
	if len(fields) < 9 || fields[0] != "cpu" {
		return CPUTick{}, fmt.Errorf("unexpected /proc/stat cpu format")
	}
	var t CPUTick
	fmt.Sscanf(fields[1], "%d", &t.User)
	fmt.Sscanf(fields[2], "%d", &t.Nice)
	fmt.Sscanf(fields[3], "%d", &t.System)
	fmt.Sscanf(fields[4], "%d", &t.Idle)
	fmt.Sscanf(fields[5], "%d", &t.Iowait)
	fmt.Sscanf(fields[6], "%d", &t.Irq)
	fmt.Sscanf(fields[7], "%d", &t.Softirq)
	fmt.Sscanf(fields[8], "%d", &t.Steal)
	return t, nil
}

func getCPUUsage(prev CPUTick) (float64, error) {
	current, err := getCPUUsageRaw()
	if err != nil {
		return 0, err
	}
	return calculateCPUUsage(prev, current), nil
}

func calculateCPUUsage(prev, current CPUTick) float64 {
	prevIdle := prev.Idle + prev.Iowait
	currentIdle := current.Idle + current.Iowait

	prevNonIdle := prev.User + prev.Nice + prev.System + prev.Irq + prev.Softirq + prev.Steal
	currentNonIdle := current.User + current.Nice + current.System + current.Irq + current.Softirq + current.Steal

	prevTotal := prevIdle + prevNonIdle
	currentTotal := currentIdle + currentNonIdle

	totalDiff := currentTotal - prevTotal
	idleDiff := currentIdle - prevIdle

	if totalDiff == 0 {
		return 0.0
	}
	return 100.0 * (1.0 - float64(idleDiff)/float64(totalDiff))
}

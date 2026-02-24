package manager

import (
	"bufio"
	"context"
	"fmt"
	"io"
	"log"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"sync"

	"github.com/chrisesplin/quiver-hq/internal/db"
)

type MissionControl struct {
	ID         string
	Command    *exec.Cmd
	CancelFunc context.CancelFunc
	Stdin      io.WriteCloser
}

type Manager struct {
	db               *db.DB
	missions         map[string]*MissionControl
	approvals        map[string]chan bool // missionID -> approval channel
	mu               sync.RWMutex
	LogObserver      func(missionID, text string)
	ApprovalObserver func(missionID, prompt string)
	RootDir          string
}

func NewManager(database *db.DB, rootDir string) *Manager {
	return &Manager{
		db:        database,
		missions:  make(map[string]*MissionControl),
		approvals: make(map[string]chan bool),
		RootDir:   rootDir,
	}
}

func (m *Manager) RequestApproval(missionID, prompt string) bool {
	ch := make(chan bool)
	m.mu.Lock()
	m.approvals[missionID] = ch
	m.mu.Unlock()

	if m.ApprovalObserver != nil {
		m.ApprovalObserver(missionID, prompt)
	}

	result := <-ch

	m.mu.Lock()
	delete(m.approvals, missionID)
	m.mu.Unlock()

	return result
}

func (m *Manager) ResolveApproval(missionID string, approved bool) {
	m.mu.RLock()
	ch, ok := m.approvals[missionID]
	m.mu.RUnlock()

	if ok {
		ch <- approved
	}
}

func (m *Manager) PrepareWorkspace(projectPath string) error {
	// Check for .env.tmpl
	tmplPath := filepath.Join(projectPath, ".env.tmpl")
	if _, err := os.Stat(tmplPath); os.IsNotExist(err) {
		return nil // No template, nothing to hydrate
	}

	log.Printf("Hydrating workspace at %s...", projectPath)
	// Execute quiver-secrets hydrate
	// We assume quiver-secrets is in the root or in the PATH
	execPath := filepath.Join(m.RootDir, "quiver-secrets")
	cmd := exec.Command(execPath, "hydrate", projectPath)
	
	// Ensure op session is available if possible, or assume it's already in env
	output, err := cmd.CombinedOutput()
	if err != nil {
		return fmt.Errorf("hydration failed: %v\nOutput: %s", err, string(output))
	}

	return nil
}

func (m *Manager) StartMission(ctx context.Context, id, projectDir, commandStr string, args ...string) error {
	m.mu.Lock()
	if _, exists := m.missions[id]; exists {
		m.mu.Unlock()
		return fmt.Errorf("mission %s is already running", id)
	}
	m.mu.Unlock()

	// 1. Prepare Workspace (Hydrate secrets)
	if err := m.PrepareWorkspace(projectDir); err != nil {
		return fmt.Errorf("failed to prepare workspace: %v", err)
	}

	missionCtx, cancel := context.WithCancel(ctx)
	cmd := exec.CommandContext(missionCtx, commandStr, args...)
	cmd.Dir = projectDir

	stdout, _ := cmd.StdoutPipe()
	stderr, _ := cmd.StderrPipe()
	stdin, _ := cmd.StdinPipe()

	if err := cmd.Start(); err != nil {
		cancel()
		return err
	}

	mc := &MissionControl{
		ID:         id,
		Command:    cmd,
		CancelFunc: cancel,
		Stdin:      stdin,
	}
	
	m.mu.Lock()
	m.missions[id] = mc
	m.mu.Unlock()

	// Log mission start
	m.db.CreateMission(ctx, id, "running", fmt.Sprintf("Command: %s %v", commandStr, args))

	// Stream output to logs in background
	go m.streamOutput(id, io.MultiReader(stdout, stderr))

	// Wait for completion in background
	go func() {
		err := cmd.Wait()
		m.mu.Lock()
		delete(m.missions, id)
		m.mu.Unlock()

		status := "completed"
		if err != nil {
			status = "failed"
			m.db.LogMission(context.Background(), id, "Process exited with error", err.Error())
		}

		// Notify observer of completion
		if m.LogObserver != nil {
			m.LogObserver(id, fmt.Sprintf("🏁 Mission %s finished with status: %s", id, status))
		}
		log.Printf("Mission %s finished with status: %s", id, status)
	}()

	return nil
}

func (m *Manager) WriteToMission(id, text string) error {
	m.mu.RLock()
	mc, ok := m.missions[id]
	m.mu.RUnlock()

	if !ok {
		return fmt.Errorf("mission %s not found", id)
	}

	_, err := fmt.Fprintln(mc.Stdin, text)
	return err
}

func (m *Manager) StopMission(id string) error {
	m.mu.Lock()
	defer m.mu.Unlock()

	mc, ok := m.missions[id]
	if !ok {
		return fmt.Errorf("mission %s not found", id)
	}

	mc.CancelFunc()
	return nil
}

func (m *Manager) streamOutput(id string, r io.Reader) {
	scanner := bufio.NewScanner(r)
	for scanner.Scan() {
		text := scanner.Text()

		if strings.HasPrefix(text, "QUIVER_SIGNAL:REQUEST_APPROVAL") {
			prompt := strings.TrimPrefix(text, "QUIVER_SIGNAL:REQUEST_APPROVAL ")
			if prompt == text {
				prompt = "The agent is requesting approval for a risky action."
			}
			
			// Start approval flow in a goroutine to avoid blocking the scanner
			go func(p string) {
				approved := m.RequestApproval(id, p)
				response := "DENIED"
				if approved {
					response = "APPROVED"
				}
				m.WriteToMission(id, response)
			}(prompt)
			continue
		}

		// Log to DB: text is the entry, "stdout" is the metadata
		err := m.db.LogMission(context.Background(), id, text, "stdout")
		if err != nil {
			log.Printf("Failed to log output for mission %s: %v", id, err)
		}

		// Notify observer
		if m.LogObserver != nil {
			m.LogObserver(id, text)
		}
	}
}

func (m *Manager) ListActiveMissions() []string {
	m.mu.RLock()
	defer m.mu.RUnlock()

	var list []string
	for id := range m.missions {
		list = append(list, id)
	}
	return list
}

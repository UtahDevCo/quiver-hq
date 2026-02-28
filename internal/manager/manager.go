package manager

import (
	"bufio"
	"bytes"
	"context"
	"fmt"
	"io"
	"log"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"strings"
	"sync"

	"github.com/chrisesplin/quiver-hq/internal/db"
	"github.com/creack/pty"
)

type MissionControl struct {
	ID         string
	Command    *exec.Cmd
	CancelFunc context.CancelFunc
	Pty        *os.File
}

type Manager struct {
	db               *db.DB
	missions         map[string]*MissionControl
	missionProjects  map[string]string    // missionID -> projectDir (persists after exit)
	approvals        map[string]chan bool // missionID -> approval channel
	mu               sync.RWMutex
	LogObserver      func(missionID, text string)
	ApprovalObserver func(missionID, prompt string)
	RootDir          string
}

func NewManager(database *db.DB, rootDir string) *Manager {
	return &Manager{
		db:              database,
		missions:        make(map[string]*MissionControl),
		missionProjects: make(map[string]string),
		approvals:       make(map[string]chan bool),
		RootDir:         rootDir,
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
	tmplPath := filepath.Join(projectPath, ".env.tmpl")
	if _, err := os.Stat(tmplPath); os.IsNotExist(err) {
		return nil
	}

	log.Printf("Hydrating workspace at %s...", projectPath)
	execPath := filepath.Join(m.RootDir, "quiver-secrets")
	cmd := exec.Command(execPath, "hydrate", projectPath)
	
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
	m.missionProjects[id] = projectDir
	m.mu.Unlock()

	if err := m.PrepareWorkspace(projectDir); err != nil {
		return fmt.Errorf("failed to prepare workspace: %v", err)
	}

	return m.runProcess(ctx, id, projectDir, commandStr, args...)
}

func (m *Manager) runProcess(ctx context.Context, id, projectDir, commandStr string, args ...string) error {
	missionCtx, cancel := context.WithCancel(ctx)
	cmd := exec.CommandContext(missionCtx, commandStr, args...)
	cmd.Dir = projectDir
	
	homeDir, _ := os.UserHomeDir()
	cmd.Env = os.Environ()
	cmd.Env = append(cmd.Env, "TERM=xterm-256color")
	cmd.Env = append(cmd.Env, "NO_COLOR=1")
	cmd.Env = append(cmd.Env, fmt.Sprintf("GEMINI_CLI_HOME=%s", homeDir))
	cmd.Env = append(cmd.Env, fmt.Sprintf("HOME=%s", homeDir))

	log.Printf("Spawning mission %s: %s %v", id, commandStr, args)

	f, err := pty.Start(cmd)
	if err != nil {
		cancel()
		return err
	}

	_ = pty.Setsize(f, &pty.Winsize{Rows: 24, Cols: 80})

	mc := &MissionControl{
		ID:         id,
		Command:    cmd,
		CancelFunc: cancel,
		Pty:        f,
	}
	
	m.mu.Lock()
	m.missions[id] = mc
	m.mu.Unlock()

	m.db.CreateMission(ctx, id, "running", fmt.Sprintf("Command: %s %v", commandStr, args))

	go m.streamOutput(id, f)

	go func() {
		defer f.Close()
		err := cmd.Wait()
		
		m.mu.Lock()
		delete(m.missions, id)
		m.mu.Unlock()

		if err != nil {
			m.db.LogMission(context.Background(), id, "Process exited with error", err.Error())
		}

		if m.LogObserver != nil {
			msg := fmt.Sprintf("🏁 Mission %s turn finished", id)
			if err != nil {
				msg += fmt.Sprintf(" (Error: %v)", err)
			}
			m.LogObserver(id, msg)
		}
	}()

	return nil
}

func (m *Manager) WriteToMission(id, text string) error {
	m.mu.RLock()
	mc, running := m.missions[id]
	projectDir := m.missionProjects[id]
	m.mu.RUnlock()

	if running {
		// Mission is already active (like bash), write to stdin
		_, err := fmt.Fprintln(mc.Pty, text)
		return err
	}

	if projectDir == "" {
		return fmt.Errorf("mission %s not found and has no project directory", id)
	}

	// Stateless resumption: spawn a new gemini command
	log.Printf("Resuming mission %s in %s", id, projectDir)
	return m.runProcess(context.Background(), id, projectDir, "gemini", "--output-format", "text", "--resume", "latest", "--prompt", text)
}

func (m *Manager) StopMission(id string) error {
	m.mu.Lock()
	defer m.mu.Unlock()

	mc, ok := m.missions[id]
	if !ok {
		return fmt.Errorf("mission %s not found", id)
	}

	mc.CancelFunc()
	mc.Pty.Close()
	return nil
}

func (m *Manager) streamOutput(id string, r io.Reader) {
	scanner := bufio.NewScanner(r)
	
	scanner.Split(func(data []byte, atEOF bool) (advance int, token []byte, err error) {
		if atEOF && len(data) == 0 {
			return 0, nil, nil
		}
		if i := bytes.IndexAny(data, "\n\r"); i >= 0 {
			return i + 1, data[0:i], nil
		}
		if atEOF {
			return len(data), data, nil
		}
		return 0, nil, nil
	})

	var lastText string
	for scanner.Scan() {
		rawText := scanner.Text()
		text := strings.TrimSpace(m.StripANSI(rawText))
		
		if text == "" || text == lastText {
			continue
		}
		lastText = text

		if strings.HasPrefix(text, "QUIVER_SIGNAL:REQUEST_APPROVAL") {
			prompt := strings.TrimPrefix(text, "QUIVER_SIGNAL:REQUEST_APPROVAL ")
			if prompt == text {
				prompt = "The agent is requesting approval for a risky action."
			}
			
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

		_ = m.db.LogMission(context.Background(), id, text, "stdout")
		if m.LogObserver != nil {
			m.LogObserver(id, text)
		}
	}
}

var ansiRegex = regexp.MustCompile("[\u001B\u009B][[\\]()#;?]*(?:(?:(?:[a-zA-Z\\d]*(?:;[-a-zA-Z\\d\\/#&.:=?%@~]*)*)?\u0007)|(?:(?:\\d{1,4}(?:;\\d{0,4})*)?[\\dA-PR-TZcf-ntqry=><~]))")

func (m *Manager) StripANSI(str string) string {
	clean := ansiRegex.ReplaceAllString(str, "")
	var sb strings.Builder
	for _, r := range clean {
		if r >= 32 || r == '\n' || r == '\r' || r == '\t' {
			sb.WriteRune(r)
		}
	}
	return sb.String()
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

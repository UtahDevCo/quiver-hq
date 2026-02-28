package discord

import (
	"context"
	"fmt"
	"log"
	"math/rand"
	"strings"
	"sync"
	"time"

	"github.com/bwmarrin/discordgo"
	"github.com/chrisesplin/quiver-hq/internal/db"
	"github.com/chrisesplin/quiver-hq/internal/manager"
	"github.com/chrisesplin/quiver-hq/internal/projects"
)

var (
	adjectives = []string{"friendly", "angry", "brave", "sleepy", "happy", "grumpy", "clever", "silent", "funky", "bold"}
	nouns      = []string{"muffin", "cheesecurd", "burrito", "walrus", "otter", "badger", "rocket", "wizard", "ninja", "panda"}
)

type Bot struct {
	Session        *discordgo.Session
	Manager        *manager.Manager
	Scanner        *projects.Scanner
	DB             *db.DB
	MissionThreads map[string]string // missionID -> threadID
	mu             sync.Mutex
}

func NewBot(token string, mgr *manager.Manager, scanner *projects.Scanner, database *db.DB) (*Bot, error) {
	dg, err := discordgo.New("Bot " + token)
	if err != nil {
		return nil, fmt.Errorf("error creating Discord session: %v", err)
	}

	bot := &Bot{
		Session:        dg,
		Manager:        mgr,
		Scanner:        scanner,
		DB:             database,
		MissionThreads: make(map[string]string),
	}

	mgr.LogObserver = bot.onLog
	mgr.ApprovalObserver = bot.onApprovalRequest

	dg.AddHandler(bot.onInteractionCreate)
	dg.AddHandler(bot.messageCreate)
	dg.Identify.Intents = discordgo.IntentsGuildMessages | discordgo.IntentsMessageContent

	err = dg.Open()
	if err != nil {
		return nil, fmt.Errorf("error opening connection: %v", err)
	}

	// Register Slash Commands
	commands := []*discordgo.ApplicationCommand{
		{
			Name:        "ping",
			Description: "Check if Quiver HQ is online",
		},
		{
			Name:        "project",
			Description: "Bind projects to channels",
			Options: []*discordgo.ApplicationCommandOption{
				{
					Type:        discordgo.ApplicationCommandOptionSubCommand,
					Name:        "attach",
					Description: "Attach a project to this channel",
					Options: []*discordgo.ApplicationCommandOption{
						{
							Type:         discordgo.ApplicationCommandOptionString,
							Name:         "name",
							Description:  "Project name",
							Required:     true,
							Autocomplete: true,
						},
					},
				},
				{
					Type:        discordgo.ApplicationCommandOptionSubCommand,
					Name:        "release",
					Description: "Release the project from this channel",
				},
			},
		},
		{
			Name:        "mission",
			Description: "Manage missions in the attached project",
			Options: []*discordgo.ApplicationCommandOption{
				{
					Type:        discordgo.ApplicationCommandOptionString,
					Name:        "prompt",
					Description: "Start a gemini mission with an optional prompt",
					Required:    false,
				},
				{
					Type:        discordgo.ApplicationCommandOptionString,
					Name:        "raw",
					Description: "Run a raw shell command (e.g. 'bash', 'ls -la')",
					Required:    false,
				},
				{
					Type:        discordgo.ApplicationCommandOptionString,
					Name:        "stop",
					Description: "Stop a running mission in this channel",
					Required:    false,
				},
			},
		},
		{
			Name:        "mission-debug",
			Description: "Debug the mission environment (runs tty and env)",
		},
	}

	for _, v := range commands {
		_, err := dg.ApplicationCommandCreate(dg.State.User.ID, "", v)
		if err != nil {
			log.Printf("Cannot create '%v' command: %v", v.Name, err)
		}
	}

	log.Println("Discord bot is now running with Enhanced Commands.")
	return bot, nil
}

func (b *Bot) generateFunkyID() string {
	r := rand.New(rand.NewSource(time.Now().UnixNano()))
	adj := adjectives[r.Intn(len(adjectives))]
	noun := nouns[r.Intn(len(nouns))]
	return fmt.Sprintf("%s-%s", adj, noun)
}

func (b *Bot) onInteractionCreate(s *discordgo.Session, i *discordgo.InteractionCreate) {
	switch i.Type {
	case discordgo.InteractionApplicationCommand:
		b.handleSlashCommand(s, i)
	case discordgo.InteractionApplicationCommandAutocomplete:
		b.handleAutocomplete(s, i)
	case discordgo.InteractionMessageComponent:
		b.handleComponentInteraction(s, i)
	}
}

func (b *Bot) handleComponentInteraction(s *discordgo.Session, i *discordgo.InteractionCreate) {
	customID := i.MessageComponentData().CustomID
	parts := strings.Split(customID, "_")
	if len(parts) < 3 || parts[0] != "approval" {
		return
	}

	action := parts[1]
	missionID := parts[2]
	approved := action == "approve"

	b.Manager.ResolveApproval(missionID, approved)

	content := "✅ Action Approved"
	if !approved {
		content = "❌ Action Denied"
	}

	s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
		Type: discordgo.InteractionResponseUpdateMessage,
		Data: &discordgo.InteractionResponseData{
			Content:    content,
			Components: []discordgo.MessageComponent{},
		},
	})
}

func (b *Bot) onApprovalRequest(missionID, prompt string) {
	b.mu.Lock()
	threadID, ok := b.MissionThreads[missionID]
	b.mu.Unlock()

	if !ok {
		return
	}

	_, err := b.Session.ChannelMessageSendComplex(threadID, &discordgo.MessageSend{
		Content: fmt.Sprintf("🛡️ **Approval Required**\n%s", prompt),
		Components: []discordgo.MessageComponent{
			discordgo.ActionsRow{
				Components: []discordgo.MessageComponent{
					discordgo.Button{
						Label:    "Approve",
						Style:    discordgo.SuccessButton,
						CustomID: fmt.Sprintf("approval_approve_%s", missionID),
					},
					discordgo.Button{
						Label:    "Deny",
						Style:    discordgo.DangerButton,
						CustomID: fmt.Sprintf("approval_deny_%s", missionID),
					},
				},
			},
		},
	})
	if err != nil {
		log.Printf("Failed to send approval request to Discord: %v", err)
	}
}

func (b *Bot) handleAutocomplete(s *discordgo.Session, i *discordgo.InteractionCreate) {
	data := i.ApplicationCommandData()
	var choices []*discordgo.ApplicationCommandOptionChoice

	if data.Name == "project" {
		options := data.Options[0]
		if options.Name == "attach" {
			for _, opt := range options.Options {
				if opt.Name == "name" && opt.Focused {
					projects, _ := b.Scanner.ListSubmodules()
					for name := range projects {
						if strings.HasPrefix(strings.ToLower(name), strings.ToLower(opt.StringValue())) {
							choices = append(choices, &discordgo.ApplicationCommandOptionChoice{
								Name:  name,
								Value: name,
							})
						}
					}
				}
			}
		}
	}

	s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
		Type: discordgo.InteractionApplicationCommandAutocompleteResult,
		Data: &discordgo.InteractionResponseData{
			Choices: choices,
		},
	})
}

func (b *Bot) handleSlashCommand(s *discordgo.Session, i *discordgo.InteractionCreate) {
	data := i.ApplicationCommandData()

	switch data.Name {
	case "ping":
		s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
			Type: discordgo.InteractionResponseChannelMessageWithSource,
			Data: &discordgo.InteractionResponseData{
				Content: "Pong! Quiver HQ is online.",
			},
		})
	case "project":
		b.handleProjectSlash(s, i)
	case "mission":
		b.handleMissionSlash(s, i)
	case "mission-debug":
		b.handleMissionDebug(s, i)
	}
}

func (b *Bot) handleProjectSlash(s *discordgo.Session, i *discordgo.InteractionCreate) {
	options := i.ApplicationCommandData().Options[0]
	ctx := context.Background()

	switch options.Name {
	case "attach":
		projectName := options.Options[0].StringValue()
		projectPath, err := b.Scanner.GetProjectPath(projectName)
		if err != nil {
			s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
				Type: discordgo.InteractionResponseChannelMessageWithSource,
				Data: &discordgo.InteractionResponseData{Content: fmt.Sprintf("❌ Error: %v", err)},
			})
			return
		}

		err = b.DB.BindChannelToProject(ctx, i.ChannelID, projectName, projectPath)
		if err != nil {
			s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
				Type: discordgo.InteractionResponseChannelMessageWithSource,
				Data: &discordgo.InteractionResponseData{Content: fmt.Sprintf("❌ DB Error: %v", err)},
			})
			return
		}

		s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
			Type: discordgo.InteractionResponseChannelMessageWithSource,
			Data: &discordgo.InteractionResponseData{Content: fmt.Sprintf("✅ Channel bound to project: `%s`", projectName)},
		})

	case "release":
		err := b.DB.UnbindChannel(ctx, i.ChannelID)
		if err != nil {
			s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
				Type: discordgo.InteractionResponseChannelMessageWithSource,
				Data: &discordgo.InteractionResponseData{Content: fmt.Sprintf("❌ DB Error: %v", err)},
			})
			return
		}
		s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
			Type: discordgo.InteractionResponseChannelMessageWithSource,
			Data: &discordgo.InteractionResponseData{Content: "🔓 Channel released from project."},
		})
	}
}

func (b *Bot) handleMissionDebug(s *discordgo.Session, i *discordgo.InteractionCreate) {
	ctx := context.Background()
	_, projectPath, err := b.DB.GetChannelBinding(ctx, i.ChannelID)
	if err != nil {
		s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
			Type: discordgo.InteractionResponseChannelMessageWithSource,
			Data: &discordgo.InteractionResponseData{Content: "❌ Channel not bound."},
		})
		return
	}

	missionID := "debug-" + b.generateFunkyID()
	s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
		Type: discordgo.InteractionResponseChannelMessageWithSource,
		Data: &discordgo.InteractionResponseData{Content: "🔍 Running environment debug..."},
	})

	msg, _ := s.InteractionResponse(i.Interaction)
	thread, _ := s.MessageThreadStartComplex(i.ChannelID, msg.ID, &discordgo.ThreadStart{
		Name: "Debug: Environment",
		Type: discordgo.ChannelTypeGuildPublicThread,
	})
	
	b.mu.Lock()
	b.MissionThreads[missionID] = thread.ID
	b.mu.Unlock()

	// Run tty and fd check
	b.Manager.StartMission(ctx, missionID, projectPath, "sh", "-c", "tty; ls -l /proc/self/fd; env | grep TERM")
}

func (b *Bot) handleMissionSlash(s *discordgo.Session, i *discordgo.InteractionCreate) {
	ctx := context.Background()
	projectName, projectPath, err := b.DB.GetChannelBinding(ctx, i.ChannelID)
	if err != nil {
		s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
			Type: discordgo.InteractionResponseChannelMessageWithSource,
			Data: &discordgo.InteractionResponseData{Content: "❌ This channel is not bound to a project. Use `/project attach` first."},
		})
		return
	}

	var prompt, raw, stopID string
	for _, opt := range i.ApplicationCommandData().Options {
		switch opt.Name {
		case "prompt":
			prompt = opt.StringValue()
		case "raw":
			raw = opt.StringValue()
		case "stop":
			stopID = opt.StringValue()
		}
	}

	if stopID != "" {
		err := b.Manager.StopMission(stopID)
		content := fmt.Sprintf("🛑 Mission `%s` stopped.", stopID)
		if err != nil {
			content = fmt.Sprintf("❌ Error: %v", err)
		}
		s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
			Type: discordgo.InteractionResponseChannelMessageWithSource,
			Data: &discordgo.InteractionResponseData{Content: content},
		})
		return
	}

	missionID := b.generateFunkyID()

	// Initial response
	s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
		Type: discordgo.InteractionResponseChannelMessageWithSource,
		Data: &discordgo.InteractionResponseData{
			Content: fmt.Sprintf("🚀 Starting mission `%s` in project `%s`...", missionID, projectName),
		},
	})

	msg, _ := s.InteractionResponse(i.Interaction)
	thread, err := s.MessageThreadStartComplex(i.ChannelID, msg.ID, &discordgo.ThreadStart{
		Name:                fmt.Sprintf("Mission: %s [%s]", missionID, projectName),
		AutoArchiveDuration: 60,
		Type:                discordgo.ChannelTypeGuildPublicThread,
	})

	if err == nil {
		b.mu.Lock()
		b.MissionThreads[missionID] = thread.ID
		b.mu.Unlock()
	} else {
		b.mu.Lock()
		b.MissionThreads[missionID] = i.ChannelID
		b.mu.Unlock()
	}

	if raw != "" {
		parts := strings.Fields(raw)
		cmd := parts[0]
		args := []string{}
		if len(parts) > 1 {
			args = parts[1:]
		}
		err = b.Manager.StartMission(ctx, missionID, projectPath, cmd, args...)
	} else {
		cmdArgs := []string{"--output-format", "text"}
		if prompt != "" {
			cmdArgs = append(cmdArgs, "--prompt", prompt)
		}
		err = b.Manager.StartMission(ctx, missionID, projectPath, "gemini", cmdArgs...)
	}

	if err != nil {
		s.FollowupMessageCreate(i.Interaction, true, &discordgo.WebhookParams{
			Content: fmt.Sprintf("❌ Failed to start: %v", err),
		})
	}
}

func (b *Bot) onLog(missionID, text string) {
	b.mu.Lock()
	threadID, ok := b.MissionThreads[missionID]
	b.mu.Unlock()

	if ok {
		cleanText := b.Manager.StripANSI(text)
		if cleanText == "" {
			return
		}
		
		if len(cleanText) > 1950 {
			cleanText = cleanText[:1950] + "..."
		}
		
		b.Session.ChannelMessageSend(threadID, cleanText)
	}
}

func (b *Bot) Close() {
	b.Session.Close()
}

func (b *Bot) messageCreate(s *discordgo.Session, m *discordgo.MessageCreate) {
	if m.Author.ID == s.State.User.ID {
		return
	}

	b.mu.Lock()
	var missionID string
	for id, threadID := range b.MissionThreads {
		if threadID == m.ChannelID {
			missionID = id
			break
		}
	}
	b.mu.Unlock()

	if missionID != "" {
		err := b.Manager.WriteToMission(missionID, m.Content)
		if err != nil {
			log.Printf("Failed to write to mission %s stdin: %v", missionID, err)
		}
	}
}

func (b *Bot) SendMessage(channelID, message string) error {
	_, err := b.Session.ChannelMessageSend(channelID, message)
	return err
}

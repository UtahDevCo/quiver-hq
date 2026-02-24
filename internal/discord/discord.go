package discord

import (
	"context"
	"fmt"
	"log"
	"strings"
	"sync"

	"github.com/bwmarrin/discordgo"
	"github.com/chrisesplin/quiver-hq/internal/manager"
	"github.com/chrisesplin/quiver-hq/internal/projects"
)

type Bot struct {
	Session        *discordgo.Session
	Manager        *manager.Manager
	Scanner        *projects.Scanner
	MissionThreads map[string]string // missionID -> threadID
	mu             sync.Mutex
}

func NewBot(token string, mgr *manager.Manager, scanner *projects.Scanner) (*Bot, error) {
	dg, err := discordgo.New("Bot " + token)
	if err != nil {
		return nil, fmt.Errorf("error creating Discord session: %v", err)
	}

	bot := &Bot{
		Session:        dg,
		Manager:        mgr,
		Scanner:        scanner,
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
			Name:        "mission",
			Description: "Manage Quiver missions",
			Options: []*discordgo.ApplicationCommandOption{
				{
					Type:        discordgo.ApplicationCommandOptionSubCommand,
					Name:        "list",
					Description: "List all active missions",
				},
				{
					Type:        discordgo.ApplicationCommandOptionSubCommand,
					Name:        "stop",
					Description: "Stop a running mission",
					Options: []*discordgo.ApplicationCommandOption{
						{
							Type:        discordgo.ApplicationCommandOptionString,
							Name:        "id",
							Description: "The ID of the mission to stop",
							Required:    true,
						},
					},
				},
				{
					Type:        discordgo.ApplicationCommandOptionSubCommand,
					Name:        "start",
					Description: "Start a new mission",
					Options: []*discordgo.ApplicationCommandOption{
						{
							Type:        discordgo.ApplicationCommandOptionString,
							Name:        "project",
							Description: "The project/submodule name",
							Required:    true,
							Autocomplete: true,
						},
						{
							Type:        discordgo.ApplicationCommandOptionString,
							Name:        "id",
							Description: "A unique ID for this mission",
							Required:    true,
						},
						{
							Type:        discordgo.ApplicationCommandOptionString,
							Name:        "command",
							Description: "The command to run",
							Required:    true,
						},
						{
							Type:        discordgo.ApplicationCommandOptionString,
							Name:        "args",
							Description: "Space-separated arguments",
							Required:    false,
						},
					},
				},
			},
		},
	}

	for _, v := range commands {
		_, err := dg.ApplicationCommandCreate(dg.State.User.ID, "", v)
		if err != nil {
			log.Printf("Cannot create '%v' command: %v", v.Name, err)
		}
	}

	log.Println("Discord bot is now running with Slash Commands.")
	return bot, nil
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
	// Format: approval_<approve|deny>_<missionID>
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
			Components: []discordgo.MessageComponent{}, // Remove buttons
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

	if data.Name == "mission" {
		subcommand := data.Options[0]
		if subcommand.Name == "start" {
			// Find the 'project' option
			for _, opt := range subcommand.Options {
				if opt.Name == "project" && opt.Focused {
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
	case "mission":
		b.handleMissionSlash(s, i)
	}
}

func (b *Bot) handleMissionSlash(s *discordgo.Session, i *discordgo.InteractionCreate) {
	options := i.ApplicationCommandData().Options[0]
	
	switch options.Name {
	case "list":
		missions := b.Manager.ListActiveMissions()
		content := "No active missions."
		if len(missions) > 0 {
			content = fmt.Sprintf("Active Missions: %s", strings.Join(missions, ", "))
		}
		s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
			Type: discordgo.InteractionResponseChannelMessageWithSource,
			Data: &discordgo.InteractionResponseData{Content: content},
		})

	case "stop":
		id := options.Options[0].StringValue()
		err := b.Manager.StopMission(id)
		content := fmt.Sprintf("🛑 Mission `%s` stopped.", id)
		if err != nil {
			content = fmt.Sprintf("❌ Error: %v", err)
		}
		s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
			Type: discordgo.InteractionResponseChannelMessageWithSource,
			Data: &discordgo.InteractionResponseData{Content: content},
		})

	case "start":
		var project, id, cmdStr, argsStr string
		for _, opt := range options.Options {
			switch opt.Name {
			case "project":
				project = opt.StringValue()
			case "id":
				id = opt.StringValue()
			case "command":
				cmdStr = opt.StringValue()
			case "args":
				argsStr = opt.StringValue()
			}
		}

		projectPath, err := b.Scanner.GetProjectPath(project)
		if err != nil {
			s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
				Type: discordgo.InteractionResponseChannelMessageWithSource,
				Data: &discordgo.InteractionResponseData{Content: fmt.Sprintf("❌ Error: %v", err)},
			})
			return
		}

		// Initial response
		s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
			Type: discordgo.InteractionResponseChannelMessageWithSource,
			Data: &discordgo.InteractionResponseData{
				Content: fmt.Sprintf("🚀 Starting mission `%s` in project `%s`...", id, project),
			},
		})

		// Follow-up with thread creation
		msg, _ := s.InteractionResponse(i.Interaction)
		thread, err := s.MessageThreadStartComplex(i.ChannelID, msg.ID, &discordgo.ThreadStart{
			Name:                fmt.Sprintf("Mission: %s [%s]", id, project),
			AutoArchiveDuration: 60,
			Type:                discordgo.ChannelTypeGuildPublicThread,
		})

		if err == nil {
			b.mu.Lock()
			b.MissionThreads[id] = thread.ID
			b.mu.Unlock()
			s.ChannelMessageSend(i.ChannelID, fmt.Sprintf("Thread created: <#%s>", thread.ID))
		} else {
			b.mu.Lock()
			b.MissionThreads[id] = i.ChannelID
			b.mu.Unlock()
		}

		cmdArgs := strings.Fields(argsStr)
		err = b.Manager.StartMission(context.Background(), id, projectPath, cmdStr, cmdArgs...)
		if err != nil {
			s.FollowupMessageCreate(i.Interaction, true, &discordgo.WebhookParams{
				Content: fmt.Sprintf("❌ Failed to start mission: %v", err),
			})
		}
	}
}

func (b *Bot) onLog(missionID, text string) {
	b.mu.Lock()
	threadID, ok := b.MissionThreads[missionID]
	b.mu.Unlock()

	if ok {
		if strings.HasPrefix(text, "QUIVER_SIGNAL:NEED_INPUT") {
			b.Session.ChannelMessageSend(threadID, "🚨 **Attention Required**: This agent is waiting for your input!")
			return
		}
		b.Session.ChannelMessageSend(threadID, text)
	}
}

func (b *Bot) Close() {
	b.Session.Close()
}

func (b *Bot) messageCreate(s *discordgo.Session, m *discordgo.MessageCreate) {
	if m.Author.ID == s.State.User.ID {
		return
	}

	// Check if this message is in a mission thread
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
		// This is a reply in a mission thread, pipe it to stdin
		err := b.Manager.WriteToMission(missionID, m.Content)
		if err != nil {
			log.Printf("Failed to write to mission %s stdin: %v", missionID, err)
		}
		return
	}
}

func (b *Bot) SendMessage(channelID, message string) error {
	_, err := b.Session.ChannelMessageSend(channelID, message)
	return err
}

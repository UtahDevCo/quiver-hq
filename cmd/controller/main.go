package main

import (
	"bytes"
	"context"
	"fmt"
	"log"
	"os"
	"os/exec"
	"os/signal"
	"syscall"

	"github.com/chrisesplin/quiver-hq/internal/db"
	"github.com/chrisesplin/quiver-hq/internal/discord"
	"github.com/chrisesplin/quiver-hq/internal/manager"
	"github.com/chrisesplin/quiver-hq/internal/projects"
	"github.com/google/generative-ai-go/genai"
	"github.com/joho/godotenv"
	"google.golang.org/api/option"
)

func main() {
	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()

	rootDir, _ := os.Getwd()

	// Load .env.local if it exists
	if err := godotenv.Load(".env.local"); err != nil {
		log.Println("No .env.local found or error loading it, proceeding with env/1Password")
	}

	// 1. Load Secrets
	apiKey := getSecret("GEMINI_API_KEY")
	discordToken := getSecret("DISCORD_BOT_TOKEN")

	if apiKey == "" || apiKey == "YOUR_API_KEY_HERE" {
		log.Fatal("GEMINI_API_KEY is required")
	}

	// 2. Initialize DB
	database, err := db.InitDB("quiver.db")
	if err != nil {
		log.Fatalf("failed to initialize database: %v", err)
	}
	defer database.Close()

	if err := database.InitSchema("schema.sql"); err != nil {
		log.Fatalf("failed to initialize schema: %v", err)
	}

	// 3. Initialize Manager & Scanner
	mgr := manager.NewManager(database, rootDir)
	scanner := projects.NewScanner(rootDir)

	// 4. Initialize Discord
	var bot *discord.Bot
	if discordToken != "" {
		bot, err = discord.NewBot(discordToken, mgr, scanner, database)
		if err != nil {
			log.Printf("Warning: failed to initialize Discord bot: %v", err)
		} else {
			defer bot.Close()
		}
	} else {
		log.Println("DISCORD_BOT_TOKEN not found, running without Discord integration")
	}

	// 5. Initialize Gemini
	client, err := genai.NewClient(ctx, option.WithAPIKey(apiKey))
	if err != nil {
		log.Fatalf("failed to create genai client: %v", err)
	}
	defer client.Close()

	// 6. System Check
	runSystemCheck(ctx, database, client, bot)

	log.Println("Quiver HQ Daemon is fully operational. Press Ctrl+C to exit.")
	<-ctx.Done()
	log.Println("Shutting down Quiver HQ...")
}

func getSecret(key string) string {
	val := os.Getenv(key)
	if val != "" {
		return val
	}
	        log.Printf("%s not in env, checking 1Password...", key)
	        cmd := exec.Command("op", "read", fmt.Sprintf("op://Dev/quiver-hq/%s", key))
	                out, err := cmd.Output()
	                if err != nil {
	                        return ""
	                }
	return string(bytes.TrimSpace(out))
}

func runSystemCheck(ctx context.Context, database *db.DB, client *genai.Client, bot *discord.Bot) {
	model := client.GenerativeModel("gemini-flash-latest")
	missionID := "system-check"
	
	database.CreateMission(ctx, missionID, "started", "Daemon Startup System Check")

	resp, err := model.GenerateContent(ctx, genai.Text("System check. Reply with 'Daemon Online'."))
	if err != nil {
		log.Printf("Gemini system check failed: %v", err)
		return
	}

	var responseText string
	for _, cand := range resp.Candidates {
		for _, part := range cand.Content.Parts {
			responseText += fmt.Sprintf("%v", part)
		}
	}

	log.Printf("System Check Result: %s", responseText)
	database.LogMission(ctx, missionID, "System check complete", responseText)

	if bot != nil {
		// Attempt to notify a channel if DISCORD_CHANNEL_ID is set
		channelID := os.Getenv("DISCORD_CHANNEL_ID")
		if channelID == "" {
			channelID = getSecret("DISCORD_CHANNEL_ID")
		}
		if channelID != "" {
			bot.SendMessage(channelID, fmt.Sprintf("🚀 **Quiver HQ Daemon Online**\nGemini Status: %s", responseText))
		}
	}
}

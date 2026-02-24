package main

import (
	"context"
	"fmt"
	"log"
	"time"

	"github.com/chrisesplin/quiver-hq/internal/db"
	"github.com/chrisesplin/quiver-hq/internal/manager"
)

func main() {
	database, err := db.InitDB("quiver.db")
	if err != nil {
		log.Fatal(err)
	}
	defer database.Close()

	mgr := manager.NewManager(database)

	ctx := context.Background()
	missionID := "test-run-2"

	fmt.Println("Starting test mission...")
	err = mgr.StartMission(ctx, missionID, ".", "./test-mission")
	if err != nil {
		log.Fatalf("Failed to start mission: %v", err)
	}

	// Wait for it to finish (it takes 5 seconds)
	time.Sleep(7 * time.Second)

	fmt.Println("Checking database for logs...")
	rows, err := database.Query("SELECT entry FROM mission_logs WHERE mission_id = ?", missionID)
	if err != nil {
		log.Fatal(err)
	}
	defer rows.Close()

	for rows.Next() {
		var entry string
		rows.Scan(&entry)
		fmt.Printf("Log: %s\n", entry)
	}
}

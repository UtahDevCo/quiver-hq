package db

import (
	"context"
	"database/sql"
	_ "modernc.org/sqlite"
	"os"
)

type DB struct {
	*sql.DB
}

func InitDB(path string) (*DB, error) {
	db, err := sql.Open("sqlite", path)
	if err != nil {
		return nil, err
	}

	if err := db.Ping(); err != nil {
		return nil, err
	}

	return &DB{db}, nil
}

func (db *DB) InitSchema(schemaPath string) error {
	schema, err := os.ReadFile(schemaPath)
	if err != nil {
		return err
	}

	_, err = db.Exec(string(schema))
	return err
}

func (db *DB) LogMission(ctx context.Context, missionID, entry string, metadata string) error {
	_, err := db.ExecContext(ctx, "INSERT INTO mission_logs (mission_id, entry, metadata) VALUES (?, ?, ?)", missionID, entry, metadata)
	return err
}

func (db *DB) CreateMission(ctx context.Context, id, status, goal string) error {
	_, err := db.ExecContext(ctx, "INSERT INTO missions (id, status, goal) VALUES (?, ?, ?)", id, status, goal)
	return err
}

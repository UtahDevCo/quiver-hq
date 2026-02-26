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

func (db *DB) BindChannelToProject(ctx context.Context, channelID, projectName, projectPath string) error {
	_, err := db.ExecContext(ctx, "INSERT OR REPLACE INTO channel_projects (channel_id, project_name, project_path) VALUES (?, ?, ?)", channelID, projectName, projectPath)
	return err
}

func (db *DB) UnbindChannel(ctx context.Context, channelID string) error {
	_, err := db.ExecContext(ctx, "DELETE FROM channel_projects WHERE channel_id = ?", channelID)
	return err
}

func (db *DB) GetChannelBinding(ctx context.Context, channelID string) (projectName, projectPath string, err error) {
	err = db.QueryRowContext(ctx, "SELECT project_name, project_path FROM channel_projects WHERE channel_id = ?", channelID).Scan(&projectName, &projectPath)
	return
}

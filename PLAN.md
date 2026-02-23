Act as a Senior Go Engineer. We are building "Quiver HQ," an agentic controller for my development server. 

### CONTEXT:
1. ENVIRONMENT: NixOS on WSL2 (2026 stack).
2. TOOLS AVAILABLE: Go 1.22, SQLite3, 1Password CLI (op), and 'gh'.
3. USER: Christopher Esplin (Software Engineer, 15yrs exp).
4. PROJECT ROOT: ~/dev/quiver-hq

### THE MISSION:
Initialize a professional Go workspace that includes a "Mission Log" system. The controller must be able to record its own actions and thoughts into a SQLite database.

### YOUR TASKS:
1. GENERATE `go.mod`: Initialize the module as `github.com/chrisesplin/quiver-hq`.
2. CREATE `schema.sql`: Define a 'missions' table (id, status, goal, created_at) and a 'mission_logs' table (id, mission_id, entry, metadata, timestamp).
3. CREATE `internal/db/db.go`: Write a clean wrapper to initialize the SQLite connection using 'modernc.org/sqlite' (the CGO-free driver is preferred for NixOS compatibility).
4. CREATE `cmd/controller/main.go`: 
   - Load the GEMINI_API_KEY from environment.
   - Initialize the database.
   - Make a "system check" call to Gemini.
   - Log the success of the system check into the SQLite 'mission_logs' table.

### CONSTRAINTS:
- Use standard Go project layout.
- Use 'database/sql' for the DB layer.
- Ensure the code handles context and graceful shutdowns.

Output the file structures and code blocks clearly so I can pipe them to files.

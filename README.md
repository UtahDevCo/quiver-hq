# Quiver HQ NixOS Configuration

This repository contains the complete NixOS and home-manager configuration for the hosts and development environments used at Quiver HQ. It is designed to be fully reproducible and managed via this git repository.

## Quiver HQ Agentic Tools

The project includes a Go-based agentic controller and a secret management utility.

### 1. Secret Management (`quiver-secrets`)

Manage environment variables via 1Password.

*   **Ingest**: Scan a project for `.env` files, push secrets to 1Password, and create a `.env.tmpl` file.
    ```bash
    ./quiver-secrets ingest ./my-project
    ```
*   **Hydrate**: Reconstruct a `.env` file from 1Password using the `.env.tmpl`.
    ```bash
    ./quiver-secrets hydrate ./my-project
    ```

### 2. Mission Controller (`controller`)

The central daemon that orchestrates agents and logs missions to SQLite.

*   **Systemd Service**: The controller is managed as a NixOS systemd service.
    ```bash
    qlogs      # View live daemon logs
    qrestart   # Restart the daemon
    ```
*   **Manual Run**: (For debugging)
    ```bash
    nix develop -c env GEMINI_API_KEY=$(op read op://Personal/quiver-hq/GEMINI_API_KEY) \
        DISCORD_BOT_TOKEN=$(op read op://Personal/quiver-hq/DISCORD_BOT_TOKEN) \
        ./controller
    ```

### 3. Remote Access & Stability

*   **Tailscale**: The system is configured with Tailscale for secure remote access.
*   **Persistence**: The daemon automatically starts on boot (or WSL startup) and restarts on failure via systemd.

### 4. Discord Slash Commands

Talk to the daemon remotely via Discord using `/` commands:

*   `/ping`: Check if the daemon is online.
*   `/mission list`: List all active missions.
*   `/mission start <project> <id> <command> [args...]`: Start a new mission. 
    *   **Autocomplete**: The `project` field will suggest submodules found in `.gitmodules`.
    *   **Threads**: Creates a dedicated thread for output.
*   `/mission stop <id>`: Kill a running mission.

### 4. Human-in-the-Loop (Approval Gates)

Agents can request approval for risky actions by outputting a specific signal:
`QUIVER_SIGNAL:REQUEST_APPROVAL <prompt>`

The daemon will present **Approve** and **Deny** buttons in the Discord thread. The agent will wait for your decision, which is piped back to its `stdin` as `APPROVED` or `DENIED`.

### 5. Database Management

Missions and logs are stored in `quiver.db`.
```bash
nix develop -c sqlite3 quiver.db "SELECT * FROM mission_logs;"
```

---

## 🚀 Setup & Integration Guide

Follow these steps to fully activate the Quiver HQ ecosystem.

### 1. 1Password Integration (The Secret Vault)
The controller expects a 1Password item named `quiver-hq` to store its credentials.

1.  **Sign In**: Run `opsignin` (or `eval $(op signin)`) in your terminal.
2.  **Create Item**: Create a new **API Credential** or **Secure Note** in 1Password named `quiver-hq`.
3.  **Add Fields**:
    *   `GEMINI_API_KEY`: Your Google AI Studio API key.
    *   `DISCORD_BOT_TOKEN`: Your Discord bot token (see below).
    *   `DISCORD_CHANNEL_ID`: (Optional) The ID of the channel where the daemon should post startup notifications.

### 2. Discord Integration (The UI)
You need to create a Discord application to act as the Quiver HQ interface.

1.  **Developer Portal**: Go to the [Discord Developer Portal](https://discord.com/developers/applications).
2.  **Create App**: Click "New Application" and name it "Quiver HQ".
3.  **Bot Setup**:
    *   Go to the **Bot** tab.
    *   Reset/Copy the **Token** and save it to your `quiver-hq` 1Password item.
    *   **Crucial**: Scroll down to "Privileged Gateway Intents" and enable **Message Content Intent**. This is required to pipe your replies to the agent's stdin.
4.  **OAuth2 (Invite)**:
    *   Go to **OAuth2** -> **URL Generator**.
    *   Select scopes: `bot`, `applications.commands`.
    *   Select bot permissions: `Read Messages/View Channels`, `Send Messages`, `Create Public Threads`, `Send Messages in Threads`.
    *   Open the generated URL to invite the bot to your server.

### 3. Tailscale Integration (The Network)
Tailscale provides secure remote access to your NixOS/WSL machine.

1.  **Apply Config**: Run `sudo nixos-rebuild switch --flake .#quiver-wsl`.
2.  **Authenticate**: Run `sudo tailscale up`.
3.  **Login**: Click the link provided in the terminal to add this machine to your Tailnet.
4.  **Remote Control**: You can now access your Quiver HQ dashboard or terminal from any device on your Tailnet (phone, laptop, etc.).

### 4. Running the Controller
Once the secrets are set in 1Password and the NixOS config is applied:

1.  **Build**: `nix develop -c go build -o controller ./cmd/controller/main.go`
2.  **Start Service**: `sudo systemctl start quiver-controller`
3.  **Watch Logs**: `qlogs`

---

## 🛠️ Standalone / WSL2 Setup (Non-NixOS)

If you are running on a standard WSL2 instance (e.g., Ubuntu) and want to use `.env.local` for secrets:

### 1. Create a 1Password Service Account Token
Create a service account token with a read-only vault scope:

```bash
op service-account create "nix-view-copy" --vault "Dev:read_items" --expires-in 90d
```

Then store the resulting token in `.env.local` as:

```bash
OP_SERVICE_ACCOUNT_TOKEN=<your-token>
```

### 2. Build and Prepare
```bash
go build -o controller ./cmd/controller/main.go
chmod +x qcontrol
```

### 3. Configure Systemd User Service
To make the bot start automatically with WSL2:
```bash
mkdir -p ~/.config/systemd/user/
cp quiver-controller.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable quiver-controller.service
systemctl --user start quiver-controller.service
```

### 4. Background Persistence (Linger)
By default, user services stop when you close your last terminal. To keep the bot running in the background:
```bash
./qcontrol linger-enable
```

### 5. Management Script (`qcontrol`)
Use the included helper script for common tasks:
- `./qcontrol logs`: View live output.
- `./qcontrol restart`: Restart the daemon.
- `./qcontrol status`: Check if it's running.

---

## 🤖 Interacting with the Bot

The Quiver HQ Controller is designed to be your interface to all projects in the `projects/` directory.

### 1. Projects as Submodules
The controller automatically scans the `projects/` folder. To add a new project:
```bash
git submodule add <repo-url> projects/<project-name>
```

### 2. Starting a Mission (Project Interaction)
In Discord, use the `/mission start` command. 
- **Project**: Use the autocomplete to select your project.
- **ID**: Give this specific task a name (e.g., `fix-bugs`).
- **Command**: The command to run (e.g., `npm`, `python`, `go`).
- **Args**: Arguments for the command (e.g., `run dev`, `main.py`).

### 3. Dedicated Threads
When you start a mission, the bot creates a **dedicated thread** in Discord.
- **Output**: All logs from your command are piped to this thread.
- **Input**: Any message you type in the thread is piped directly to the command's `stdin`. This allows you to interact with CLIs or provide input to your scripts in real-time.

### 4. Approval Gates
If an agent/script outputs `QUIVER_SIGNAL:REQUEST_APPROVAL <prompt>`, the bot will pause and show **Approve/Deny** buttons. This is perfect for "Human-in-the-loop" workflows where you want to review an action before it executes.

---

## Workflows

There are two primary workflows for using this repository: managing an existing system and installing a new system from scratch.

### 1. Day-to-Day System Management (Existing System)

This is the most common workflow. Use it to apply updates or configuration changes to a system that is already running this configuration.

1.  **Edit Configuration**: Make any desired changes to the `.nix` files in this repository.
2.  **Apply Changes**: From within this repository's root directory (`/home/chris/dev/quiver-hq`), run the following command to apply the configuration to your running system:

    ```bash
    sudo nixos-rebuild switch --flake .#quiver-wsl
    ```

    *   `sudo nixos-rebuild switch`: The standard command to build and activate a new system generation.
    *   `--flake .`: Tells the command to use the `flake.nix` in the current directory.
    *   `#quiver-wsl`: Specifies which `nixosConfigurations` output from your `flake.nix` to build and apply.

3.  **Commit**: Once you are happy with the changes, commit them to git to track your configuration's history.

    ```bash
    git add .
    git commit -m "feat: add new package and update shell alias"
    ```

### 2. "From Scratch" Installation (New System)

Use this workflow to install a completely new NixOS system (e.g., a new WSL instance, a new VM, or a new physical machine) using this repository as the source of truth.

1.  **Boot Installer**: Boot the target machine using a standard NixOS installer image.
2.  **Prepare Disks**: Partition and format the disks as required for your new system.
3.  **Mount Filesystems**: Mount the newly created filesystems under `/mnt`. For example, mount your root partition on `/mnt` and your boot partition on `/mnt/boot`.
4.  **Clone Repository**: Clone this repository onto the installation medium.

    ```bash
    git clone https://github.com/your-username/quiver-hq.git /mnt/etc/nixos
    ```
    *(Note: It's common practice to clone the configuration into `/mnt/etc/nixos`)*

5.  **Run Installation**: Instead of generating a new configuration, run `nixos-install` and point it directly to the host definition within your cloned flake:

    ```bash
    sudo nixos-install --flake /mnt/etc/nixos#quiver-wsl
    ```

After the installation is complete and you reboot, the new system will be running the exact configuration defined in this repository.

### 3. Migrating a Project (Submodule Integration)

To migrate an existing project into the Quiver HQ ecosystem for management via the Mission Controller:

1.  **Add the Submodule**:
    Add the project as a git submodule within the `projects/` directory.
    ```bash
    cd dev/quiver-hq
    git submodule add <git-url> projects/<project-name>
    ```

2.  **Ingest Secrets** (Optional):
    If the project uses `.env` files, you can manage them via 1Password.
    - Create or move your local secrets to `.env.local` within the project directory.
    - Run the ingestion tool:
      ```bash
      ./bin/quiver-secrets ingest projects/<project-name>
      ```
    - This pushes the secrets to the `quiver-hq` item in 1Password and generates a `.env.tmpl` file.

3.  **Commit & Push**:
    Commit the new submodule, the `.gitmodules` file, and any generated `.env.tmpl` files.
    ```bash
    git add .
    git commit -m "feat: migrate <project-name> to Quiver HQ"
    git push
    ```

4.  **Verification**:
    The Mission Controller will automatically detect the new project (via the `Scanner`) and include it in the `/mission start` autocomplete options in Discord.

## Configuration Recommendations

Your configuration is well-structured. Here are a few recommendations to make it even more robust and portable.

### Use Portable Paths

Your `home.nix` contains aliases with hardcoded absolute paths (e.g., `/home/chris/dev/quiver-hq`). This can break if you clone the repo to a different location or use it for another user.

**Recommendation**: Modify the `reload` alias in `nixos/home.nix` to be independent of its absolute path. A more robust version would change directory to the known location first:

*   **From**: `alias reload="sudo nixos-rebuild switch --flake /home/chris/dev/quiver-hq#quiver-wsl"`
*   **To**: `alias reload='(cd /home/chris/dev/quiver-hq && sudo nixos-rebuild switch --flake .#quiver-wsl)'`

This ensures the command always runs from the correct directory context.

### Centralize Shell Configuration

You have correctly placed your Zsh configuration inside `home.nix` using `programs.zsh.initContent`. The file at `nixos/files/.zshrc` appears to be unused, as its content is managed by home-manager. This is good! Centralizing configuration in `home.nix` is the idiomatic approach.

### Hardware Configuration

The file `nixos/hosts/wsl/hardware-configuration.nix` is specific to your current machine. When installing on a new machine, NixOS will generate a new version of this file that is specific to that new hardware. Your current setup correctly isolates this file from the common configuration.

---

## 🌐 Caddy Reverse Proxy Setup (Tailscale Network Serving)

Serve multiple websites and services to your Tailscale network devices using Caddy as a reverse proxy on **quiver-pn54** (Ryzen 5 desktop). This setup provides automatic HTTPS via Let's Encrypt and supports both private (Tailscale VPN) and public (optional Funnel) access.

### Architecture Overview

- **Caddy Server**: Runs on quiver-pn54, listens on ports 80 and 443
- **Services**: Run on localhost with unique ports (3000, 3001, 4000, etc.)
- **Reverse Proxy**: Routes `*.chrisesplin.com` subdomains to backend services
- **HTTPS**: Automatic certificates from Let's Encrypt (email: chris@chrisesplin.com)
- **Network Access**: Private (Tailscale VPN) + optional public (Funnel)

### Quick Start

#### 1. Apply NixOS Configuration

First, deploy Caddy to quiver-pn54:

```bash
cd /home/chris/dev/quiver-hq
sudo nixos-rebuild switch --flake .#quiver-pn54
```

This will:
- Install and enable Caddy service
- Configure automatic HTTPS with Let's Encrypt
- Open firewall ports 80 and 443
- Load the Caddyfile from the repository

Verify Caddy is running:
```bash
sudo systemctl status caddy
sudo journalctl -u caddy -f  # View live logs
```

#### 2. Configure a Service

Start a service on a unique port. For example, if you have a Next.js app:

```bash
# Terminal 1: On quiver-pn54
cd ~/my-project
npm run dev  # Listens on localhost:3000
```

#### 3. Add to Caddyfile

Edit `/home/chris/dev/quiver-hq/Caddyfile` and add your service:

```caddy
app.chrisesplin.com {
  reverse_proxy localhost:3000
}
```

Reload Caddy to apply changes:
```bash
sudo systemctl reload caddy
```

#### 4. Access from Tailscale Network

**Option A: With DNS configured** (recommended):
```bash
# From any device on your Tailscale network
curl https://app.chrisesplin.com
```

**Option B: Without DNS** (temporary):
```bash
# Add to /etc/hosts on your client machine:
# 100.x.x.x app.chrisesplin.com

curl https://app.chrisesplin.com
```

### Adding New Services

#### Services Reference

Here are all the services currently configured in your Caddyfile:

| Service | Subdomain | Port | Technology | Purpose |
|---------|-----------|------|-----------|---------|
| **Foundation-Web** | app.chrisesplin.com | 3000 | Next.js 15, TypeScript | Multi-tenant B2B SaaS (Demo, Buyer, Operator, Super Admin dashboards) |
| **Inngest** | inngest.chrisesplin.com | 8288 | Workflow Engine | Event-driven async workflows (dev) |
| **Email Preview** | email.chrisesplin.com | 55420 | jsx-email | Email template testing (dev) |
| **Jaeger** | tracing.chrisesplin.com | 16686 | OpenTelemetry | Distributed tracing dashboard (dev) |
| **Therapy Animal Hub** | therapy.chrisesplin.com | 3001 | Next.js, TypeScript | Mental health therapy animal platform with Stripe, Twilio |
| **Wiley** | wiley.chrisesplin.com | 3600 | Next.js, TypeScript, Firebase | AI call management with Netsapiens & AltaWorx integration |
| **Trikin** | trikin.chrisesplin.com | 3700 | Next.js, TypeScript, Cloudflare D1 | Property management system with real estate integrations |
| **K1** | k1.chrisesplin.com | 3010 | Next.js Turbo monorepo | Shadcn/ui component library template |

#### Starting Services

**Foundation-Web:**
```bash
cd projects/foundation-web
npm run dev  # Runs on localhost:3000
```

**Therapy Animal Hub:**
```bash
cd projects/therapyanimalhub.com
npm run dev  # Runs on localhost:3001
```

**Wiley:**
```bash
cd projects/wiley
next dev --port 3600  # Or check for configured dev script
```

**Trikin:**
```bash
cd projects/trikin
next dev --port 3700  # Or check for configured dev script
```

**K1 (Turbo Monorepo):**
```bash
cd projects/k1
pnpm dev  # Turbo manages ports dynamically; may use 3000-3009 range
# If conflicts with foundation-web, configure different port in next.config.js
```

#### Troubleshooting Port Conflicts

If multiple projects try to use port 3000:

**Option 1: Run on different machines**
- Foundation-Web on quiver-pn54 (port 3000)
- Other services on different Tailscale machines

**Option 2: Run services sequentially**
- Stop Foundation-Web before starting K1
- Or start K1 on explicit port:
  ```bash
  cd projects/k1
  PORT=3010 pnpm dev  # If supported by project config
  ```

**Option 3: Use environment variables**
- Check project `.env` or `.env.example` for port configuration
- Many Next.js projects support `PORT` env var

**Option 4: Modify next.config.js**
```javascript
module.exports = {
  server: {
    port: 3010,
  }
}
```

#### Standard Pattern

Edit `/home/chris/dev/quiver-hq/Caddyfile` and add a block for each service:

```caddy
service-name.chrisesplin.com {
  reverse_proxy localhost:PORT
}
```

Then reload Caddy:
```bash
sudo systemctl reload caddy
```

#### Examples

**API Service:**
```caddy
api.chrisesplin.com {
  reverse_proxy localhost:3001
}
```

**Multiple routes to one host:**
```caddy
dashboard.chrisesplin.com {
  reverse_proxy /api/* localhost:4000
  reverse_proxy /* localhost:4001
}
```

**With request/response headers:**
```caddy
service.chrisesplin.com {
  reverse_proxy localhost:5000 {
    header_up X-Forwarded-Proto https
    header_up X-Forwarded-Host {host}
  }
}
```

### DNS & Tailscale Configuration

#### Option 1: Tailscale MagicDNS (Easiest)

1. Go to [Tailscale Admin Console](https://login.tailscale.com/admin/dns)
2. Enable **MagicDNS** for your tailnet
3. Add a **DNS nameserver** rule:
   - Domain: `chrisesplin.com`
   - Nameservers: Your normal DNS provider (or configure per-subdomain routing)
4. Devices will now resolve `*.chrisesplin.com` to your quiver-pn54 machine

#### Option 2: /etc/hosts (Manual, Per-Device)

On each client device, add to `/etc/hosts`:
```
100.x.x.x app.chrisesplin.com
100.x.x.x api.chrisesplin.com
100.x.x.x dashboard.chrisesplin.com
```

Replace `100.x.x.x` with your Tailscale IP from `tailscale status`.

#### Option 3: Split DNS / Conditional Forwarder

If you have a local DNS server, configure it to resolve `*.chrisesplin.com` to your Tailscale IP.

### HTTPS/TLS Details

- **Automatic provisioning**: First access to a new subdomain triggers Let's Encrypt cert request
- **Auto-renewal**: Certificates renew automatically 30 days before expiration
- **Email**: chris@chrisesplin.com receives renewal notices
- **Staging server** (for testing): Uncomment the `acme_ca` line in Caddyfile

### Firewall & Port Configuration

Caddy needs:
- **Port 80** (HTTP): Redirects to HTTPS
- **Port 443** (HTTPS): Main service port

These are opened automatically via NixOS when you apply the configuration. Check:
```bash
sudo ufw status  # or your firewall tool
```

### Logs & Troubleshooting

**View Caddy logs:**
```bash
sudo journalctl -u caddy -f
sudo tail -f /var/log/caddy/access.log
```

**Test a service:**
```bash
curl -v https://app.chrisesplin.com
```

**Reload configuration without downtime:**
```bash
sudo systemctl reload caddy
```

**Check certificate status:**
```bash
caddy list-modules
sudo /run/current-system/sw/bin/caddy validate --config /etc/caddy/Caddyfile
```

### Public Exposure (Optional - Tailscale Funnel)

To expose a service publicly on the internet:

1. **Enable Tailscale Funnel:**
   ```bash
   tailscale funnel 443
   ```

2. **Configure Caddy** (optional, Funnel works with Caddy automatically):
   - Funnel creates a public URL like `https://quiver-pn54.tail123456.ts.net`
   - Route to your subdomain via DNS or `chrisesplin.com` CNAME

3. **Security note**: Only services you explicitly enable via Funnel are exposed.

### Service Discovery & Health

To help organize services, consider maintaining a service registry in your project:

**Example `services.md`:**
```markdown
# Quiver HQ Services

| Service | Subdomain | Port | Status | Notes |
|---------|-----------|------|--------|-------|
| Frontend App | app | 3000 | Active | Next.js |
| API | api | 3001 | Active | Node.js |
| Dashboard | dashboard | 4000 | Active | React |
```

### Commit Configuration to Git

Once configured and tested:

```bash
git add Caddyfile nixos/caddy.nix nixos/hosts/pn54/configuration.nix
git commit -m "feat: add Caddy reverse proxy for Tailscale network serving

- Enable Caddy on quiver-pn54 with automatic HTTPS
- Support *.chrisesplin.com subdomains for services
- Configure Let's Encrypt with chris@chrisesplin.com
- Open firewall ports 80 and 443
- Services routed to localhost with unique ports"
```

# Quiver HQ Projects Setup Guide

Complete guide for setting up and running all Quiver HQ projects with Caddy reverse proxy.

## 📊 Complete Services Overview

| Project | Location | Tech Stack | Port | Subdomain | Status | Dev Command |
|---------|----------|-----------|------|-----------|--------|------------|
| Foundation-Web | `projects/foundation-web` | Next.js 15, React 19, TypeScript, PostgreSQL | 3000 | app.chrisesplin.com | ✅ Ready | `npm run dev` |
| Therapy Animal Hub | `projects/therapyanimalhub.com` | Next.js, TypeScript, Turso/SQLite, Stripe | 3001 | therapy.chrisesplin.com | ✅ Ready | `npm run dev` |
| Wiley | `projects/wiley` | Next.js, TypeScript, Bun, Firebase | 3600 | wiley.chrisesplin.com | ✅ Ready | `next dev --port 3600` |
| Trikin | `projects/trikin` | Next.js, TypeScript, Cloudflare D1 | 3700 | trikin.chrisesplin.com | ✅ Ready | `next dev --port 3700` |
| K1 | `projects/k1` | Next.js Turbo monorepo, Pnpm, Firebase | 3010* | k1.chrisesplin.com | ⚠️ Dynamic port | `pnpm dev` |

*K1 uses Turbo's dynamic port management; default 3000-3009 range

---

## 🚀 Quick Start (All Services)

### Prerequisites

```bash
# Ensure Git submodules are initialized
cd /home/chris/dev/quiver-hq
git submodule update --init --recursive

# Check which projects are initialized
ls -la projects/
```

### Terminal Setup (Recommended: tmux or multiple terminals)

**Terminal 1: Foundation-Web**
```bash
cd ~/dev/quiver-hq/projects/foundation-web
npm install  # If needed
npm run dev
# Runs on localhost:3000 → app.chrisesplin.com
```

**Terminal 2: Therapy Animal Hub**
```bash
cd ~/dev/quiver-hq/projects/therapyanimalhub.com
npm install  # If needed
npm run dev
# Runs on localhost:3001 → therapy.chrisesplin.com
```

**Terminal 3: Wiley**
```bash
cd ~/dev/quiver-hq/projects/wiley
npm install  # If needed
# Check package.json for dev script, or:
npx next dev --port 3600
# Runs on localhost:3600 → wiley.chrisesplin.com
```

**Terminal 4: Trikin**
```bash
cd ~/dev/quiver-hq/projects/trikin
npm install  # If needed
# Check package.json for dev script, or:
npx next dev --port 3700
# Runs on localhost:3700 → trikin.chrisesplin.com
```

**Terminal 5: K1 (Turbo Monorepo)**
```bash
cd ~/dev/quiver-hq/projects/k1
pnpm install  # If needed (uses pnpm, not npm)
pnpm dev
# Turbo manages ports dynamically
```

### Access Services

From any device on your Tailscale network:

```bash
curl https://app.chrisesplin.com        # Foundation-Web
curl https://therapy.chrisesplin.com    # Therapy Animal Hub
curl https://wiley.chrisesplin.com      # Wiley
curl https://trikin.chrisesplin.com     # Trikin
curl https://k1.chrisesplin.com         # K1
```

---

## 📦 Detailed Project Setup

### 1. Foundation-Web

**Location**: `projects/foundation-web`  
**Port**: 3000  
**Subdomain**: app.chrisesplin.com

**Description**: Multi-tenant B2B SaaS platform with 4 dashboards (Demo, Buyer, Operator, Super Admin). Built with Next.js 15, React 19, TypeScript, PostgreSQL, Auth0, Stream Chat, Inngest, OpenTelemetry.

**Setup**:
```bash
cd projects/foundation-web

# Install dependencies
npm install

# Environment setup (if needed)
cp .env.example .env.local
# Update with your credentials

# Run development server
npm run dev

# Should output: ▲ Next.js 15.x ready
```

**Access**:
```bash
# Via Tailscale
curl https://app.chrisesplin.com

# Inngest (port 8288)
curl https://inngest.chrisesplin.com

# Email preview (port 55420)
curl https://email.chrisesplin.com

# Jaeger tracing (port 16686)
curl https://tracing.chrisesplin.com
```

---

### 2. Therapy Animal Hub

**Location**: `projects/therapyanimalhub.com`  
**Port**: 3001  
**Subdomain**: therapy.chrisesplin.com

**Description**: Mental health therapy animal platform with provider matching, intake forms, Stripe payments, Twilio SMS notifications. Built with Next.js, TypeScript, Turso/SQLite, Firebase, Stripe.

**Setup**:
```bash
cd projects/therapyanimalhub.com

# Install dependencies
npm install

# Environment setup
cp .env.example .env.local
# Add Stripe keys, Firebase config, Twilio credentials

# Run development server (configured for port 3001)
npm run dev

# Server starts on localhost:3001
```

**Key Features**:
- Provider intake forms
- Consumer therapy animal matching
- Stripe payment processing
- Twilio SMS notifications
- Firebase Realtime DB integration

**Access**:
```bash
curl https://therapy.chrisesplin.com
```

**Environment Variables** (see .env.example):
- `STRIPE_PUBLIC_KEY` / `STRIPE_SECRET_KEY`
- `TWILIO_ACCOUNT_SID` / `TWILIO_AUTH_TOKEN`
- `FIREBASE_API_KEY` / Firebase config
- Database connection strings (Turso)

---

### 3. Wiley

**Location**: `projects/wiley`  
**Port**: 3600  
**Subdomain**: wiley.chrisesplin.com

**Description**: AI-powered call management platform that integrates with Netsapiens and AltaWorx for phone system management, spam blocking, and call screening. Built with Next.js, TypeScript, Bun, Firebase, Netsapiens API.

**Setup**:
```bash
cd projects/wiley

# Install dependencies (uses Bun)
bun install
# Or with npm:
npm install

# Environment setup
cp .env.example .env.local
# Add Firebase config, Netsapiens API credentials

# Run development server (explicitly set port 3600)
bunx next dev --port 3600
# Or with npm:
npx next dev --port 3600

# Server starts on localhost:3600
```

**Key Features**:
- AI call management dashboard
- Netsapiens integration for phone system management
- AltaWorx integration for billing and call analytics
- Firebase Firestore + Cloud Functions backend
- Real-time call screening and spam blocking

**Access**:
```bash
curl https://wiley.chrisesplin.com
```

**Environment Variables**:
- `FIREBASE_API_KEY` / Firebase config
- `NETSAPIENS_API_KEY` / `NETSAPIENS_API_URL`
- `ALTAWORX_API_KEY` / `ALTAWORX_API_URL`

---

### 4. Trikin

**Location**: `projects/trikin`  
**Port**: 3700  
**Subdomain**: trikin.chrisesplin.com

**Description**: Property management system with integrations for Oakland Creek, Dwelling Collection, Promove, and GoHighLevel leads. Built with Next.js, TypeScript, Cloudflare D1 database, Workers.

**Setup**:
```bash
cd projects/trikin

# Install dependencies
npm install

# Environment setup
cp .env.example .env.local
# Add Cloudflare D1 connection string, integration API keys

# Run development server (set port to 3700)
npx next dev --port 3700

# Server starts on localhost:3700
```

**Key Features**:
- Property management dashboard
- Integration with Oakland Creek CRM
- Dwelling Collection property data
- Promove lead generation
- GoHighLevel automation
- Cloudflare D1 database backend
- Cloudflare Workers for serverless functions

**Access**:
```bash
curl https://trikin.chrisesplin.com
```

**Environment Variables**:
- `DATABASE_URL` (Cloudflare D1)
- `CLOUDFLARE_ACCOUNT_ID` / `CLOUDFLARE_API_TOKEN`
- Integration API keys for:
  - `OAKLAND_CREEK_API_KEY`
  - `DWELLING_COLLECTION_API_KEY`
  - `PROMOVE_API_KEY`
  - `GOHIGHLEVEL_API_KEY`

---

### 5. K1

**Location**: `projects/k1`  
**Port**: 3000-3009 (Turbo dynamic) → 3010 (Caddyfile)  
**Subdomain**: k1.chrisesplin.com

**Description**: Monorepo template using Turbo and Pnpm with Shadcn/ui components. Built with Next.js, TypeScript, Turbo, Pnpm, Firebase.

**Setup**:
```bash
cd projects/k1

# Install dependencies (uses Pnpm - faster than npm)
pnpm install

# Environment setup (if needed)
cp .env.example .env.local

# Run development server (Turbo manages multiple workspaces)
pnpm dev

# Turbo will start multiple dev servers (check console for port assignments)
# Typically uses ports 3000-3009
```

**Port Management**:
Since K1 uses Turbo's dynamic port management (typically 3000+), and Foundation-Web uses 3000:

**Option 1: Sequential Execution**
```bash
# Terminal 1: foundation-web
cd projects/foundation-web && npm run dev  # Port 3000

# Terminal 2: k1 (after foundation-web is running, or don't run together)
cd projects/k1 && pnpm dev  # Will use alternate port
```

**Option 2: Override Port in K1**
```bash
cd projects/k1
PORT=3010 pnpm dev  # Force port 3010
```

**Option 3: Configure in next.config.js**
Edit `projects/k1/next.config.js`:
```javascript
module.exports = {
  webpackDevMiddleware: (config) => {
    return config;
  },
  // Add port configuration if supported
  server: {
    port: 3010,
  }
}
```

**Key Features**:
- Monorepo template with multiple workspaces
- Shadcn/ui component library integration
- Turbo for fast builds and dev server
- Pnpm for efficient dependency management
- Firebase integration
- TypeScript support across all packages

**Access**:
```bash
curl https://k1.chrisesplin.com
```

---

## 🔄 Managing Multiple Services

### Using tmux (Recommended)

```bash
# Create tmux session
tmux new-session -d -s quiver

# Create windows for each service
tmux new-window -t quiver -n foundation
tmux new-window -t quiver -n therapy
tmux new-window -t quiver -n wiley
tmux new-window -t quiver -n trikin
tmux new-window -t quiver -n k1

# Send commands to each window
tmux send-keys -t quiver:foundation "cd ~/dev/quiver-hq/projects/foundation-web && npm run dev" Enter
tmux send-keys -t quiver:therapy "cd ~/dev/quiver-hq/projects/therapyanimalhub.com && npm run dev" Enter
tmux send-keys -t quiver:wiley "cd ~/dev/quiver-hq/projects/wiley && npx next dev --port 3600" Enter
tmux send-keys -t quiver:trikin "cd ~/dev/quiver-hq/projects/trikin && npx next dev --port 3700" Enter
tmux send-keys -t quiver:k1 "cd ~/dev/quiver-hq/projects/k1 && pnpm dev" Enter

# Attach to session
tmux attach -t quiver

# Switch between windows with: Ctrl+B, then [0-5]
```

### Using Docker Compose (Alternative)

Create `docker-compose.yml` in repository root:

```yaml
version: '3.8'

services:
  foundation-web:
    build: ./projects/foundation-web
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
    volumes:
      - ./projects/foundation-web:/app

  therapy:
    build: ./projects/therapyanimalhub.com
    ports:
      - "3001:3001"
    environment:
      - NODE_ENV=development
      - PORT=3001

  wiley:
    build: ./projects/wiley
    ports:
      - "3600:3600"
    environment:
      - NODE_ENV=development
      - PORT=3600

  trikin:
    build: ./projects/trikin
    ports:
      - "3700:3700"
    environment:
      - NODE_ENV=development
      - PORT=3700

  k1:
    build: ./projects/k1
    ports:
      - "3010:3010"
    environment:
      - NODE_ENV=development
      - PORT=3010
```

Run with:
```bash
docker-compose up -d
```

---

## 🔐 Environment Variables & Secrets

Each project may require specific environment variables. Setup process:

1. Copy `.env.example` to `.env.local` in each project:
   ```bash
   cp projects/PROJECTNAME/.env.example projects/PROJECTNAME/.env.local
   ```

2. Update values with your credentials:
   - API keys (Stripe, Firebase, etc.)
   - Database connection strings
   - Service integrations (Netsapiens, Twilio, etc.)
   - OAuth credentials (Auth0, etc.)

3. For secure credential management, use:
   ```bash
   # Via 1Password (if configured)
   ./quiver-secrets hydrate ./projects/PROJECTNAME

   # Or manually set environment variables
   export STRIPE_SECRET_KEY=sk_test_...
   npm run dev
   ```

---

## 📝 Caddyfile Configuration

All services are configured in `/home/chris/dev/quiver-hq/Caddyfile`:

```caddy
# Existing services
app.chrisesplin.com {
  reverse_proxy localhost:3000
}

# New project services
therapy.chrisesplin.com {
  reverse_proxy localhost:3001
}

wiley.chrisesplin.com {
  reverse_proxy localhost:3600
}

trikin.chrisesplin.com {
  reverse_proxy localhost:3700
}

k1.chrisesplin.com {
  reverse_proxy localhost:3010
}
```

After updating Caddyfile:
```bash
sudo systemctl reload caddy
```

---

## ✅ Verification Checklist

- [ ] All projects have git submodules initialized: `git submodule update --init --recursive`
- [ ] Dependencies installed for each project: `npm/pnpm install`
- [ ] Environment files configured: `.env.local` with API keys
- [ ] Development servers running on correct ports
- [ ] Caddy configuration updated and reloaded
- [ ] DNS configured (Tailscale Split DNS or /etc/hosts)
- [ ] Services accessible via HTTPS from Tailscale network
- [ ] Certificates provisioned by Let's Encrypt
- [ ] Logs monitored: `sudo journalctl -u caddy -f`

---

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Find what's using the port
lsof -i :3000
sudo netstat -tulpn | grep :3000

# Kill the process
kill -9 PID

# Or find and stop the service
ps aux | grep "npm run dev"
```

### Dependencies Installation Issues

```bash
# Clear node_modules and reinstall
cd projects/PROJECTNAME
rm -rf node_modules package-lock.json
npm install

# Or for K1 (uses pnpm)
rm -rf node_modules
pnpm install
```

### Missing Environment Variables

```bash
# Check what variables are required
grep -r "process.env" projects/PROJECTNAME/src | head -20

# or check .env.example
cat projects/PROJECTNAME/.env.example
```

### Caddy Can't Resolve Subdomains

See `CADDY_DNS_SETUP.md` for DNS configuration options.

### SSL Certificate Issues

```bash
# Validate Caddyfile syntax
caddy validate --config /etc/caddy/Caddyfile

# Check certificate status
ls -la ~/.local/share/caddy/certificates/

# Monitor ACME certificate provisioning
sudo journalctl -u caddy -f | grep acme
```

---

## 📚 Additional Resources

- [Project Configurations](./README.md#caddy-reverse-proxy-setup)
- [DNS & Tailscale Setup](./CADDY_DNS_SETUP.md)
- [Caddy Documentation](https://caddyserver.com/docs/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Tailscale Documentation](https://tailscale.com/kb/)

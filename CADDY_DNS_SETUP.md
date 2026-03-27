# Caddy + Tailscale DNS Setup Guide

This guide covers how to configure DNS so that `*.chrisesplin.com` subdomains resolve to your quiver-pn54 machine within your Tailscale network.

## Prerequisites

- Caddy running on quiver-pn54 (via `sudo nixos-rebuild switch --flake .#quiver-pn54`)
- Tailscale installed and authenticated on quiver-pn54 and client devices
- A domain name (chrisesplin.com) pointed to your DNS provider
- Admin access to [Tailscale Admin Console](https://login.tailscale.com/admin)

## Quick Reference: quiver-pn54 Tailscale Info

First, get your Tailscale IP on quiver-pn54:

```bash
tailscale status
```

Output example:
```
     State  URL                              Machines
     -----  ---                              --------
  Stopped  https://login.tailscale.com/?key=...
  Running
  100.64.0.1/32  quiver-pn54.ts.net  chris@...
```

In this example:
- **Tailscale IP**: `100.64.0.1`
- **MagicDNS name**: `quiver-pn54.ts.net`

---

## Option 1: Tailscale Split DNS (Recommended)

This method uses Tailscale's DNS to resolve `*.chrisesplin.com` to your quiver-pn54.

### Setup Steps

1. **Get your Tailscale IP:**
   ```bash
   tailscale status | grep quiver-pn54
   ```
   Note the IP (e.g., `100.64.0.1`)

2. **Visit Tailscale Admin Console:**
   - Go to https://login.tailscale.com/admin/dns
   - Scroll to **"Nameservers"** section

3. **Add Split DNS Rule:**
   - Click **"Add nameserver"** or **"Custom nameservers"**
   - **Domain**: `chrisesplin.com` (or `*.chrisesplin.com`)
   - **Nameservers**: 
     - Enter your local DNS provider's nameservers (or use Cloudflare: `1.1.1.1`, `1.0.0.1`)
     - **Alternative**: Leave blank and use Tailscale's default resolution

4. **Alternative: Route to Tailscale IP directly**
   - In some Tailscale installations, you can specify:
     - **Domain**: `chrisesplin.com`
     - **Resolver**: `100.64.0.1` (your quiver-pn54 IP)

5. **Verify on client:**
   ```bash
   nslookup app.chrisesplin.com
   # Should resolve to 100.64.0.1
   ```

### Pros & Cons

✅ **Pros:**
- Works across all devices on your tailnet automatically
- No per-device configuration needed
- Elegant and scalable

❌ **Cons:**
- Requires Tailscale MagicDNS enabled
- Requires admin access to Tailscale console
- Changes take ~5-10 seconds to propagate

---

## Option 2: Tailscale MagicDNS (Easiest)

This method uses Tailscale's built-in MagicDNS to automatically resolve all tailnet machines.

### Setup Steps

1. **Verify MagicDNS is enabled:**
   ```bash
   tailscale status
   ```
   Look for `*.ts.net` in the output

2. **Access quiver-pn54.ts.net directly:**
   ```bash
   curl https://quiver-pn54.ts.net/  # May fail if no service on root
   curl https://app.chrisesplin.com  # Still needs DNS routing
   ```

3. **Set up DNS via /etc/hosts (for testing):**
   ```bash
   echo "100.x.x.x app.chrisesplin.com" | sudo tee -a /etc/hosts
   ```

### Pros & Cons

✅ **Pros:**
- Simple for testing and quick verification
- No additional DNS configuration needed
- Works immediately after adding to /etc/hosts

❌ **Cons:**
- Must configure on each client device
- Not scalable for multiple clients
- Requires manual maintenance of /etc/hosts

---

## Option 3: Manual /etc/hosts Configuration

For testing or small deployments, edit `/etc/hosts` on each client.

### Setup Steps

1. **Get quiver-pn54 Tailscale IP:**
   ```bash
   tailscale status
   # Note the IP, e.g., 100.64.0.1
   ```

2. **Edit /etc/hosts on your client device:**
   
   **Linux/macOS:**
   ```bash
   sudo nano /etc/hosts
   
   # Add these lines:
   100.64.0.1 app.chrisesplin.com
   100.64.0.1 api.chrisesplin.com
   100.64.0.1 dashboard.chrisesplin.com
   ```

   **Windows (PowerShell as Admin):**
   ```powershell
   Add-Content -Path "C:\Windows\System32\drivers\etc\hosts" -Value "100.64.0.1`tapp.chrisesplin.com"
   ```

3. **Verify:**
   ```bash
   nslookup app.chrisesplin.com
   # Should resolve to 100.64.0.1
   ```

### Pros & Cons

✅ **Pros:**
- Works on any OS
- No Tailscale console access needed
- Simple for quick testing

❌ **Cons:**
- Manual configuration on every device
- Not scalable
- Requires updating for new services

---

## Option 4: Local DNS Server (Advanced)

If you have a local DNS server (Pi-hole, dnsmasq, etc.), configure it.

### Setup Steps (dnsmasq example)

1. **SSH into your DNS server**

2. **Edit dnsmasq config:**
   ```bash
   sudo nano /etc/dnsmasq.conf
   
   # Add:
   address=/chrisesplin.com/100.64.0.1
   ```

3. **Restart dnsmasq:**
   ```bash
   sudo systemctl restart dnsmasq
   ```

4. **Point clients to this DNS server** (usually via DHCP or manual DNS settings)

### Pros & Cons

✅ **Pros:**
- Centralized management
- Works for entire home network
- Very flexible and powerful

❌ **Cons:**
- Requires maintaining a DNS server
- More complex setup
- Requires network admin access

---

## Verifying Your DNS Configuration

### Test DNS Resolution

```bash
# Should resolve to your quiver-pn54 Tailscale IP (e.g., 100.64.0.1)
nslookup app.chrisesplin.com
dig app.chrisesplin.com
host app.chrisesplin.com
```

### Test HTTPS Connection

```bash
# From a device on your Tailscale network
curl -v https://app.chrisesplin.com
# Should return 200 OK with Caddy response

# Check certificate
openssl s_client -connect app.chrisesplin.com:443
# Should show valid Let's Encrypt certificate for *.chrisesplin.com
```

### Verify Caddy is Listening

On quiver-pn54:
```bash
sudo netstat -tulpn | grep caddy
# Should show listening on 0.0.0.0:80 and 0.0.0.0:443

sudo ss -tulpn | grep caddy
# Alternative command
```

---

## Troubleshooting

### "Name or service not known" Error

**Problem**: DNS resolution fails

**Solutions**:
1. Check Tailscale is running: `tailscale status`
2. Verify you're on the tailnet: `tailscale whois 100.64.0.1`
3. Check DNS setting:
   ```bash
   cat /etc/resolv.conf  # Linux/macOS
   ipconfig /all  # Windows
   ```
4. Try flushing DNS cache:
   ```bash
   sudo systemd-resolve --flush-caches  # systemd
   sudo dscacheutil -flushcache  # macOS
   ipconfig /flushdns  # Windows
   ```

### "Connection refused" Error

**Problem**: DNS resolves but Caddy doesn't respond

**Solutions**:
1. Verify Caddy is running on quiver-pn54:
   ```bash
   sudo systemctl status caddy
   sudo systemctl restart caddy
   ```
2. Check firewall:
   ```bash
   sudo ufw status
   # Ports 80 and 443 should be open
   ```
3. Verify service is running on backend port:
   ```bash
   netstat -tulpn | grep :3000  # If backend on port 3000
   ```
4. Check Caddy logs:
   ```bash
   sudo journalctl -u caddy -f
   ```

### "Certificate error" on First Access

**Problem**: Browser shows "self-signed certificate" or "certificate not yet valid"

**Solutions**:
1. This is normal on first access - Let's Encrypt is provisioning the cert
2. Wait 30-60 seconds and try again
3. Check Caddy logs for ACME activity:
   ```bash
   sudo journalctl -u caddy -f | grep -i acme
   ```
4. Verify email is correct in Caddyfile:
   ```bash
   grep "email" /etc/caddy/Caddyfile
   ```
5. If still failing, check Let's Encrypt rate limits (50 certs per domain per week)

### "Timeout" or "No route to host"

**Problem**: Can't reach quiver-pn54

**Solutions**:
1. Verify quiver-pn54 is on Tailscale:
   ```bash
   tailscale status
   # Should list quiver-pn54 as "Running"
   ```
2. Try pinging quiver-pn54:
   ```bash
   ping 100.64.0.1
   ping quiver-pn54.ts.net
   ```
3. Check firewall on quiver-pn54:
   ```bash
   sudo ufw status
   sudo firewall-cmd --list-all  # firewalld
   ```
4. Verify Caddy is listening on all interfaces:
   ```bash
   sudo ss -tulpn | grep :443
   # Should show 0.0.0.0:443, not just 127.0.0.1:443
   ```

---

## Firewall Configuration Details

### Opening Ports on quiver-pn54

The NixOS Caddy module automatically opens ports 80 and 443. If you're using a firewall, verify:

```bash
# Check if UFW is running
sudo ufw status

# If running, verify rules:
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw reload

# Or with firewalld:
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --reload
```

---

## SSL/TLS Certificate Management

### Automatic Renewal

Caddy automatically renews certificates 30 days before expiration. Monitor via logs:

```bash
sudo journalctl -u caddy -f | grep -i cert
```

### Force Renewal (for testing)

```bash
# Uncomment staging server in Caddyfile temporarily
# Then restart
sudo systemctl restart caddy
```

### Certificate Locations

Let's Encrypt certificates are stored at:
```bash
ls ~/.local/share/caddy/certificates/acme/acme-v02.api.letsencrypt.org/
```

### Wildcard Certificate Considerations

- Current setup requires individual certs for each subdomain
- To use a wildcard (`*.chrisesplin.com`), require DNS validation
- Contact Caddy documentation for DNS provider integration

---

## Next Steps

1. **Test your setup:**
   ```bash
   curl -v https://app.chrisesplin.com
   ```

2. **Document your services in the registry:**
   Create or update a `services.md` file with all running services

3. **Set up automatic backups** of your Caddyfile and service configs

4. **Monitor logs regularly** for errors:
   ```bash
   sudo journalctl -u caddy -f
   ```

---

## Additional Resources

- [Caddy Documentation](https://caddyserver.com/docs/)
- [Tailscale DNS Documentation](https://tailscale.com/kb/1054/dns/)
- [Tailscale Split DNS Guide](https://tailscale.com/kb/1196/custom-dns/)
- [Let's Encrypt Rate Limits](https://letsencrypt.org/docs/rate-limits/)

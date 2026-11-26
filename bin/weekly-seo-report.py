#!/usr/bin/env python3
"""Weekly SEO & Google Search Console email report for Quiver web properties.

Uses:
  - ~/.local/bin/gsc (KLIXPERT-io/gsc-cli) for Search Console analytics & sitemaps
  - Live HTTP checks for redirects, sitemap URLs, and self-referencing canonicals
  - ~/.local/bin/gws for sending the email via Gmail API

Usage:
  weekly-seo-report.py [--dry-run] [--to email@example.com]
"""

import argparse
import base64
import concurrent.futures
import datetime
import email.mime.multipart
import email.mime.text
import html
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request

GSC_BIN = os.path.expanduser("~/.local/bin/gsc")
GWS_BIN = os.path.expanduser("~/.local/bin/gws")
DEFAULT_TO = "christopher.esplin@gmail.com"

HEALTH_DOMAINS = [
    "chrisesplin.com",
    "utahdevco.com",
    "calligraphy.org",
    "melissaesplin.com",
    "quiverphotos.com",
    "therapyanimalhub.com",
    "trikin.co",
]

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)


def run_gsc(args):
    try:
        proc = subprocess.run(
            [GSC_BIN, *args, "--output", "json"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if proc.returncode != 0:
            return None, (proc.stderr or proc.stdout).strip()
        return json.loads(proc.stdout), None
    except Exception as exc:
        return None, str(exc)


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


_OPENER = urllib.request.build_opener(_NoRedirect)


def _check_url(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        resp = _OPENER.open(req, timeout=8)
        body = resp.read(30000).decode("utf-8", errors="ignore")
        m = re.search(
            r'<link[^>]+rel=["\']canonical["\'][^>]*href=["\']([^"\']+)["\']',
            body,
            re.I,
        )
        if not m:
            m = re.search(
                r'<link[^>]+href=["\']([^"\']+)["\'][^>]*rel=["\']canonical["\']',
                body,
                re.I,
            )
        canon = m.group(1) if m else None
        return (url, resp.status, None, canon)
    except urllib.error.HTTPError as e:
        return (url, e.code, e.headers.get("Location"), None)
    except Exception as e:
        return (url, "ERR", str(e), None)


def audit_site_health(domain):
    issues = []
    sm_url = f"https://www.{domain}/sitemap.xml"
    try:
        req = urllib.request.Request(sm_url, headers={"User-Agent": UA})
        xml = urllib.request.urlopen(req, timeout=10).read().decode("utf-8", errors="ignore")
        urls = re.findall(r"<loc>(.*?)</loc>", xml)
    except Exception as e:
        return {"domain": domain, "checked": 0, "total": 0, "issues": [f"Sitemap fetch failed: {e}"]}

    sample = urls[:30]
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        results = list(ex.map(_check_url, sample))

    for u, code, loc, canon in results:
        if code != 200:
            issues.append(f"{u} -> HTTP {code}" + (f" ({loc})" if loc else ""))
        elif canon and canon.rstrip("/") != u.rstrip("/"):
            issues.append(f"{u} -> canonical points to {canon}")

    return {"domain": domain, "checked": len(sample), "total": len(urls), "issues": issues}


def fmt_delta(curr, prev, is_pct=False, invert=False):
    if prev is None or curr is None:
        return ""
    diff = curr - prev
    if abs(diff) < 1e-6:
        return " (0)"
    sign = "+" if diff > 0 else ""
    if is_pct:
        return f" ({sign}{diff * 100:.1f}pp)"
    if invert:
        return f" ({sign}{diff:.1f})"
    if prev:
        pct = (diff / prev) * 100
        return f" ({sign}{pct:.0f}%)"
    return f" ({sign}{diff:.0f})"


def collect_gsc_data():
    sites_resp, err = run_gsc(["sites", "list"])
    if err or not sites_resp:
        return None, err or "Failed to list GSC sites"

    raw_sites = sites_resp.get("data", [])
    if isinstance(raw_sites, dict):
        raw_sites = raw_sites.get("sites", []) or raw_sites.get("siteEntry", [])

    # Prefer sc-domain: properties, sorted alphabetically
    props = []
    for s in raw_sites:
        url = s.get("siteUrl") or s.get("site_url") or s.get("url")
        if url and url.startswith("sc-domain:"):
            props.append(url)
    props.sort()

    report = []
    for prop in props:
        ov, ov_err = run_gsc(
            ["analytics", "overview", prop, "--range", "last-7d", "--compare", "previous-period"]
        )
        queries, _ = run_gsc(
            ["analytics", "query", prop, "--dimensions", "query", "--range", "last-7d", "--limit", "5"]
        )
        pages, _ = run_gsc(
            ["analytics", "query", prop, "--dimensions", "page", "--range", "last-7d", "--limit", "5"]
        )
        sitemaps, _ = run_gsc(["sitemaps", "list", prop])

        report.append(
            {
                "property": prop,
                "overview": ov.get("data") if ov else None,
                "overview_err": ov_err,
                "queries": (queries or {}).get("data"),
                "pages": (pages or {}).get("data"),
                "sitemaps": (sitemaps or {}).get("data"),
            }
        )
    return report, None


def extract_rows(data):
    if not data:
        return []
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return data.get("rows") or data.get("sitemaps") or []
    return []


def build_report():
    today = datetime.date.today().isoformat()
    gsc_data, gsc_err = collect_gsc_data()

    with concurrent.futures.ThreadPoolExecutor(max_workers=7) as ex:
        health = list(ex.map(audit_site_health, HEALTH_DOMAINS))

    text_lines = [f"Weekly SEO & Search Console Report — {today}", "=" * 56, ""]
    html_parts = [
        f"<h2>Weekly SEO &amp; Search Console Report ({html.escape(today)})</h2>",
    ]

    # 1. GSC Summary
    text_lines.append("1. GOOGLE SEARCH CONSOLE (LAST 7 DAYS vs PREVIOUS 7 DAYS)")
    text_lines.append("-" * 56)
    html_parts.append("<h3>1. Google Search Console (Last 7 Days vs Previous 7 Days)</h3>")

    if gsc_err:
        msg = f"GSC CLI unavailable (run `gsc auth login` to authenticate): {gsc_err}"
        text_lines.append(msg)
        html_parts.append(f"<p style='color:#b45309'><strong>Note:</strong> {html.escape(msg)}</p>")
    elif not gsc_data:
        text_lines.append("No sc-domain properties found.")
        html_parts.append("<p>No sc-domain properties found.</p>")
    else:
        html_parts.append(
            "<table border='1' cellpadding='6' cellspacing='0' style='border-collapse:collapse;font-size:13px'>"
            "<tr style='background:#f3f4f6'><th>Property</th><th>Clicks</th><th>Impressions</th><th>CTR</th><th>Avg Pos</th><th>Sitemaps</th></tr>"
        )
        for item in gsc_data:
            prop = item["property"].replace("sc-domain:", "")
            ov = item["overview"] or {}
            curr = ov.get("current") if isinstance(ov.get("current"), dict) else ov
            prev = ov.get("previous") if isinstance(ov.get("previous"), dict) else {}

            clicks = curr.get("clicks", 0)
            impr = curr.get("impressions", 0)
            ctr = curr.get("ctr", 0.0)
            pos = curr.get("position", 0.0)

            c_str = f"{clicks:.0f}{fmt_delta(clicks, prev.get('clicks'))}"
            i_str = f"{impr:.0f}{fmt_delta(impr, prev.get('impressions'))}"
            ctr_str = f"{ctr*100:.1f}%{fmt_delta(ctr, prev.get('ctr'), is_pct=True)}"
            pos_str = f"{pos:.1f}{fmt_delta(pos, prev.get('position'), invert=True)}" if pos else "—"

            sms = extract_rows(item["sitemaps"])
            sm_errs = sum(int(s.get("errors", 0) or 0) for s in sms if isinstance(s, dict))
            sm_warns = sum(int(s.get("warnings", 0) or 0) for s in sms if isinstance(s, dict))
            sm_str = f"{len(sms)} ok" if (sm_errs == 0 and sm_warns == 0) else f"{sm_errs} err, {sm_warns} warn"

            text_lines.append(f"- {prop}: {c_str} clicks | {i_str} impr | CTR {ctr_str} | Pos {pos_str} | Sitemaps: {sm_str}")
            html_parts.append(
                f"<tr><td><strong>{html.escape(prop)}</strong></td>"
                f"<td>{html.escape(c_str)}</td><td>{html.escape(i_str)}</td>"
                f"<td>{html.escape(ctr_str)}</td><td>{html.escape(pos_str)}</td>"
                f"<td>{html.escape(sm_str)}</td></tr>"
            )

            q_rows = extract_rows(item["queries"])[:3]
            if q_rows:
                top_q = ", ".join(
                    f"{(r.get('keys') or ['?'])[0]} ({r.get('clicks', 0):.0f}c/{r.get('impressions', 0):.0f}i)"
                    for r in q_rows
                )
                text_lines.append(f"    Top queries: {top_q}")
        html_parts.append("</table>")

    # 2. Live Technical SEO Health
    text_lines.extend(["", "2. LIVE SITEMAP & CANONICAL HEALTH CHECK", "-" * 56])
    html_parts.append("<h3>2. Live Sitemap &amp; Canonical Health Check</h3><ul>")
    for h in health:
        dom = h["domain"]
        if not h["issues"]:
            line = f"OK  {dom} ({h['checked']}/{h['total']} sitemap URLs checked — all 200 with self-referencing canonicals)"
            text_lines.append(line)
            html_parts.append(
                f"<li><strong style='color:#15803d'>OK</strong> {html.escape(dom)} "
                f"({h['checked']}/{h['total']} sitemap URLs clean)</li>"
            )
        else:
            text_lines.append(f"WARN {dom} ({len(h['issues'])} issues in {h['checked']} checked):")
            html_parts.append(
                f"<li><strong style='color:#b91c1c'>WARN</strong> {html.escape(dom)} "
                f"({len(h['issues'])} issues):<ul>"
            )
            for iss in h["issues"][:10]:
                text_lines.append(f"    - {iss}")
                html_parts.append(f"<li><code>{html.escape(iss)}</code></li>")
            html_parts.append("</ul></li>")
    html_parts.append("</ul>")

    footer_text = [
        "",
        "-" * 56,
        "ABOUT THIS REPORT & HOW TO DEACTIVATE IT",
        "Generated by: /Users/christopher/dev/quiver-hq/bin/weekly-seo-report.py",
        "Data sources: ~/.local/bin/gsc (Google Search Console API) + live HTTP sitemap/canonical checks",
        "Sent via:     ~/.local/bin/gws (Gmail API) from/to christopher.esplin@gmail.com",
        "Schedule:     macOS launchd (com.quiver.weekly-seo-report) — Mondays at 8:00 AM",
        "Plist:        ~/Library/LaunchAgents/com.quiver.weekly-seo-report.plist",
        "Logs:         ~/Library/Logs/weekly-seo-report.log",
        "",
        "Run manually:",
        "  python3 /Users/christopher/dev/quiver-hq/bin/weekly-seo-report.py",
        "",
        "Deactivate (stop future emails):",
        "  launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.quiver.weekly-seo-report.plist && rm ~/Library/LaunchAgents/com.quiver.weekly-seo-report.plist",
    ]
    text_lines.extend(footer_text)

    html_parts.append(
        "<hr style='margin-top:24px;border:none;border-top:1px solid #e5e7eb'/>"
        "<div style='font-size:12px;color:#4b5563;line-height:1.5'>"
        "<strong>About this report &amp; how to deactivate it</strong><br/>"
        "<strong>Script:</strong> <code>/Users/christopher/dev/quiver-hq/bin/weekly-seo-report.py</code><br/>"
        "<strong>Data sources:</strong> <code>~/.local/bin/gsc</code> (Google Search Console API) + live HTTP sitemap/canonical checks<br/>"
        "<strong>Sent via:</strong> <code>~/.local/bin/gws</code> (Gmail API) on your Mac<br/>"
        "<strong>Schedule:</strong> macOS <code>launchd</code> (<code>com.quiver.weekly-seo-report</code>) — Mondays at 8:00 AM "
        "(plist: <code>~/Library/LaunchAgents/com.quiver.weekly-seo-report.plist</code>, log: <code>~/Library/Logs/weekly-seo-report.log</code>)<br/><br/>"
        "<strong>Run manually:</strong><br/>"
        "<code>python3 /Users/christopher/dev/quiver-hq/bin/weekly-seo-report.py</code><br/><br/>"
        "<strong>Deactivate (stop future emails):</strong><br/>"
        "<code>launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.quiver.weekly-seo-report.plist &amp;&amp; rm ~/Library/LaunchAgents/com.quiver.weekly-seo-report.plist</code>"
        "</div>"
    )

    subject = f"Weekly SEO & GSC Report — {today}"
    return subject, "\n".join(text_lines), "\n".join(html_parts)


def send_email(to_addr, subject, text_body, html_body):
    msg = email.mime.multipart.MIMEMultipart("alternative")
    msg["To"] = to_addr
    msg["From"] = to_addr
    msg["Subject"] = subject
    msg.attach(email.mime.text.MIMEText(text_body, "plain", "utf-8"))
    msg.attach(email.mime.text.MIMEText(html_body, "html", "utf-8"))

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("ascii")
    proc = subprocess.run(
        [
            GWS_BIN,
            "gmail",
            "users",
            "messages",
            "send",
            "--params",
            json.dumps({"userId": "me"}),
            "--json",
            json.dumps({"raw": raw}),
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"gws send failed: {proc.stderr or proc.stdout}")
    return proc.stdout


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--to", default=DEFAULT_TO)
    args = parser.parse_args()

    subject, text_body, html_body = build_report()
    if args.dry_run:
        print("SUBJECT:", subject)
        print(text_body)
        return

    out = send_email(args.to, subject, text_body, html_body)
    print("Sent:", out.strip())


if __name__ == "__main__":
    main()

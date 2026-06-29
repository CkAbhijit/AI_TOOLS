#!/usr/bin/env python3
"""
===================================================================================
                       SSL-ARMOR v2.5 (BUG BOUNTY ULTIMATE)
===================================================================================
Features: HSTS, SSLv3 (POODLE), TLS 1.0 CBC (BEAST), 3DES (Sweet32), Cookies,
          + Subdomain Takeover Detection & CORS Misconfiguration Auditor.
===================================================================================
"""

import socket
import ssl
import sys
import urllib.parse
from datetime import datetime
import requests
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()

BANNER = """
[bold red] ██████╗███████╗██╗         █████╗ ██████╗ ███╗   ███╗ ██████╗ ██████╗ 
██╔════╝██╔════╝██║        ██╔══██╗██╔══██╗████╗ ████║██╔═══██╗██╔══██╗
╚█████╗ ███████╗██║  █████╗███████║██████╔╝██╔████╔██║██║   ██║██████╔╝
 ╚═══██╗╚════██║██║  ╚════╝██╔══██║██╔══██╗██║╚██╔╝██║██║   ██║██╔══██╗
██████╔╝███████║███████╗   ██║  ██║██║  ██║██║ ╚═╝ ██║╚██████╔╝██║  ██║
╚═════╝ ╚══════╝╚══════╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝[/bold red]
                [bold yellow]🧬 Version 2.5 (Elite Bug Bounty Edition) 🧬[/bold yellow]
      [bold cyan]💎 SSL/TLS, Transport, CORS Misconfiguration & Subdomain Takeover 💎[/bold cyan]
"""

# Common signatures for third-party hosting fingerprints (Subdomain Takeover)
TAKEOVER_FINGERPRINTS = {
    "github.io": "There isn't a GitHub Pages site here",
    "cloudfront.net": "Bad Gateway: Forbidden",
    "herokuapp.com": "no such app",
    "wordpress.com": "Do you want to register",
    "bitbucket.io": "Repository not found",
    "squarespace.com": "Squarespace - Page Not Found",
    "amazonaws.com": "The specified bucket does not exist",
    "pantheonsite.io": "The Pantheon Site you are looking for",
}


def show_banner():
    console.print(BANNER)


def extract_target_metadata(url_string):
    url_string = url_string.strip()
    if not url_string.startswith("http://") and not url_string.startswith(
        "https://"
    ):
        url_string = "https://" + url_string
    parsed_obj = urllib.parse.urlparse(url_string)
    host_target = parsed_obj.hostname
    port_target = parsed_obj.port
    if not port_target:
        port_target = 443 if parsed_obj.scheme == "https" else 80
    return host_target, port_target, url_string


def audit_http_transport(clean_url):
    findings = {
        "hsts_absent": True,
        "hsts_raw_data": None,
        "improper_max_age": False,
        "improper_max_age_val": None,
        "unprotected_cookies": [],
        "ssl_striping_viable": False,
        "cors_vulnerable": False,
        "cors_origin_allowed": None,
    }

    headers_payload = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:115.0) Gecko/20100101 Firefox/115.0",
        "Origin": "https://evil-attacker.com",
    }

    # Redirection Check
    try:
        insecure_variant = clean_url.replace("https://", "http://")
        http_response = requests.get(
            insecure_variant,
            headers=headers_payload,
            allow_redirects=False,
            timeout=5,
            verify=False
        )
        if http_response.status_code not in [301, 302, 303, 307, 308]:
            findings["ssl_striping_viable"] = True
    except Exception:
        findings["ssl_striping_viable"] = True

    # HSTS, Cookies, and CORS Check
    try:
        secure_response = requests.get(
            clean_url, headers=headers_payload, timeout=5, verify=False
        )
        resp_headers = secure_response.headers

        # HSTS Audit
        if "Strict-Transport-Security" in resp_headers:
            findings["hsts_absent"] = False
            hsts_header_content = resp_headers["Strict-Transport-Security"]
            findings["hsts_raw_data"] = hsts_header_content
            if "max-age" in hsts_header_content.lower():
                parts = hsts_header_content.split(";")
                for part in parts:
                    if "max-age" in part.lower():
                        try:
                            val = int(part.split("=")[1].strip())
                            if val < 31536000:
                                findings["improper_max_age"] = True
                                findings["improper_max_age_val"] = val
                        except Exception:
                            pass

        # CORS Audit
        aca_origin = resp_headers.get("Access-Control-Allow-Origin", "")
        aca_creds = resp_headers.get("Access-Control-Allow-Credentials", "")
        if aca_origin == "*" or aca_origin == "https://evil-attacker.com":
            findings["cors_vulnerable"] = True
            findings["cors_origin_allowed"] = aca_origin

        # Cookies Audit
        for cookie in secure_response.cookies:
            if not cookie.secure:
                findings["unprotected_cookies"].append(cookie.name)
    except Exception:
        pass

    return findings


def audit_subdomain_takeover(host):
    """Checks DNS CNAME and HTTP responses for potential third-party takeovers."""
    status = {"takeover_possible": False, "provider": None, "cname": None}
    try:
        # Get CNAME info
        try:
            cname_target = socket.gethostbyname_ex(host)[0]
            if cname_target != host:
                status["cname"] = cname_target
        except:
            pass

        # Check HTTP response body for dead signatures
        response = requests.get(f"https://{host}", timeout=5, verify=False)
        html_content = response.text

        for provider, signature in TAKEOVER_FINGERPRINTS.items():
            if signature in html_content:
                status["takeover_possible"] = True
                status["provider"] = provider
                break
    except Exception:
        pass
    return status


def audit_tls_cryptography(host, port):
    crypt_findings = {
        "is_tls_accessible": False,
        "poodle_vulnerable": "Safe",
        "beast_vulnerable": "Safe",
        "sweet32_vulnerable": "Safe",
    }
    try:
        tls_context = ssl.create_default_context()
        tls_context.check_hostname = False
        tls_context.verify_mode = ssl.CERT_NONE
        with socket.create_connection((host, port), timeout=4) as network_socket:
            with tls_context.wrap_socket(
                network_socket, server_hostname=host
            ) as secure_socket:
                crypt_findings["is_tls_accessible"] = True
    except Exception:
        pass

    # POODLE Simulation
    try:
        poodle_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
        poodle_context.options |= (
            ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1 | ssl.OP_NO_TLSv1_2 | ssl.OP_NO_TLSv1_3
        )
        poodle_context.check_hostname = False
        poodle_context.verify_mode = ssl.CERT_NONE
        with socket.create_connection((host, port), timeout=3) as socket_p:
            with poodle_context.wrap_socket(
                socket_p, server_hostname=host
            ) as secure_p:
                crypt_findings["poodle_vulnerable"] = (
                    "VULNERABLE (SSLv3 Handshake Accepted)"
                )
    except Exception:
        crypt_findings["poodle_vulnerable"] = "Safe"

    # BEAST Simulation
    try:
        beast_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        beast_context.set_ciphers("AES128-SHA:DES-CBC3-SHA")
        beast_context.check_hostname = False
        beast_context.verify_mode = ssl.CERT_NONE
        with socket.create_connection((host, port), timeout=3) as socket_b:
            with beast_context.wrap_socket(
                socket_b, server_hostname=host
            ) as secure_b:
                crypt_findings["beast_vulnerable"] = (
                    "VULNERABLE (TLSv1.0 CBC Ciphers Accepted)"
                )
    except Exception:
        crypt_findings["beast_vulnerable"] = "Safe"

    # Sweet32 Simulation
    try:
        sweet_context = ssl.create_default_context()
        sweet_context.set_ciphers("3DES:DES")
        sweet_context.check_hostname = False
        sweet_context.verify_mode = ssl.CERT_NONE
        with socket.create_connection((host, port), timeout=3) as socket_s:
            with sweet_context.wrap_socket(
                socket_s, server_hostname=host
            ) as secure_s:
                crypt_findings["sweet32_vulnerable"] = (
                    "VULNERABLE (3DES Ciphers Accepted)"
                )
    except Exception:
        crypt_findings["sweet32_vulnerable"] = "Safe"

    return crypt_findings


def generate_high_quality_report(host, target_url, http_info, tls_info, takeover_info):
    report_content = f"""# Advanced Security Assessment Report
**Target Host:** `{host}`
**Target URL:** {target_url}
**Scanner Engine:** SSL-ARMOR v2.5 (Ultimate Pro Edition)
**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---
"""
    counter = 1
    if takeover_info["takeover_possible"]:
        report_content += f"""## Bug #{counter}: High Risk - Subdomain Takeover Detected
- **Severity:** High (CVSS v3: 8.2)
- **CWE-ID:** CWE-404
- **Provider Identified:** {takeover_info['provider']}

### Description:
The subdomain points to a third-party service provider ({takeover_info['provider']}), but the associated account setup has been removed or abandoned. An attacker can register the same identifier at the provider's platform to claim ownership of this domain.

### Remediation:
Remove the dangling CNAME pointer from your DNS zone settings file immediately.

---
"""
        counter += 1

    if http_info["cors_vulnerable"]:
        report_content += f"""## Bug #{counter}: Medium Risk - Insecure CORS Misconfiguration
- **Severity:** Medium (CVSS v3: 6.5)
- **CWE-ID:** CWE-942

### Description:
The application dynamically reflects arbitrary domains inside the `Access-Control-Allow-Origin` header (Allowed Origin: `{http_info['cors_origin_allowed']}`).

### Impact:
Malicious scripts hosted on completely foreign domains can make authenticated requests to extract sensitive APIs or user data.

### Remediation:
Implement a strict whitelist of trusted source origins. Avoid blindly reflecting the 'Origin' request header.

---
"""
        counter += 1

    if http_info["hsts_absent"]:
        report_content += f"""## Bug #{counter}: Low Risk - Missing Strict-Transport-Security (HSTS) Header
- **Severity:** Low (CVSS v3: 3.5)
- **CWE-ID:** CWE-693

### Description:
The server does not implement the HSTS header, exposing local network clients to SSL Striping attacks.

### Remediation:
Add `add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;` to Nginx configs [hstspreload.org].

---
"""
        counter += 1

    if "VULNERABLE" in tls_info["poodle_vulnerable"]:
        report_content += f"""## Bug #{counter}: High Risk - POODLE Vulnerability (SSLv3)
- **Severity:** High (CVSS v3: 7.5)
- **CWE-ID:** CWE-327

### Description:
The server accepts SSLv3 protocol, which is vulnerable to POODLE attacks.

### Remediation:
Disable SSLv3 and use TLS 1.2 or higher only.

---
"""
        counter += 1

    if "VULNERABLE" in tls_info["beast_vulnerable"]:
        report_content += f"""## Bug #{counter}: High Risk - BEAST Vulnerability (TLS 1.0 CBC)
- **Severity:** High (CVSS v3: 7.5)
- **CWE-ID:** CWE-327

### Description:
The server accepts TLS 1.0 with CBC ciphers, vulnerable to BEAST attacks.

### Remediation:
Disable TLS 1.0 and use TLS 1.2 or higher with strong ciphers.

---
"""
        counter += 1

    if "VULNERABLE" in tls_info["sweet32_vulnerable"]:
        report_content += f"""## Bug #{counter}: Medium Risk - Sweet32 Vulnerability (3DES)
- **Severity:** Medium (CVSS v3: 6.5)
- **CWE-ID:** CWE-327

### Description:
The server accepts 3DES cipher, which has weak 64-bit block size leading to Sweet32 attacks.

### Remediation:
Remove 3DES ciphers and use AES-256 or ChaCha20 instead.

---
"""
        counter += 1

    report_content += f"""## Summary
Total Vulnerabilities Found: {counter - 1}

This report was generated by SSL-ARMOR v2.5
**Scanner Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

    return report_content


def main():
    show_banner()
    try:
        user_raw_url = console.input(
            "\n[bold green][+] Input Target URL (e.g., https://example.com): [/bold green]"
        ).strip()
        if not user_raw_url:
            console.print("[bold red][-] No URL provided![/bold red]")
            sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[bold red][-] Scan cancelled by user[/bold red]")
        sys.exit(0)

    host, port, finalized_url = extract_target_metadata(user_raw_url)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress_ui:
        progress_ui.add_task(
            description="[cyan]Running Global Security Scan Suite v2.5...[/cyan]",
            total=100,
        )
        http_audit = audit_http_transport(finalized_url)
        tls_audit = audit_tls_cryptography(host, port)
        takeover_audit = audit_subdomain_takeover(host)

    summary_table = Table(title=f"\n📊 Vulnerability Scan Summary: {host}")
    summary_table.add_column("Security Checkpoint", justify="left", style="cyan")
    summary_table.add_column("Result Finding", justify="center", style="white")

    summary_table.add_row(
        "Subdomain Takeover Target",
        (
            f"[bold red]VULNERABLE ({takeover_audit['provider']})[/bold red]"
            if takeover_audit["takeover_possible"]
            else "[green]Safe (No Dangling Pointers)[/green]"
        ),
    )
    summary_table.add_row(
        "CORS Cross-Origin Policy",
        (
            "[bold red]VULNERABLE (Arbitrary Reflection Enabled)[/bold red]"
            if http_audit["cors_vulnerable"]
            else "[green]Safe (Secure Origin Strategy)[/green]"
        ),
    )
    summary_table.add_row(
        "HSTS Policy Protection",
        "[bold red]MISSING[/bold red]" if http_audit["hsts_absent"] else "[green]Safe[/green]",
    )
    summary_table.add_row(
        "POODLE / SSLv3 Check",
        (
            "[bold red]VULNERABLE[/bold red]"
            if "VULNERABLE" in tls_audit["poodle_vulnerable"]
            else "[green]Safe[/green]"
        ),
    )
    summary_table.add_row(
        "BEAST / TLS 1.0 CBC",
        (
            "[bold red]VULNERABLE[/bold red]"
            if "VULNERABLE" in tls_audit["beast_vulnerable"]
            else "[green]Safe[/green]"
        ),
    )
    summary_table.add_row(
        "Sweet32 / 3DES Cipher",
        (
            "[bold red]VULNERABLE[/bold red]"
            if "VULNERABLE" in tls_audit["sweet32_vulnerable"]
            else "[green]Safe[/green]"
        ),
    )

    console.print(summary_table)

    report_md = generate_high_quality_report(
        host, finalized_url, http_audit, tls_audit, takeover_audit
    )
    output_filename = f"bug_bounty_report_{host.replace('.', '_')}.md"

    with open(output_filename, "w", encoding="utf-8") as text_file:
        text_file.write(report_md)

    console.print(
        f"\n[bold green][+] High-Quality Markdown Bug Report Saved As: {output_filename}[/bold green]"
    )


if __name__ == "__main__":
    main()
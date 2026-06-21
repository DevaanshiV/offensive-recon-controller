# app.py
import threading
import time
import random
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# ------------------------------------------------------------------------------
# SIMULATED SCANNING ENGINES
# ------------------------------------------------------------------------------
# Each scan function uses multi-threading to simulate concurrent checks.
# All network interactions are replaced with deterministic sleeps and
# pre-defined result sets to avoid any real network traffic and firewall blocks.

def run_port_scan(target):
    """Simulate a port scan on common ports with multi-threading."""
    ports = [
        {"port": 22, "service": "SSH"},
        {"port": 80, "service": "HTTP"},
        {"port": 443, "service": "HTTPS"},
        {"port": 8080, "service": "HTTP-Alt"},
        {"port": 3306, "service": "MySQL"},
        {"port": 5432, "service": "PostgreSQL"},
        {"port": 25, "service": "SMTP"},
        {"port": 110, "service": "POP3"},
        {"port": 143, "service": "IMAP"},
        {"port": 993, "service": "IMAPS"},
        {"port": 995, "service": "POP3S"},
    ]
    # Predefined open ports for simulation
    open_ports = {80, 443, 8080, 3306}  # these will be "open"

    results = []
    # Use ThreadPoolExecutor to check ports concurrently
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for p in ports:
            # Submit each port check as a separate task
            futures.append(executor.submit(simulate_port_check, p, open_ports, target))
        for future in futures:
            results.append(future.result())
    return results

def simulate_port_check(port_info, open_ports, target):
    """Simulate checking a single port."""
    port = port_info["port"]
    service = port_info["service"]
    # Simulate network delay
    time.sleep(random.uniform(0.02, 0.08))
    is_open = port in open_ports
    status = "OPEN" if is_open else "CLOSED"
    badge = "success" if is_open else "danger"
    return {
        "port": port,
        "service": service,
        "status": status,
        "badge": badge,
    }

def run_directory_scan(target):
    """Simulate a directory busting scan on common paths."""
    paths = [
        "/",
        "/admin",
        "/login",
        "/api",
        "/assets",
        "/images",
        "/css",
        "/js",
        "/wp-admin",
        "/phpmyadmin",
        "/backup",
        "/config",
        "/robots.txt",
        "/sitemap.xml",
    ]
    # Predefined status codes for simulation
    status_map = {
        "/": 200,
        "/admin": 403,
        "/login": 200,
        "/api": 200,
        "/assets": 200,
        "/images": 200,
        "/css": 200,
        "/js": 200,
        "/wp-admin": 403,
        "/phpmyadmin": 404,
        "/backup": 404,
        "/config": 404,
        "/robots.txt": 200,
        "/sitemap.xml": 200,
    }

    results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for path in paths:
            futures.append(executor.submit(simulate_directory_check, path, status_map, target))
        for future in futures:
            results.append(future.result())
    return results

def simulate_directory_check(path, status_map, target):
    """Simulate checking a single directory path."""
    time.sleep(random.uniform(0.01, 0.06))
    status_code = status_map.get(path, 404)
    is_found = status_code < 400
    badge = "success" if is_found else "danger"
    # Simulate content length
    length = random.randint(100, 5000) if is_found else 0
    return {
        "path": path,
        "status_code": status_code,
        "length": length,
        "found": is_found,
        "badge": badge,
    }

def run_subdomain_scan(target):
    """Simulate subdomain enumeration on common subdomains."""
    subdomains = [
        "www",
        "mail",
        "dev",
        "staging",
        "api",
        "blog",
        "shop",
        "ftp",
        "admin",
        "test",
        "vpn",
    ]
    # Predefined resolved subdomains (simulated)
    resolved = {"www", "mail", "api", "blog", "shop"}

    results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for sub in subdomains:
            futures.append(executor.submit(simulate_subdomain_check, sub, resolved, target))
        for future in futures:
            results.append(future.result())
    return results

def simulate_subdomain_check(subdomain, resolved, target):
    """Simulate checking a single subdomain."""
    time.sleep(random.uniform(0.02, 0.07))
    is_resolved = subdomain in resolved
    ip = f"192.168.{random.randint(1,254)}.{random.randint(1,254)}" if is_resolved else None
    badge = "success" if is_resolved else "danger"
    return {
        "subdomain": subdomain,
        "resolved": is_resolved,
        "ip": ip,
        "badge": badge,
    }

# ------------------------------------------------------------------------------
# FLASK ROUTING MATRIX
# ------------------------------------------------------------------------------
#   Endpoint         Method   Purpose
#   /                GET      Render the main dashboard (index.html)
#   /scan            POST     Accept target and scan_type, execute scan, return JSON results
# ------------------------------------------------------------------------------

@app.route("/")
def index():
    """Render the main interface."""
    return render_template("index.html")

@app.route("/scan", methods=["POST"])
def scan():
    """
    Execute a scan based on the provided parameters.
    Expects JSON: { "target": "example.com", "scan_type": "port" | "directory" | "subdomain" }
    Returns JSON with scan results.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request, JSON expected"}), 400

    target = data.get("target", "").strip()
    scan_type = data.get("scan_type", "").strip()

    if not target:
        return jsonify({"error": "Target is required"}), 400

    # Validate scan_type
    if scan_type not in ("port", "directory", "subdomain"):
        return jsonify({"error": "Invalid scan_type. Must be 'port', 'directory', or 'subdomain'"}), 400

    # Execute the appropriate scan function (simulated, multi-threaded)
    if scan_type == "port":
        results = run_port_scan(target)
    elif scan_type == "directory":
        results = run_directory_scan(target)
    elif scan_type == "subdomain":
        results = run_subdomain_scan(target)
    else:
        results = []

    # Return results as JSON
    return jsonify({
        "target": target,
        "scan_type": scan_type,
        "results": results,
        "count": len(results),
    })

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
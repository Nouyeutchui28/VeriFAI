import socket
import concurrent.futures

def scan_port(ip, port, timeout=2):
    """Scan a single port and try to grab the banner."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            result = s.connect_ex((ip, port))
            if result == 0:
                # Try to grab banner
                try:
                    s.sendall(b"HEAD / HTTP/1.0\r\n\r\n")
                    banner = s.recv(1024).decode('utf-8', errors='ignore').strip()
                except:
                    banner = "Unknown Service (No banner)"
                return {
                    "port": port,
                    "status": "Open",
                    "banner": banner[:200] if banner else "No banner response"
                }
    except:
        pass
    return None

def run_infra_scan(target, ports=None):
    """Run a multi-threaded port scan on a target."""
    if ports is None:
        # Common ports similar to Shodan/Nmap defaults
        ports = [21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445, 993, 995, 1723, 3306, 3389, 5900, 8080, 8443]
    
    # Resolve domain to IP if necessary
    try:
        ip = socket.gethostbyname(target)
    except:
        return {"error": f"Could not resolve target: {target}"}

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(scan_port, ip, port) for port in ports]
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            if res:
                results.append(res)
    
    return {
        "target": target,
        "ip": ip,
        "findings": sorted(results, key=lambda x: x['port'])
    }

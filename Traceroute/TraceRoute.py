import subprocess
import re
import socket
import requests

def perform_traceroute(target, max_hops=30):

    hops = []
    try:

        target_ip = socket.gethostbyname(target)
        print(f"Tracing route to {target} ({target_ip})...")

        # Run tracert command
        process = subprocess.Popen(['tracert', '-h', str(max_hops), target_ip],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   text=True)
        output, _ = process.communicate()


        lines = output.splitlines()
        for line in lines[4:]:
            if "***" in line or "Request timed out" in line:
                hops.append("*")
                print(line.strip())
            else:
                match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                if match:
                    ip = match.group(1)
                    hops.append(ip)
                    print(line.strip())
            if target_ip in line:
                break

        return hops
    except Exception as e:
        print(f"Error during traceroute: {e}")
        return []

def is_private_ip(ip):

    private_ranges = [
        r'^10\..*',
        r'^172\.(1[6-9]|2[0-9]|3[0-1])\..*',
        r'^192\.168\..*'
    ]
    return any(re.match(pattern, ip) for pattern in private_ranges)

def get_asn(ip):

    if ip == "*" or is_private_ip(ip):
        return "N/A"

    try:
        whois_server = "whois.radb.net"
        port = 43
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((whois_server, port))

        s.send(f"{ip}\r\n".encode())
        response = ""
        while True:
            data = s.recv(1024).decode()
            if not data:
                break
            response += data

        s.close()

        asn_match = re.search(r'origin:\s*AS(\d+)', response, re.IGNORECASE)
        return asn_match.group(1) if asn_match else "Unknown"
    except Exception as e:
        print(f"WHOIS query failed for {ip}: {e}")
        return "Unknown"

def get_geo_info(ip):

    if ip == "*" or is_private_ip(ip):
        return "N/A", "N/A"

    try:
        response = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
        data = response.json()
        if data["status"] == "success":
            country = data.get("country", "Unknown")
            isp = data.get("isp", "Unknown")
            return country, isp
        return "Unknown", "Unknown"
    except Exception as e:
        print(f"Geo info query failed for {ip}: {e}")
        return "Unknown", "Unknown"

def print_table(hops):

    print("\n{:<10} | {:<15} | {:<10} | {:<20} | {:<30}".format("Order", "IP", "AS", "Country", "Provider"))
    print("-" * 80)
    for i, ip in enumerate(hops, 1):
        asn = get_asn(ip)
        country, isp = get_geo_info(ip)
        print("{:<10} | {:<15} | {:<10} | {:<20} | {:<30}".format(i, ip, asn, country, isp))

def main():

    target = input("Enter a domain name or IP address: ").strip()


    hops = perform_traceroute(target)


    print_table(hops)

if __name__ == "__main__":
    main()
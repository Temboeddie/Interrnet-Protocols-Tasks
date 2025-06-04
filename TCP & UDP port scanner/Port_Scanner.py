import socket
import concurrent.futures
import time



TIMEOUT = 1
Max_threads = 100


def scan_tcp_port(host,port):
    #Trying to connect to a TCP port
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as sock:
        sock.settimeout(TIMEOUT)
        try:
            sock.connect((host,port))
            return  port, 'Open'
        except:
            return port, 'Closed'


def scan_udp_port(host,port):
    # Send empty udp packet and check ICMP unreachable
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(TIMEOUT)
        try:
            sock.sendto(b'', (host, port))
            sock.recvfrom(1024)  # Try to receive back any response
            return port, 'open or filtered'
        except socket.timeout:
            return port, 'open or filtered'
        except socket.error:
            return port, 'closed'

def scan_range(host, port_range, protocol='tcp'):
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=Max_threads) as executor:
        futures = []
        for port in port_range:
            if protocol == 'tcp':
                futures.append(executor.submit(scan_tcp_port, host, port))
            elif protocol == 'udp':
                futures.append(executor.submit(scan_udp_port, host, port))
        for future in concurrent.futures.as_completed(futures):
            port, status = future.result()
            results.append((port, status))
    return sorted(results)


def main():
    host = input("Enter the host IP or domain: ").strip()
    start_port = int(input("Start port: "))
    end_port = int(input("End port: "))
    ports = range(start_port, end_port + 1)

    print("\n Scanning TCP ports...")
    start = time.time()
    tcp_results = scan_range(host, ports, protocol='tcp')
    print(f"TCP scan done in {time.time() - start:.2f} seconds.\n")
    for port, status in tcp_results:
        if status == 'open':
            print(f"TCP {port}: {status}")

    print("\n Scanning UDP ports...")
    start = time.time()
    udp_results = scan_range(host, ports, protocol='udp')
    print(f"UDP scan done in {time.time() - start:.2f} seconds.\n")
    for port, status in udp_results:
        print(f"UDP {port}: {status}")


if __name__ == "__main__":
    main()
import socket
import struct
import time
import datetime

NTP_SERVER = "127.0.0.1"
NTP_PORT = 123
NTP_DELTA = 2208988800

def request_time():
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.settimeout(5)

    # Send empty 48-byte request
    msg = b'\x1b' + 47 * b'\0'
    client.sendto(msg, (NTP_SERVER, NTP_PORT))

    try:
        data, _ = client.recvfrom(1024)
    except socket.timeout:
        print("Request timed out.")
        return

    if len(data) < 48:
        print("Incomplete SNTP response.")
        return

    # Unpack transmit timestamp (bytes 40–47)
    unpacked = struct.unpack("!12I", data)
    transmit_timestamp = unpacked[10] + float(unpacked[11]) / 2**32

    unix_time = transmit_timestamp - NTP_DELTA
    print("Received (fake) time:", datetime.datetime.fromtimestamp(unix_time, datetime.timezone.utc))
    print("Unix time (with offset):", unix_time)

if __name__ == "__main__":
    request_time()

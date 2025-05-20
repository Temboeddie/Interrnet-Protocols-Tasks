import socket
import time
import struct



Config_file = "config.txt"
NTP_Port = 123
NTP_Delta = 2208988800

def read_offset():
    with open(Config_file) as f:
        for line in f :
            if line.startswith("offset_seconds"):
                return int(line.strip().split('-')[1])

    return 0

def get_curr_time(offset_seconds):
    unix_time =  time.time() + offset_seconds
    ntp_time = unix_time +NTP_Delta
    seconds = int(ntp_time)
    fraction = int((ntp_time-seconds) * (2**32))
    return seconds,fraction

def create_sntp_packet(transmit_ts_second,transmit_ts_fraction):
    LI = 0
    VN = 4
    MODE = 4
    STRATUM = 2
    POLL = 0
    PRECISION = -20

    root_delay = 0
    root_dispersion = 0
    ref_id = b'LOCL'  # Reference identifier


    ref_ts = transmit_ts_second,transmit_ts_fraction
    recv_ts = transmit_ts_second,transmit_ts_fraction
    orig_ts = transmit_ts_second, transmit_ts_fraction
    xmit_ts = transmit_ts_second, transmit_ts_fraction

    # Build binary packet
    packet = struct.pack(
        "!B B b b 11I",
        (LI << 6) | (VN << 3) | MODE,
        STRATUM,
        POLL,
        PRECISION,
        root_delay,
        root_dispersion,
        struct.unpack("!I", ref_id)[0],
        *ref_ts,
        *orig_ts,
        *recv_ts,
        *xmit_ts
    )
    return packet

def run_server():
    offset = read_offset()
    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    sock.bind(('',NTP_Port))
    print(f"SNTP server running on port {NTP_Port} with offset {offset} seconds ")

    while True:
        data,address = sock.recvfrom(1024)
        transmit_second,transmit_fraction = get_curr_time(offset)
        packet  = create_sntp_packet(transmit_second,transmit_fraction)
        sock.sendto(packet,address)
        print(f"Responded to {address} with altered time")
if __name__ == "__main__":
    run_server()

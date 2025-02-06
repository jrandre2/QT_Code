# speedtest.py
import socket
import utime
import struct

# -------------------------------
# ICMP Checksum Calculation
# -------------------------------
def icmp_checksum(data):
    if len(data) % 2:
        data += b'\x00'
    s = 0
    for i in range(0, len(data), 2):
        w = data[i] << 8 | data[i+1]
        s += w
        s = (s & 0xffff) + (s >> 16)
    return ~s & 0xffff

# -------------------------------
# Ping Test Functionality
# -------------------------------
def perform_ping_test(host, count=4, timeout=1000):
    """
    Sends ICMP echo requests ("ping") to the specified host.
    Returns a formatted string with the average round-trip time.
    """
    times = []
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    except Exception as e:
        return "Ping not supported: " + str(e)
    s.settimeout(timeout/1000)
    addr = socket.getaddrinfo(host, 1)[0][-1][0]
    for i in range(count):
        icmp_type = 8  # Echo request
        icmp_code = 0
        icmp_id = 1
        icmp_seq = i + 1
        header = struct.pack("!BBHHH", icmp_type, icmp_code, 0, icmp_id, icmp_seq)
        payload = b'abcdefghijklmnopqrstuvwabcdefghi'
        chksum = icmp_checksum(header + payload)
        header = struct.pack("!BBHHH", icmp_type, icmp_code, chksum, icmp_id, icmp_seq)
        packet = header + payload
        start = utime.ticks_ms()
        try:
            s.sendto(packet, (addr, 1))
            reply, _ = s.recvfrom(1024)
            end = utime.ticks_ms()
            times.append(utime.ticks_diff(end, start))
        except Exception as e:
            times.append(None)
        utime.sleep_ms(1000)
    s.close()
    successful = [t for t in times if t is not None]
    if successful:
        avg = sum(successful) / len(successful)
        return "Ping: {} ms average over {} successful pings out of {} attempts".format(avg, len(successful), count)
    else:
        return "Ping: No replies received"

# -------------------------------
# Download Speed Test
# -------------------------------
def download_speed_test(server, port, path, block_size=1024, max_bytes=1024*64):
    """
    Connects to the specified HTTP server, downloads data up to max_bytes,
    and returns a formatted string with the total bytes, elapsed time, and speed.
    """
    s = socket.socket()
    try:
        addr_info = socket.getaddrinfo(server, port)
        addr = addr_info[0][-1]
        s.connect(addr)
        request = "GET {} HTTP/1.0\r\nHost: {}\r\n\r\n".format(path, server)
        s.send(request.encode())
        total_bytes = 0
        start = utime.ticks_ms()
        while total_bytes < max_bytes:
            data = s.recv(block_size)
            if not data:
                break
            total_bytes += len(data)
        end = utime.ticks_ms()
        elapsed = utime.ticks_diff(end, start) / 1000
        speed = total_bytes / elapsed if elapsed > 0 else 0
        return "Download: {} bytes in {} sec, Speed: {} B/s".format(total_bytes, elapsed, speed)
    except Exception as e:
        return "Download test error: {}".format(e)
    finally:
        s.close()

def perform_download_test():
    # Adjust these parameters to point to a valid test resource.
    server = "example.com"        # Replace with your test server
    port = 80
    path = "/largefile.bin"       # Replace with a valid resource path
    return download_speed_test(server, port, path)

# -------------------------------
# Upload Speed Test
# -------------------------------
def upload_speed_test(server, port, data, block_size=1024):
    """
    Uploads data to the specified server and measures the upload speed.
    Returns a formatted string with the total bytes, elapsed time, and speed.
    """
    s = socket.socket()
    try:
        addr_info = socket.getaddrinfo(server, port)
        addr = addr_info[0][-1]
        s.connect(addr)
        total_bytes = 0
        start = utime.ticks_ms()
        for i in range(0, len(data), block_size):
            sent = s.send(data[i:i+block_size])
            total_bytes += sent
        end = utime.ticks_ms()
        elapsed = utime.ticks_diff(end, start) / 1000
        speed = total_bytes / elapsed if elapsed > 0 else 0
        return "Upload: {} bytes in {} sec, Speed: {} B/s".format(total_bytes, elapsed, speed)
    except Exception as e:
        return "Upload test error: {}".format(e)
    finally:
        s.close()

def perform_upload_test():
    # Adjust these parameters to point to a valid test endpoint.
    server = "example.com"        # Replace with your test server
    port = 80
    test_data = b'a' * (1024 * 64)  # 64 KB of data
    return upload_speed_test(server, port, test_data)

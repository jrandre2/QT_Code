# speedtest.py
import socket
import utime
import struct

def icmp_checksum(data):
    if len(data) % 2:
        data += b'\x00'
    s = 0
    for i in range(0, len(data), 2):
        w = (data[i] << 8) | data[i+1]
        s += w
        s = (s & 0xffff) + (s >> 16)
    return ~s & 0xffff

def perform_ping_test(host, count=4, timeout=1000):
    times = []
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    except Exception as e:
        return "Ping not supported: " + str(e)
    s.settimeout(timeout/1000)
    addr = socket.getaddrinfo(host, 1)[0][-1][0]
    for i in range(count):
        icmp_type, icmp_code, icmp_id, icmp_seq = 8, 0, 1, i+1
        header = struct.pack("!BBHHH", icmp_type, icmp_code, 0, icmp_id, icmp_seq)
        payload = b'abcdefghijklmnopqrstuvwabcdefghi'
        chksum = icmp_checksum(header + payload)
        header = struct.pack("!BBHHH", icmp_type, icmp_code, chksum, icmp_id, icmp_seq)
        packet = header + payload
        start = utime.ticks_ms()
        try:
            s.sendto(packet, (addr, 1))
            s.recvfrom(1024)
            times.append(utime.ticks_diff(utime.ticks_ms(), start))
        except Exception:
            times.append(None)
        utime.sleep_ms(1000)
    s.close()
    valid = [t for t in times if t is not None]
    if valid:
        avg = sum(valid) / len(valid)
        return "Ping: {} ms average over {} of {} pings".format(avg, len(valid), count)
    else:
        return "Ping: No replies received"

def download_speed_test(server, port, path, block_size=1024, max_bytes=1024*64):
    s = socket.socket()
    try:
        addr = socket.getaddrinfo(server, port)[0][-1]
        s.connect(addr)
        s.send("GET {} HTTP/1.0\r\nHost: {}\r\n\r\n".format(path, server).encode())
        total = 0
        start = utime.ticks_ms()
        while total < max_bytes:
            data = s.recv(block_size)
            if not data:
                break
            total += len(data)
        elapsed = utime.ticks_diff(utime.ticks_ms(), start) / 1000
        speed = total / elapsed if elapsed > 0 else 0
        return "Download: {} bytes in {} sec, Speed: {} B/s".format(total, elapsed, speed)
    except Exception as e:
        return "Download test error: " + str(e)
    finally:
        s.close()

def perform_download_test():
    server, port, path = "example.com", 80, "/largefile.bin"
    return download_speed_test(server, port, path)

def upload_speed_test(server, port, data, block_size=1024):
    s = socket.socket()
    try:
        addr = socket.getaddrinfo(server, port)[0][-1]
        s.connect(addr)
        total = 0
        start = utime.ticks_ms()
        for i in range(0, len(data), block_size):
            sent = s.send(data[i:i+block_size])
            total += sent
        elapsed = utime.ticks_diff(utime.ticks_ms(), start) / 1000
        speed = total / elapsed if elapsed > 0 else 0
        return "Upload: {} bytes in {} sec, Speed: {} B/s".format(total, elapsed, speed)
    except Exception as e:
        return "Upload test error: " + str(e)
    finally:
        s.close()

def perform_upload_test():
    server, port = "example.com", 80
    test_data = b'a' * (1024 * 64)
    return upload_speed_test(server, port, test_data)

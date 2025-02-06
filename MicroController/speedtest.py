# speedtest.py
import socket
import utime

def download_speed_test(server, port, path, block_size=1024, max_bytes=1024*64):
    """
    Connects to the specified HTTP server and downloads data until max_bytes is reached.
    Returns a formatted string with the total bytes downloaded, elapsed time, and speed in bytes/sec.
    """
    s = socket.socket()
    try:
        addr_info = socket.getaddrinfo(server, port)
        addr = addr_info[0][-1]
        s.connect(addr)
        
        # Send a simple HTTP GET request.
        request = "GET {} HTTP/1.0\r\nHost: {}\r\n\r\n".format(path, server)
        s.send(request.encode())
        
        total_bytes = 0
        start = utime.ticks_ms()
        while total_bytes < max_bytes:
            data = s.recv(block_size)
            if not data:
                break  # End of data stream
            total_bytes += len(data)
        end = utime.ticks_ms()
        
        elapsed = utime.ticks_diff(end, start) / 1000  # seconds
        speed = total_bytes / elapsed if elapsed > 0 else 0
        return "Download: {} bytes in {} sec, Speed: {} B/s".format(total_bytes, elapsed, speed)
    except Exception as e:
        print("Download speed test error:", e)
        return "Download speed test error: {}".format(e)
    finally:
        s.close()

def perform_download_test():
    # Parameters for the test – update these to point to a real test resource.
    server = "example.com"        # Replace with your test server
    port = 80
    path = "/largefile.bin"       # Replace with a valid resource path
    return download_speed_test(server, port, path)

if __name__ == '__main__':
    print(perform_download_test())

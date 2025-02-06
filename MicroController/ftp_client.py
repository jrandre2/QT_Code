# ftp_client.py
import socket
import config

cfg = config.load_config()
FTP_SERVER = cfg.get("ftp", {}).get("SERVER", "ftp.example.com")
FTP_PORT = cfg.get("ftp", {}).get("PORT", 21)
USERNAME = cfg.get("ftp", {}).get("USERNAME", "user")
PASSWORD = cfg.get("ftp", {}).get("PASSWORD", "pass")
REMOTE_PATH = cfg.get("ftp", {}).get("REMOTE_PATH", "/upload/data.txt")

def ftp_upload_data(data):
    try:
        s = socket.socket()
        addr = socket.getaddrinfo(FTP_SERVER, FTP_PORT)[0][-1]
        s.connect(addr)
        
        def recv_line(sock):
            line = b""
            while True:
                ch = sock.recv(1)
                if ch == b'\n':
                    break
                line += ch
            return line.decode("utf-8").strip()
        
        print("FTP:", recv_line(s))
        s.send("USER {}\r\n".format(USERNAME).encode())
        print("FTP:", recv_line(s))
        s.send("PASS {}\r\n".format(PASSWORD).encode())
        print("FTP:", recv_line(s))
        s.send("TYPE I\r\n".encode())
        print("FTP:", recv_line(s))
        s.send("PASV\r\n".encode())
        resp = recv_line(s)
        print("FTP PASV:", resp)
        start = resp.find('(')
        end = resp.find(')')
        numbers = resp[start+1:end].split(',')
        ip = '.'.join(numbers[:4])
        port = (int(numbers[4]) << 8) + int(numbers[5])
        s.send("STOR {}\r\n".format(REMOTE_PATH).encode())
        print("FTP:", recv_line(s))
        
        data_sock = socket.socket()
        data_addr = socket.getaddrinfo(ip, port)[0][-1]
        data_sock.connect(data_addr)
        data_sock.send(data.encode())
        data_sock.close()
        print("FTP:", recv_line(s))
        s.send("QUIT\r\n".encode())
        print("FTP:", recv_line(s))
        s.close()
        return True
    except Exception as e:
        print("FTP upload error:", e)
        return False

def upload_data(data):
    return ftp_upload_data(data)

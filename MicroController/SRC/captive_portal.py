# captive_portal.py
import socket
import config
import uasyncio as asyncio

cfg = config.load_config()
SURVEY_URL = cfg.get("captive_portal", {}).get("SURVEY_URL", "https://survey.example.com")

async def start_server():
    addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(5)
    print("Captive portal running on", addr)
    
    while True:
        client, addr = s.accept()
        print("Client connected from", addr)
        try:
            client.recv(1024)  # Discard request
            response = ("HTTP/1.1 302 Found\r\n"
                        "Location: {}\r\n"
                        "Content-Length: 0\r\n"
                        "\r\n").format(SURVEY_URL)
            client.send(response)
        except Exception as e:
            print("Error handling client:", e)
        finally:
            client.close()
        await asyncio.sleep(0)

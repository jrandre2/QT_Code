# logging.py
import utime

LOG_FILE = "log.txt"

def log(message):
    timestamp = utime.localtime()
    timestr = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(*timestamp[:6])
    log_line = "[{}] {}\n".format(timestr, message)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(log_line)
    except Exception as e:
        print("Logging error:", e)

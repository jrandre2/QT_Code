# logging.py
import utime

LOG_FILE = "log.txt"

def log(message):
    t = utime.localtime()
    # Timestamp to the minute: YYYY-MM-DD HH:MM
    timestr = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}".format(t[0], t[1], t[2], t[3], t[4])
    log_line = "[{}] {}\n".format(timestr, message)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(log_line)
    except Exception as e:
        print("Logging error:", e)

# utils.py
import utime

def get_timestamp():
    t = utime.localtime()
    return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}".format(t[0], t[1], t[2], t[3], t[4])

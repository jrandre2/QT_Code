# network_driver.py
from machine import SPI, Pin
import lib.w6100 as w6100

def init_ethernet():
    try:
        # Adjust SPI parameters and pin assignments as required for your board.
        spi = SPI(1, baudrate=10_000_000, polarity=0, phase=0)
        cs = Pin(15, Pin.OUT)
        eth = w6100.W6100(spi, cs)
        eth.init()  # Perform W6100-specific initialization.
        return True
    except Exception as e:
        print("Ethernet init error:", e)
        return False

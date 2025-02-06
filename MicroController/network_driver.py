# network_driver.py
import wizchip  # Native module from C wrapper (see extmod/wizchip/mod_wizchip.c)

def init_ethernet():
    try:
        wizchip.init()  # Call the native initialization function
        return wizchip   # Return the module so that get_ip(), etc., can be called.
    except Exception as e:
        print("Ethernet init error:", e)
        return None

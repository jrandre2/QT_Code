# File: bob/led.py
from driver import apa102
from bob.config import BASE_DIR  # or define LED config in config.py
import logging

logger = logging.getLogger('bob.led')

# Initialize the LED strip (led_strip = apa102.APA102(num_led=2, global_brightness=20, mosi=11, sclk=10, order='rgb')

def clear_leds():
    led_strip.clear_strip()
    led_strip.show()
    logger.info("LED strip cleared.")

def set_led(led_index: int, color: int):
    led_strip.set_pixel_rgb(led_index, color)
    led_strip.show()
    logger.info("Set LED %d to color 0x%06X", led_index, color)

def ready_red_leds():
    clear_leds()
    # Both LEDs red.
    for i in range(2):
        set_led(i, 0xFF0000)
    logger.info("LEDs set to red (startup/error).")

def intled_green():
    clear_leds()
    # For example, assume LED 1 is Internet status.
    set_led(1, 0x00FF00)
    # Optionally, you might want to indicate GPS status on LED 0.
    set_led(0, 0xFF0000)
    logger.info("Internet LED set to green.")

def gpsled_green():
    clear_leds()
    # Both LEDs green indicate GPS ready.
    for i in range(2):
        set_led(i, 0x00FF00)
    logger.info("GPS LED set to green.")

def bluelight_minion():
    clear_leds()
    # Both LEDs blue to indicate completion.
    for i in range(2):
        set_led(i, 0x0000FF)
    logger.info("LEDs set to blue (minion complete).")

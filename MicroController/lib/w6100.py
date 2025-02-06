"""
W6100 MicroPython Driver for the W6100-EVB-Pico2

This driver implements the low-level SPI interface to the W6100 hardwired TCP/IP controller.
It is based  the W6100 datasheet and the WIZnet-PICO-C repository.
Please verify all register addresses and control values against the official W6100 documentation.
"""

from machine import Pin, SPI
import utime

# ============================================================================
# Register Definitions (Global Registers)
# ============================================================================
W6100_MR      = 0x0000   # Mode Register (Global)
W6100_GAR     = 0x0001   # Gateway Address Register (4 bytes: 0x0001 - 0x0004)
W6100_SUBR    = 0x0005   # Subnet Mask Register (4 bytes: 0x0005 - 0x0008)
W6100_SHAR    = 0x0009   # Source Hardware Address (MAC) Register (6 bytes: 0x0009 - 0x000E)
W6100_SIPR    = 0x000F   # Source IP Address Register (4 bytes: 0x000F - 0x0012)
W6100_IR      = 0x0013   # Interrupt Register
W6100_IMR     = 0x0014   # Interrupt Mask Register

# Additional registers (for sockets, etc.) are not implemented in this driver.
# See the W6100 datasheet for a complete register map.

# ============================================================================
# SPI Control Byte Definitions
# ============================================================================
# The SPI transaction header consists of 3 bytes:
#  - 16-bit register address (big-endian)
#  - 8-bit control byte:
#      Bit 7: R/W flag (0 = write, 1 = read)
#      Bit 6: Burst Mode flag (0 = single byte, 1 = burst transfer)
#      Bits 5-0: Reserved or mode bits (typically 0)
#
# For a single-byte write operation, we use:
#    control_write = 0x00  (bit7 = 0, burst = 0)
#
# For a single-byte read operation, we use:
#    control_read = 0x80   (bit7 = 1, burst = 0)
#
CONTROL_WRITE = 0x00
CONTROL_READ  = 0x80

# ============================================================================
# W6100 Driver Class
# ============================================================================

class W6100:
    def __init__(self, spi: SPI, cs: Pin):
        """
        Initialize the W6100 driver with an SPI object and a chip-select (CS) Pin.
        """
        self.spi = spi
        self.cs = cs
        # Ensure CS is an output and initially high (inactive)
        self.cs.init(Pin.OUT, value=1)
    
    def _spi_write(self, address: int, data: bytes):
        """
        Write data bytes to the specified register address.
        The SPI frame consists of:
          - 2 bytes: register address (big-endian)
          - 1 byte: control byte (write)
          - Data bytes
        """
        header = bytearray(3)
        header[0] = (address >> 8) & 0xFF
        header[1] = address & 0xFF
        header[2] = CONTROL_WRITE  # Write operation
        self.cs.value(0)
        self.spi.write(header)
        self.spi.write(data)
        self.cs.value(1)
    
    def _spi_read(self, address: int, length: int) -> bytes:
        """
        Read 'length' bytes from the specified register address.
        The SPI frame for reading is:
          - 2 bytes: register address (big-endian)
          - 1 byte: control byte (read)
          - Then read 'length' data bytes from the SPI bus.
        """
        header = bytearray(3)
        header[0] = (address >> 8) & 0xFF
        header[1] = address & 0xFF
        header[2] = CONTROL_READ   # Read operation
        self.cs.value(0)
        self.spi.write(header)
        data = self.spi.read(length)
        self.cs.value(1)
        return data

    # --------------------------------------------------------------------------
    # Basic Control and Initialization
    # --------------------------------------------------------------------------
    def reset(self):
        """
        Perform a software reset of the W6100 by writing 0x01 to the Mode Register (MR).
        After issuing the reset, wait for the chip to complete initialization.
        """
        self._spi_write(W6100_MR, b'\x01')
        utime.sleep_ms(100)  # Wait 100 ms (adjust as per datasheet recommendations)
    
    def init(self):
        """
        Initialize the W6100.
        The initialization sequence is:
          1. Perform a software reset.
          2. Write normal operating mode to the Mode Register.
          3. (Optionally) Configure global network parameters.
        """
        self.reset()
        # Set normal operation mode (clear the reset bit)
        self._spi_write(W6100_MR, b'\x00')
        # Additional configuration may be done here if needed.
        print("W6100 initialized")
    
    # --------------------------------------------------------------------------
    # Global Network Configuration
    # --------------------------------------------------------------------------
    def set_gateway(self, ip_str: str):
        """
        Set the gateway IP address.
        :param ip_str: Gateway IP address as a string, e.g., "192.168.1.1"
        """
        parts = [int(x) for x in ip_str.split('.')]
        if len(parts) != 4:
            raise ValueError("Invalid IP address format")
        data = bytes(parts)
        self._spi_write(W6100_GAR, data)
    
    def set_subnet_mask(self, mask_str: str):
        """
        Set the subnet mask.
        :param mask_str: Subnet mask as a string, e.g., "255.255.255.0"
        """
        parts = [int(x) for x in mask_str.split('.')]
        if len(parts) != 4:
            raise ValueError("Invalid subnet mask format")
        data = bytes(parts)
        self._spi_write(W6100_SUBR, data)
    
    def set_mac(self, mac_str: str):
        """
        Set the MAC (hardware) address.
        :param mac_str: MAC address as a string, e.g., "AA:BB:CC:DD:EE:FF"
        """
        parts = mac_str.split(':')
        if len(parts) != 6:
            raise ValueError("Invalid MAC address format")
        data = bytes(int(x, 16) for x in parts)
        self._spi_write(W6100_SHAR, data)
    
    def set_ip(self, ip_str: str):
        """
        Set the source (local) IP address.
        :param ip_str: IP address as a string, e.g., "192.168.1.100"
        """
        parts = [int(x) for x in ip_str.split('.')]
        if len(parts) != 4:
            raise ValueError("Invalid IP address format")
        data = bytes(parts)
        self._spi_write(W6100_SIPR, data)
    
    # --------------------------------------------------------------------------
    # Global Configuration Readback
    # --------------------------------------------------------------------------
    def get_mac(self) -> str:
        """
        Retrieve the current MAC address from the chip.
        :return: MAC address as a string in the format "AA:BB:CC:DD:EE:FF"
        """
        data = self._spi_read(W6100_SHAR, 6)
        return ':'.join("{:02X}".format(b) for b in data)
    
    def get_ip(self) -> str:
        """
        Retrieve the current IP address from the chip.
        :return: IP address as a string in the format "192.168.1.100"
        """
        data = self._spi_read(W6100_SIPR, 4)
        return '.'.join(str(b) for b in data)

from digi.xbee.devices import DigiPointDevice, RemoteDigiPointDevice
from digi.xbee.models.address import XBee16BitAddress, XBee64BitAddress
from digi.xbee.models.options import DiscoveryOptions
from digi.xbee.models.status import NetworkDiscoveryStatus

DropBase = DigiPointDevice("COM3", 9600)
DropBase.open()

Drop1 = RemoteDigiPointDevice(DropBase, XBee64BitAddress.from_hex_string("0013A20041078CC9"))

DropBase.send_data_64_16(XBee64BitAddress.from_hex_string("000000000000FFFF"), XBee16BitAddress.UNKNOWN_ADDRESS, "DROP")


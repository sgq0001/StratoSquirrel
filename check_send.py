from digi.xbee.devices import DigiPointDevice, RemoteDigiPointDevice, XBee64BitAddress
from digi.xbee.models.address import XBee16BitAddress
from digi.xbee.models.options import DiscoveryOptions
from digi.xbee.models.status import NetworkDiscoveryStatus

DropSam = DigiPointDevice("COM14", 9600)
DropSam.open()

DropTristan = RemoteDigiPointDevice(DropSam, XBee64BitAddress.from_hex_string("0013A20041078CC9"))

DropSam.send_data_64_16(XBee64BitAddress.from_hex_string("0013A20041078CC9"), XBee16BitAddress.UNKNOWN_ADDRESS, "hello")


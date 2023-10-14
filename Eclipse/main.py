from digi.xbee.models.address import XBee16BitAddress
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
import time
from datetime import datetime
from digi.xbee.devices import DigiPointDevice, RemoteDigiPointDevice, XBee64BitAddress
from digi.xbee.models.options import DiscoveryOptions
from digi.xbee.models.status import NetworkDiscoveryStatus
from PyQt5.QtWidgets import QPushButton

# Instantiate Devices
DropBase = DigiPointDevice("COM16", 9600)
DropBase.open()

"""DropSam = DigiPointDevice("COM14", 9600)
DropSam.open()

DropTristan = RemoteDigiPointDevice(DropSam, XBee64BitAddress.from_hex_string("0013A20041078CC9"))"""

diginet = DropBase.get_network()
diginet.set_discovery_options({DiscoveryOptions.DISCOVER_MYSELF,
                               DiscoveryOptions.APPEND_DD})
diginet.set_discovery_timeout(10)
diginet.clear()


# Callback for discovered devices.
def callback_device_discovered(remote):
    print("Device discovered: %s" % remote)


# Callback for discovery finished.
def callback_discovery_finished(status):
    if status == NetworkDiscoveryStatus.SUCCESS:
        print("Discovery process finished successfully.\n")
    else:
        print("There was an error discovering devices: %s" % status.description)


"""# Start discovery process
diginet.add_device_discovered_callback(callback_device_discovered)
diginet.add_discovery_process_finished_callback(callback_discovery_finished)
diginet.start_discovery_process()
print("Discovering remote XBee devices...")
while diginet.is_discovery_running():
    time.sleep(0.5)"""

# Packet: String str = (String)(millis()/1000.0)+","+device+","
# +(String)altitude+","+(String)ascent_rate+","
# +(String)vent_status+","+(String)DROP_status+","
# +(String)latitude+","+(String)longitude;

checkDropNumber = False
counter = 0
split_data = []
dropDeviceNumber = input("Select Drop Device (1,2,3): ")

while not checkDropNumber:
    if dropDeviceNumber == "1":
        DropBalloon = RemoteDigiPointDevice(DropBase, XBee64BitAddress.from_hex_string("0013A200419992A6"))
        checkDropNumber = True
    elif dropDeviceNumber == "2":
        DropBalloon = RemoteDigiPointDevice(DropBase, XBee64BitAddress.from_hex_string("0013A200419992B6"))
        checkDropNumber = True
    elif dropDeviceNumber == "3":
        DropBalloon = RemoteDigiPointDevice(DropBase, XBee64BitAddress.from_hex_string("0013A200419992B6"))
        DropBalloon = RemoteDigiPointDevice(DropBase, XBee64BitAddress.from_hex_string("0013A200419992A6"))
        checkDropNumber = True
    else:
        dropDeviceNumber = input("Select Drop Device (1,2,3): ")
        checkDropNumber = False
    print()


packet_data = []
err_out_of_bounds = "SIM ERR: attempted to retrieve a packet out of profile's bounds"


# Receive message
def data_receive_callback(xbee_message):
    global packet_data
    raw_data = xbee_message.data.decode("latin-1")
    packet_data = raw_data.split(',')
    return packet_data


pg.setConfigOption('background', (250, 250, 250))
pg.setConfigOption('foreground', (0, 0, 0))
# Interface variables
app = QtGui.QApplication([])
view = pg.GraphicsView()
Layout = pg.GraphicsLayout()
view.setCentralItem(Layout)
view.show()
view.setWindowTitle('Flight Data')
view.resize(1200, 700)
# Fonts for text items
font = QtGui.QFont()
font.setPixelSize(90)

# buttons style
style_enable = "background-color:rgb(0, 204, 0);color:rgb(250,250,250);font:bold;font-size:17px;"
style_disable = "background-color:rgb(250, 0, 0);color:rgb(250,250,250);font:bold;font-size:17px;"

# Title
text = "Space Hardware Club: DROP Ground Station"
Layout.addLabel(text, col=3, colspan=5)
Layout.nextRow()

# Altitude graph
l1 = Layout.addLayout(colspan=20, rowspan=2)
p1 = l1.addPlot(title="GHOUL Altitude (m)")
altitude_plot = p1.plot(pen=(0, 119, 200))
altitude_data = np.linspace(0, 0, 30)
ptr1 = 0

# Altitude graph
p2 = l1.addPlot(title="SAROS Altitude (m)")
altitude2_plot = p2.plot(pen=(0, 119, 200))
altitude2_data = np.linspace(0, 0, 30)
ptr2 = 0
l1.nextCol()


def update_altitude(ALT):
    global altitude_plot, altitude_data, ptr1
    altitude_data[:-1] = altitude_data[1:]
    altitude_data[-1] = float(ALT)
    ptr1 += 1
    altitude_plot.setData(altitude_data)
    altitude_plot.setPos(ptr1, 0)

def update_altitude_S(ALT_S):
    global altitude2_plot, altitude2_data, ptr2
    altitude2_data[:-1] = altitude2_data[1:]
    altitude2_data[-1] = float(ALT_S)
    ptr2 += 1
    altitude2_plot.setData(altitude2_data)
    altitude2_plot.setPos(ptr2, 0)


# Time, battery and free fall graphs
l2 = Layout.addLayout(colspan=1, rowspan=2)


# Time graph
time_graph = l2.addPlot(title="GHOUL Time Display")
time_graph.hideAxis('bottom')
time_graph.hideAxis('left')
time_text = pg.TextItem("test", anchor=(0.5, 0.5), color=(0, 119, 200))
time_text.setFont(font)
time_graph.addItem(time_text)
time_graph.autoRange()
l2.nextRow()


def update_time(TIME):
    global time_text
    time_text.setText(str(TIME))

# State Display
vel_graph = l2.addPlot(title="GHOUL Vel Display: ")
vel_graph.hideAxis('bottom')
vel_graph.hideAxis('left')
vel_text = pg.TextItem("test", anchor=(0.5, 0.5), color=(0, 119, 200))
vel_text.setFont(font)
vel_graph.addItem(vel_text)
vel_graph.autoRange()


def update_vel(VEL):
    global vel_text
    vel_text.setText(str(VEL))


Layout.nextRow()
Layout.nextRow()
style = "background-color:rgb(0, 119, 200);color:rgb(250,250,250);font:bold;font-size:17px;"
enable = False
activate = False

prime = False
prime2= False



def drop_buttonPushed():
    if prime == True:
        DropBase.send_data_64_16(XBee64BitAddress.from_hex_string("0013A200419992A6"), XBee16BitAddress.UNKNOWN_ADDRESS, "DROP")
        print("Dropping...")

def drop_buttonPushed2():
    if prime2 == True:
        DropBase.send_data_64_16(XBee64BitAddress.from_hex_string("0013A200419992B6"), XBee16BitAddress.UNKNOWN_ADDRESS, "DROP")
        print("Dropping...")
        print("DROP SAROS")

def prime_Set():
    global prime
    if prime == False:
        prime = True
        drop_button.setStyleSheet(style_enable)
    else:
        prime = False
        drop_button.setStyleSheet(style_disable)

def prime_Set2():
    global prime2
    if prime2 == False:
        prime2 = True
        drop_button2.setStyleSheet(style_enable)
    else:
        prime2 = False
        drop_button2.setStyleSheet(style_disable)


button_layout = Layout.addLayout(colspan=21)
button_spot = button_layout.addLayout(rowspan=1, border=(83, 83, 83))
button_spot.nextRow()
proxy = QtGui.QGraphicsProxyWidget()
drop_button = QtGui.QPushButton('Drop GHOUL')
drop_button.setStyleSheet(style_disable)
drop_button.clicked.connect(drop_buttonPushed)
proxy.setWidget(drop_button)
button_spot.addItem(proxy)
button_spot.nextCol()

proxy2 = QtGui.QGraphicsProxyWidget()
prime_button = QtGui.QPushButton('Prime GHOUL')
prime_button.setStyleSheet(style)
prime_button.clicked.connect(prime_Set)
proxy2.setWidget(prime_button)
button_spot.addItem(proxy2)
button_spot.nextCol()

proxy3 = QtGui.QGraphicsProxyWidget()
drop_button2 = QtGui.QPushButton('Drop SAROS')
drop_button2.setStyleSheet(style_disable)
drop_button2.clicked.connect(drop_buttonPushed2)
proxy3.setWidget(drop_button2)
button_spot.addItem(proxy3)
button_spot.nextCol()

proxy4 = QtGui.QGraphicsProxyWidget()
prime_button2 = QtGui.QPushButton('Prime SAROS')
prime_button2.setStyleSheet(style)
prime_button2.clicked.connect(prime_Set2)
proxy4.setWidget(prime_button2)
button_spot.addItem(proxy4)
button_spot.nextCol()


def update():
    DropBase.add_data_received_callback(data_receive_callback)
    if "GHOUL" in packet_data:
        GHOUL_packet_data = packet_data
        try:
            TIME = GHOUL_packet_data[1]
            update_time(TIME)
            ALT = GHOUL_packet_data[3]
            update_altitude(ALT)
            VEL = GHOUL_packet_data[4]
            update_vel(VEL)
        except IndexError:
            print('Awaiting Packet')

    if "Drop2" in packet_data:
        SAROS_packet_data = packet_data
        print("SAROS")
        try:
            ALT_S = SAROS_packet_data[2]
            update_altitude_S(ALT_S)
        except IndexError:
            print('Awaiting Packet')

    print(packet_data)
        # CoolALT = ALT + "\r"

        # DropSam.send_data_64_16(XBee64BitAddress.from_hex_string("0013A20041078CC9"), XBee16BitAddress.UNKNOWN_ADDRESS, CoolALT)


if 1:
    timer = pg.QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(250)


if __name__ == '__main__':

    import sys

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()

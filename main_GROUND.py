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
DropBase = DigiPointDevice("COM22", 9600)
DropBase.open()

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


# Start discovery process
diginet.add_device_discovered_callback(callback_device_discovered)
diginet.add_discovery_process_finished_callback(callback_discovery_finished)
diginet.start_discovery_process()
print("Discovering remote XBee devices...")
while diginet.is_discovery_running():
    time.sleep(0.5)


checkDropNumber = False
counter = 0
split_data = []
print("Drop Device #1: Glider - cuts at 500")
print("Drop Device #2: CanSat - cuts at 700")
print("Drop Device #3: Glider - cuts at 500")
dropDeviceNumber = input("Select Drop Device (1,2,3): ")

while not checkDropNumber:
    if dropDeviceNumber == "1":
        DropBalloon = RemoteDigiPointDevice(DropBase, XBee64BitAddress.from_hex_string("0013A200419992B6"))
        checkDropNumber = True
    elif dropDeviceNumber == "2":
        DropBalloon = RemoteDigiPointDevice(DropBase, XBee64BitAddress.from_hex_string("0013A20041920D72"))
        checkDropNumber = True
    elif dropDeviceNumber == "3":
        DropBalloon = RemoteDigiPointDevice(DropBase, XBee64BitAddress.from_hex_string("0013A2004199939A"))
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


pg.setConfigOption('background', (0, 0, 0))
pg.setConfigOption('foreground', (197, 198, 199))
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

# Title
text = "DROP Ground Station"
Layout.addLabel(text, col=1, colspan=21)
Layout.nextRow()

# Vertical Label
Layout.addLabel('Space Hardware Club', angle=-90, rowspan=3)
Layout.nextRow()

# Altitude graph
l1 = Layout.addLayout(colspan=20, rowspan=2)
l11 = l1.addLayout(rowspan=1, border=(83, 83, 83))
p1 = l11.addPlot(title="Altitude (m)")
altitude_plot = p1.plot(pen=(0, 119, 200))
altitude_data = np.linspace(0, 0, 30)
ptr1 = 0


def update_altitude(ALT):
    global altitude_plot, altitude_data, ptr1
    altitude_data[:-1] = altitude_data[1:]
    altitude_data[-1] = float(ALT)
    ptr1 += 1
    altitude_plot.setData(altitude_data)
    altitude_plot.setPos(ptr1, 0)


# Time, battery and free fall graphs
l2 = Layout.addLayout(colspan=20, rowspan=2)
l21 = l2.addLayout(rowspan=1, border=(83, 83, 83))

# Time graph
time_graph = l21.addPlot(title="Time Display")
time_graph.hideAxis('bottom')
time_graph.hideAxis('left')
time_text = pg.TextItem("test", anchor=(0.5, 0.5), color=(0, 119, 200))
time_text.setFont(font)
time_graph.addItem(time_text)


def update_time(TIME):
    global time_text
    time_text.setText(str(TIME))


# State Display
l2.nextRow()
l22 = l2.addLayout(rowspan=1, border=(83, 83, 83))
state_graph = l22.addPlot(title="State Display: ")
state_graph.hideAxis('bottom')
state_graph.hideAxis('left')
state_text = pg.TextItem("test", anchor=(0.5, 0.5), color=(0, 119, 200))
state_text.setFont(font)
state_graph.addItem(state_text)


def update_state(STATE):
    global state_text
    state_text.setText(str(STATE))


Layout.nextRow()
Layout.nextRow()
style = "background-color:rgb(0, 119, 200);color:rgb(0,0,0);font-size:14px;"
enable = False
activate = False


def drop_buttonPushed():
    DropBase.send_data_64_16(XBee64BitAddress.from_hex_string("000000000000FFFF"), XBee16BitAddress.UNKNOWN_ADDRESS, "DROP")
    print("Dropping...")


def gs_bottonPushed():
    DropBase.close()
    print("GCS closed")
    exit()


button_layout = Layout.addLayout(colspan=21)
button_spot = button_layout.addLayout(rowspan=1, border=(83, 83, 83))
button_spot.nextRow()
proxy = QtGui.QGraphicsProxyWidget()
drop_button = QtGui.QPushButton('Drop Device')
drop_button.setStyleSheet(style)
drop_button.clicked.connect(drop_buttonPushed)
proxy.setWidget(drop_button)
button_spot.addItem(proxy)
button_spot.nextCol()

proxy2 = QtGui.QGraphicsProxyWidget()
gs_button = QtGui.QPushButton('GCS Off')
gs_button.setStyleSheet(style)
gs_button.clicked.connect(gs_bottonPushed)
proxy2.setWidget(gs_button)
button_spot.addItem(proxy2)
button_spot.nextCol()


def update():
    DropBase.add_data_received_callback(data_receive_callback)
    try:
        TIME = packet_data[0]
        update_time(TIME)
        ALT = packet_data[2]
        update_altitude(ALT)
        STATE = packet_data[3]
        update_state(STATE)
        CoolALT = ALT + "\r"

        DropSam.send_data_64_16(XBee64BitAddress.from_hex_string("0013A20041078CC9"), XBee16BitAddress.UNKNOWN_ADDRESS, CoolALT)

    except IndexError:
        print('Awaiting Packet')


if 1:
    timer = pg.QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(250)


if __name__ == '__main__':

    import sys

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()

import pydacq.rolling_buffer
import pydacq.polling_acquisition

import time
import socket

from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg


#### Constant for SesnorLog app ###############################################
IP_ADDR = '192.168.1.122'
IP_PORT = 56168
BUFFER_SIZE = 1024
CSV_SEPARATOR = ','

#### PyQt GUI setup ###########################################################
app = QtGui.QApplication([])
win = pg.GraphicsWindow(title="Live Buffered/Polling Plot")
win.resize(1000,600)
win.setWindowTitle('Live Buffered/Polling Plot')

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

# set up the tcp/ip connection to grab data from sensorlog
sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sck.connect((IP_ADDR,IP_PORT))

#### Data Poller, set up polling with a 100 member FIFO queued output
Poller = libs.polling_acquisition.PollingAquisition()
Poller.setup( size = 100 )

#### Rolling Numpy Array, log 3 channels for 100 samples
Buffer = libs.rolling_buffer.RollingBuffer()
Buffer.reset( length=100, dimensions=(3) )

# define the "read" function to return random data
def read_sensor( ):
  
  bufferedLines = sck.recv( BUFFER_SIZE )

  # look for newline char
  if "\n" not in bufferedLines:
    return True # try again later
  #self.log.debug( bufferedLines )
  # grab first line of data
  (line,bufferedLines) = bufferedLines.split("\n",1)

  # ignore empty line
  if line == "":
    return True # try again later

  # expected
  # date/time              ,id, time, roll      , pitch    , yaw
  # 2013-12-30 16:14:56.677,91,17.29,-0.02878424,-0.0337332,-0.02815148
  # csv split
  values = line.split( CSV_SEPARATOR )
  
  gyro_data = np.array([
    float( values[3] ),
    float( values[4] ),
    float( values[5] ),      
    ])
  
  timestamp = float( values[2] )

  return gyro_data

# when poller tries to read.... 
# assign the read_sensor function, to read from sensorlog
Poller.read = read_sensor

# define the "write" function to inject the queued data into the buffer
def write_buffer( packet ):
  Buffer.add_new( time.time(), packet )
  pass

# when poller ships data out....
# assign the write buffer function to write to our rolling array
Poller.write = write_buffer

# start acquiring data
Poller.start()

sensorplot = win.addPlot(title="Data")
curve1 = sensorplot.plot(pen='y')
curve2 = sensorplot.plot(pen='r')
curve3 = sensorplot.plot(pen='g')



# display update function runns on QTtimer
def update():
    # grab contents of rolling buffer
    ts_arr, data_arr = Buffer.get_all()
    curve1.setData( data_arr[:,0] )
    curve2.setData( data_arr[:,1] )
    curve3.setData( data_arr[:,2] )

timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(50)

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
  import sys
  if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
      QtGui.QApplication.instance().exec_()
  print('Shutting down')
  Poller.stop()
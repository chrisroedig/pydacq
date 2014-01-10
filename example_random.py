# example that displays a rolling graph of random numbers
import pydacq.rolling_buffer
import pydacq.polling_acquisition
import time

from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg


#### PyQt GUI setup ###########################################################
app = QtGui.QApplication([])
win = pg.GraphicsWindow(title="Live Buffered/Polling Plot")
win.resize(1000,600)
win.setWindowTitle('Live Buffered/Polling Plot')

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)



# polling data acquisition to grab the data
Poller = libs.polling_acquisition.PollingAquisition()
Poller.setup( size = 100 )

#### Rolling Numpy Array, log 4 channels for 100 samples
Buffer = libs.rolling_buffer.RollingBuffer()
Buffer.reset( length=1000, dimensions=(4) )


# define the "read" function to return random data
def read_rand( ):
  time.sleep(.01)
  return np.random.rand( 4 )

Poller.read = read_rand

# define the "write" function to inject the queued data into the buffer
def write_buffer( packet ):
  Buffer.add_new( time.time(), packet )
  pass

Poller.write = write_buffer

# start "acquiring data"
Poller.start()

randplot = win.addPlot(title="Data")
curve1 = randplot.plot(pen='y')
curve2 = randplot.plot(pen='r')


def update():
    ts_arr, data_arr = Buffer.get_all()
    curve1.setData( data_arr[:,0] )
    curve2.setData( data_arr[:,1] )

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
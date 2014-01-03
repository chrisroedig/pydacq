# PYDACQ 
Thread safe continous data acquisition and display framework.
Mainly an excersize in thread safe techniques.
This package allows the decoupling of data acquisition vs. UI response timeframes.
When acquiring data, the polling routine should never be blocked by downstream data handling. Likewise a UI or live analysis routine should not be block by data acquisition.
This packages provides thread safe data FIFO queues and buffers to fully decouple data acquisition from the UI while providing shared data access, streaming and processing.

## Dependecies

* numpy
* pyqtgraph (for examples)
 
## Testing

`python -m unittest discover -v`

## Examples

* example_random.py plot from a continously running rand generator
* example_sensorlog.py plt data polled (TCP/IP) from SensorLog iphone app

## Classes

### `PollingAquisition` 
Acquires data in `read` polling callback. The incoming data is buffered and shipped out of the queue by an overridable `write` callback.

### `RollingBuffer`
Maintains a stack of numpy arrays with thread safe read/write operations. Buffer has a fixed length and advances by one when new data is added, the oldest data drops off the end of the buffer. 
This is useful for providing strip-chart type displays of polled data.  

import unittest
import threading
import libs.polling_acquisition
import time 
#test_polling_acquisition.py

class TestPollingAcquisition( unittest.TestCase ):
  """
  #############################################################################
  Rolling np.array with thread safe access
  """ 
  def setUp( self ):
    self.pacq = libs.polling_acquisition.PollingAquisition()
    self.pacq.setup()
    pass

  def tearDown( self ):

    pass

  def test_setup( self ):
    self.pacq.setup(100)
    self.assertEqual( self.pacq._queue_size, 100 )
    pass

  def test_polling_loop( self ):
    # set up test tools
    self.read_lock = threading.Lock()
    self.write_lock = threading.Lock()
    self.read_val = 10
    self.write_val = None
    self.read_count = 0
    self.write_count = 0

    # override read_method
    self.pacq.read = self.locked_read_fn

    # override write_method
    self.pacq.write = self.locked_write_fn

    # acquire read lock
    self.read_lock.acquire()

    # acquire write lock
    self.write_lock.acquire()

    # start the acq
    self.pacq.start()
    #nothing should happen yet....
    
    # release lock
    self.read_lock.release()
    
    # delay
    time.sleep(0.2)
    
    # acquire lock
    self.read_lock.acquire()
    
    # check that read count increased
    read_count_increased = self.read_count > 0

    # check that polling queue contains correct number of items
    queue_is_filling = self.pacq._queue.qsize() > 0

    # release write lock
    self.write_lock.release()
    
    # join the queue, so we know it's drained before moving on
    self.pacq._queue.join()

    # make sure read_count and write_count agree
    queue_is_draining = (self.read_count == self.write_count )
    
    try:
      self.read_lock.release()
      self.write_lock.release()    
    except:
      pass

    # stop the acquisition
    self.pacq.stop()

    self.assertTrue( read_count_increased, 
      'read function was not called' )

    self.assertTrue( queue_is_filling ,
      'Queue not filling')
    
    self.assertTrue( queue_is_draining ,
      'Queue not draining')


  """
  *****************
  TEST TOOLS
  """
  read_lock = None
  write_lock = None
  read_val = None
  write_val = None
  read_count = None
  write_count = None
  
  def locked_read_fn( self ):
    """
    ---------------------------------------------------------------------------
    data read callback that can be throttled from the test
    """    
    self.read_lock.acquire()
    self.read_count += 1
    time.sleep(0.01)
    self.read_lock.release()
    

    return self.read_val

  def locked_write_fn( self,value ):
    """
    ---------------------------------------------------------------------------
    data write callback that can be throttled from the test
    """    
    self.write_lock.acquire()
    self.write_val = value
    self.write_count += 1
    time.sleep(0.01)
    self.write_lock.release()
    
    
    pass


import threading as th
import numpy as np
import copy

class RollingBuffer:
  """
  #############################################################################
  Rolling np.array with thread safe access
  """

  _lock       = None

  _timestamps = None # array of scalars containing the data timestamps
  _data       = None # array of numpy arrays containing the data
  _dimensions = None # tuple describing shape of data arrays
  _rollcount  = None # how many times data has been added 

  def __init__( self ):
    """
    ---------------------------------------------------------------------------
    Constructor
    """
    self._lock = th.Lock()
    pass

  def reset( self, length = 100, dimensions = (1) ):
    """
    ---------------------------------------------------------------------------
    reset all of the data structures
    """

    # lock up the data
    self._lock.acquire()

    # initialize the timestamps and data to proper shape and length
    self._timestamps = np.zeros( length )
    self._data = np.array([ np.zeros( dimensions ) ]*length)

    # keep track of the requested dimensions
    self._dimensions = dimensions

    # keep track of data rolls, for debugging
    self._rollcount = 0

    # unlock the data
    self._lock.release()

    pass

  def add_new( self, new_timestamp, new_data ):
    """
    ---------------------------------------------------------------------------
    Add a new data item to the buffer
    """    

    if np.rank( new_data )==1:
      if np.shape( new_data )[0] != self._dimensions:
        return False
    else:
      # make sure incoming data has correct shape
      if np.shape( new_data ) != self._dimensions:
        return False
    
    self._lock.acquire()

    # roll the arrays forward by one
    self._data = np.roll( self._data, 1 , 0 )
    self._timestamps = np.roll( self._timestamps, 1 , 0 )
    
    # insert the new data at the head 
    self._data[0] = copy.deepcopy( new_data )
    self._timestamps[0] = copy.deepcopy( new_timestamp ) 

    # increment the rollcounter
    self._rollcount += 1

    # release the lock    
    self._lock.release()
    
    return True

  def get_latest( self ):
    """
    ---------------------------------------------------------------------------
    Retrieve the latest item from the data buffer
    """

    # acquire a lock on the data 
    self._lock.acquire()

    # deepcopy the latest (first) item in the buffer
    data_out = (
      copy.deepcopy( self._timestamps[0]     ),
      copy.deepcopy( self._data[0]  )
    )
    
    # release the lock
    self._lock.release()  

    # return the data
    return data_out

  def get_all( self ):
    """
    ---------------------------------------------------------------------------
    Retrieve the full data buffer
    """ 
    
    # acquire a lock on the data 
    self._lock.acquire()

    # deepcopy the entire buffer
    data_out = (
      copy.deepcopy( self._timestamps ),
      copy.deepcopy( self._data       )
    )

    # release the lock
    self._lock.release()  
    return data_out
    
"""
###############################################################################
"""






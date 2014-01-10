import unittest
import random
import numpy as np
import threading
import pydacq.rolling_buffer 
import time

class TestRollingBuffer( unittest.TestCase ):

  def setUp( self ):
    self.rbuffer = pydacq.rolling_buffer.RollingBuffer()
    self.rbuffer.reset( 100, ( 50, 50 ) )
    pass

  def test_reset( self ): 
    # our length and dimensions
    length = 52
    dimensions = (30,40)

    # expected shapes
    data_shape = (52,30,40)
    timestamps_shape = (52)

    # reset the buffer
    self.rbuffer.reset( length = length, dimensions = dimensions )

    # should make a properly sized timestamps array
    self.assertEqual( np.shape( self.rbuffer._timestamps )[0], \
        timestamps_shape, 'incorrect size for timestamps array' )

    # should make a properly shaped data array
    self.assertEqual( np.shape( self.rbuffer._data ), data_shape, \
        'incorrect size for data array' )

    # should store dimensions
    self.assertEqual( self.rbuffer._dimensions , dimensions, \
        'incorrect dimensions' )    

    pass

  def test_add_new_rejects_bad_data( self ):
    

    data_in = np.random.rand( 12, 12 )
    time_in = time.time()
    rollcount = self.rbuffer._rollcount

    retval = self.rbuffer.add_new(time_in,data_in)
    
    self.assertFalse( retval, \
     'got TRUE from add_new in spite of bad data entry' )

    self.assertEqual( self.rbuffer._rollcount , rollcount , \
     'rollcounter incremented in spite of bad data entry')

    self.assertNotEqual( self.rbuffer._data[0], data_in, \
     'buffer accepted improperly formatted data'  )

    self.assertNotEqual( self.rbuffer._timestamps[0], time_in, \
     'buffer accepted timestamp for improperly formatted data'  )

    pass

  def test_add_new_adds_data( self ):
    data_in1 = np.random.rand( 50, 50 )
    data_in2 = np.random.rand( 50, 50 )
    time_in1 = time.time()
    time_in2 = time_in1 + 10
    
    rollcount = self.rbuffer._rollcount

    retval1 = self.rbuffer.add_new( time_in1, data_in1 )
    retval2 = self.rbuffer.add_new( time_in2, data_in2 )

    self.assertTrue( retval1, \
        'got TRUE inspite of good data entry, first time' )

    self.assertTrue( retval2, \
        'got TRUE inspite of good data entry, second time' )

    self.assertEqual( self.rbuffer._rollcount , rollcount+2 , \
        'rollcounter incorrect after data was added')

    self.assertEqual( np.sum( self.rbuffer._data[0] ), np.sum( data_in2 ), \
        'expected input data not found at correct location'  )

    self.assertEqual( self.rbuffer._timestamps[0], time_in2, \
        'expected timestamp not found at correct location'  )

    self.assertEqual( np.sum(  self.rbuffer._data[1] ), np.sum( data_in1 ), \
        'expected input data not found at correct location'  )

    self.assertEqual( self.rbuffer._timestamps[1], time_in1, \
        'expected timestamp not found at correct location'  )

  def test_add_new_holds_at_lock( self ):
    data_in1 = np.random.rand( 50, 50 )
    data_in2 = np.random.rand( 50, 50 )
    time_in1 = time.time()
    time_in2 = time_in1 + 10
    rollcount = self.rbuffer._rollcount

    def add_data():
        self.rbuffer.add_new( time_in1, data_in1 )
        pass
    
    # acquire a lock to simulate data access from another thread
    self.rbuffer._lock.acquire()

    # start a thread that adds data
    adt = threading.Thread( target = add_data )
    adt.start()

    # rollcount should not have increased
    self.assertEqual( self.rbuffer._rollcount, rollcount, \
        'rollcount increased when data was locked' )

    # release the lock to simulate other thread finishing access
    self.rbuffer._lock.release()

    # join the thread to make sure it finishes before checking data state
    adt.join()

    # rollcount should have increased
    self.assertEqual( self.rbuffer._rollcount, rollcount+1, \
        'rollcount did not increase after data was unlocked' )    

    pass

  def test_get_latest_returns_data( self ):
    
    data_array = np.random.rand( 100, 50, 50 )
    timestamps = np.arange( 0 ,100 , 1 )
    rollcount = self.rbuffer._rollcount

    # add all of the data to the buffer
    for i in range( 100 ):
        self.rbuffer.add_new( timestamps[i], data_array[ i ] )

    ret_data = self.rbuffer.get_latest()

    self.assertEqual( ret_data[0] , timestamps[ -1 ], 'timestamp was incorrect')
    self.assertEqual( np.sum( ret_data[1] ) , np.sum( data_array[ -1 ] ), 'data was incorrect')

    pass

  def test_get_all_returns_data( self ):
    data_array = np.random.rand( 100, 50, 50 )
    timestamps = np.arange( 0 ,100 , 1 )
    rollcount = self.rbuffer._rollcount

    # add all of the data to the buffer
    for i in range( 100 ):
        self.rbuffer.add_new( timestamps[i], data_array[ i ] )

    # pull the entire buffer
    ret_data = self.rbuffer.get_all()

    # set data integrity flags
    ts_ok = True
    data_ok = True

    # scan timestamps and data, unset flags if incorrect
    for i in range( 100 ):
        ts_ok   = ts_ok and (ret_data[0][i] == timestamps[ 99 - i ])
        data_ok = data_ok and (np.sum( ret_data[1][i] ) == np.sum( data_array[ 99 - i ] ))

    # check if data integrity flags are still OK
    self.assertTrue( ts_ok, 'a timestamp was incorrect')
    self.assertTrue( data_ok, 'a data item was incorrect')

    pass
  
  def test_get_latest_holds_at_lock( self ):
    data_array = np.random.rand( 100, 50, 50 )
    timestamps = np.arange( 0 ,100 , 1 )
    rollcount = self.rbuffer._rollcount

    self.ret_val = False
    def get_data_fn():
        self.ret_val = self.rbuffer.get_latest()
        

    # add all of the data to the buffer
    for i in range( 100 ):
        self.rbuffer.add_new( timestamps[i], data_array[ i ] )


    # acquire lock on the data, simulates other thread operating on data
    self.rbuffer._lock.acquire()

    # launch thread to grab data
    glt = threading.Thread( target = get_data_fn )
    glt.start()

    # make sure no data was returned
    self.assertFalse( self.ret_val , 'got data in spite of locked condition' )

    # release the lock
    self.rbuffer._lock.release()

    # join thread to ensure operation finishes before we check
    glt.join()

    # data should be available now
    self.assertFalse( not self.ret_val , 'failed to get data after unlock' )


    pass

  def test_get_all_holds_at_lock( self ):
    data_array = np.random.rand( 100, 50, 50 )
    timestamps = np.arange( 0 ,100 , 1 )
    rollcount = self.rbuffer._rollcount

    self.ret_val = False
    def get_data_fn():
        self.ret_val = self.rbuffer.get_all()

    # add all of the data to the buffer
    for i in range( 100 ):
        self.rbuffer.add_new( timestamps[i], data_array[ i ] )

    # acquire lock on the data, simulates other thread operating on data
    self.rbuffer._lock.acquire()

    # launch thread to grab data
    glt = threading.Thread( target = get_data_fn )
    glt.start()

    # make sure no data was returned
    self.assertFalse( self.ret_val , 'got data in spite of locked condition' )

    # release the lock
    self.rbuffer._lock.release()

    # join thread to ensure operation finishes before we check
    glt.join()

    # data should be available now
    self.assertFalse( not self.ret_val , 'failed to get data after unlock' )
    pass


  def tearDown( self ):
    pass

if __name__ == '__main__':
    unittest.main()
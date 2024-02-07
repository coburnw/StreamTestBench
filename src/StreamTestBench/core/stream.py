# stream.py - StramTestBench - data stream object passed between blocks

# Copyright (c) 2024 Coburn Wightman
# AGPL-3.0-or-later

import numpy as np

class Listener(object):
    """ A list of objects to alert on change
    
    Both listeners and speakers subclass the Listener class.
    
    A listener adds itself to an objects list of listeners by calling
    that objects add_listener(self) method with self as its only parameter.
    
    When the object changes, that object calls its update_listeners(self) method
    with self as its only parameter.
    
    Each listener is then alerted to the change when the
    listeners listener_update(obj) method is called with the object that
    changed as its only parameter  
    """
    
    def __init__(self):
        self.listeners = []
        return

    def add_listener(self, listener):
        # add a listener to our list of users to alert if a change
        self.listeners.append(listener.listener_update)
        return

    def update_listeners(self, obj=None):
        # call the listeners callback to signal a change
        for listener in self.listeners:
            listener(obj)

        return
    
    def listener_update(self, obj=None):
        # to be implemented by the listener.  Called by update_listeners.
        raise NotImplemented

    
class Stream(Listener):
    """ A container for periodic samples, timestamps, and associated metadata.
    
    as a subclass of listener, stream consumers can register for updates when
    the stream is changed.  Stream producers can alert consumers of a stream
    change by calling its update_listeners method when the change is complete. 
    """
    
    def __init__(self, name, dt, N, osr, dtype=np.float64):
        """

        Args:
            name (str): A stream title used in plots or debug messages
            dt (float): sample interval in secons
            N (int): total number of samples
            osr (float): over sampling ratio (f_sample/f_nyquist)
            dtype (np.dtype): the data type of the individual samples
        """
        super().__init__()
        
        self._name = name
        self._dt = dt
        self._N = N
        self._osr = osr
        self._dtype = dtype

        t_max = self.delta_t + self.sample_count * self.delta_t
        self._time_series = np.arange(self.delta_t, t_max, self.delta_t)
        self._samples = np.zeros(self.sample_count, dtype=dtype)

        return

    def update_listeners(self, obj=None):
        """ Alert stream listeners of a change in stream data.
        
        When modification is complete, a stream producer calls update_listener to
        alert all stream consumers of that change.  

        Args:
            obj: None or empty.

        Returns:

        """
        
        if obj is not None:
            raise ValueError('a stream references itself')

        super().update_listeners(self)
        return

    def __len__(self):
        return self._N

    def copy(self, new_name, dtype=None):
        """ make an empty copy of a stream
        
        allocates and returns an empty copy of this stream preserving all metadata 

        Args:
            new_name (str): name to assign to new stream.
            dtype (np.dtype): Data type to cast copy too.

        Returns:
            (Stream): A copy of self with samples initialized to zero.
        """
        if dtype is None:
            dtype = self._dtype

        new_stream = type(self)(new_name, self._dt, self._N, self._osr, dtype)
        new_stream._name = new_name

        return new_stream

    @property
    def name(self):
        """
        Returns:
            (str): Stream name
        """
        return self._name

    @property
    def dtype(self):
        """
        Returns:
            (int): dtype of sample array.
        """
        return self._samples.dtype

    @property
    def time_series(self):
        """
        Returns:
            (numpy array): of periodic time series data 
        """
        return self._time_series

    @property
    def samples(self):
        """
        Returns:
            (numpy array): array of periodic samples, aligned with time_series.
        """
        return self._samples

    @samples.setter
    def samples(self, samples):
        if len(samples) != self._N:
            raise ValueError('samples length != time_series length') 

        if samples.dtype != self.dtype:
            raise ValueError('new samples datatype ({}) does not match existing samples datatype ({})'.format(samples.dtype, self.samples.dtype))

        self._samples = samples

        return
    
    @property
    def delta_t(self):
        """
        Returns:
            (float): time in seconds between samples
        """
        return self._dt
    
    @property
    def sample_count(self):
        """
        Returns:
            (int): number of items in series arrays
        """
        return self._N
    
    @property
    def osr(self):
        """
        Returns:
            (int): Over Sampling Ratio. Number of samples per cycle of fc.
        """
        return self._osr
    
    @property
    def full_scale(self):
        """
        Returns:
            (float): Full scale value in positive direction. Typically +1.0 for float.
        """

        if self.dtype.kind == 'f':
            fs = 1.0
        elif self.dtype.kind == 'i':
            fs = 2**(self.dtype.itemsize * 8 - 1)
        elif self.dtype.kind == 'u':
            fs = 2 ** (self.dtype.itemsize * 8)
        else:
            raise TypeError('unrecognized sample type')

        return fs

    @property
    def extents(self):
        """
        The total possible range for this data type

        Returns:
            (float): possible extents of data type
        """
        if self.dtype.kind == 'u':
            extents = self.full_scale
        else:
            extents = 2 * self.full_scale

        return extents

    @property
    def max_frequency(self):
        """
        Returns:
            (float): nyquist frequency accounting for Over Sampling Ratio.
        """
        return 1/(self.delta_t*2) / self.osr


class Streams(Listener):
    def __init__(self, name):
        super().__init__()

        self.name = name
        self.streams = []
        
        return

    def __len__(self):
        return len(self.streams)
    
    def __getitem__(self, index):
        return self.streams[index]

    def listener_update(self, ignored):
        # one of our streams has changed. let downstream know
        self.update_listeners(self)

        return

    def reset(self):
        self.streams = []
        return
    
    def append(self, stream):
        self.streams.append(stream)
        stream.add_listener(self)

        return


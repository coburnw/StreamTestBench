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
    
    def __init__(self, name, dt, N, osr, bit_depth):
        super().__init__()
        
        self._name = name
        self._dt = dt
        self._N = N
        if osr < 2:
            # an osr of less than 2 corrupts spectrum calculations.  Perhaps this exception would
            # be better handled there so the user could actually see the effects of that violation
            raise ValueError('the oversampling ratio must be 2 or larger to meet the requirements of Mr Nyquist')
        self._osr = osr
        self._n_bit = bit_depth

        tmax = self.delta_t + self.sample_count * self.delta_t
        self._time_series = np.arange(self.delta_t, tmax, self.delta_t)
        self._samples = np.zeros(self.sample_count)

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

    def copy(self, new_name):
        """ make an empty copy of a stream
        
        allocates and returns an empty copy of this stream preserving all metadata 

        Args:
            new_name (str): name to assign to new stream. 

        Returns:
            (Stream): A copy of self with samples initialized to zero.
        """
        new_stream = type(self)(new_name, self._dt, self._N, self._osr, self._n_bit)
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
    def bit_count(self):
        """
        Returns:
            (int): resolution of each sample in number of bits.  0 for float (default).
        """
        return self._n_bit

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
        fs = 1.0
        
        if self.bit_count > 0:
            fs = 2**(self.bit_count - 1)  # account for sign bit

        return fs
            
    @property
    def max_frequency(self):
        """
        Returns:
            (float): maximum frequency accounting for Over Sampling Ratio.
        """
        return (1/self.delta_t) / self.osr


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


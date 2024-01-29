# dsm.py - StreamTestBench -  Models of Delta-Sigma Modulators

# Copyright (c) 2024 Coburn Wightman
# AGPL-3.0-or-later

# Copyright (c) 2018 Harnesser@github
# MIT License

import numpy as np

import StreamTestBench.core.block as block
import StreamTestBench.core.stream as stream

def run(t, vin):
    #return _dac(t, vin)
    #return _first_order(t, vin)
    #return _second_order(t, vin)
    #return _mash_1_1(t, vin)
    #return _mash_2_1(t, vin)
    #return _mash_1_1_unscaled(t, vin)
    return _first_order_unscaled(t, vin)
    #return _second_order_unscaled(t, vin)
        
class FirstOrder(block.Block):
    def __init__(self, name, input_stream):
        super().__init__('First Order DSM')

        self.v_in = input_stream

        # allocate and configure output stream
        self.result_stream = input_stream.copy(name)

        # tell stream we want to be alerted to updates
        #self.v_in.add_listener(self.listener_update)
        self.v_in.add_listener(self)

        self._testpoints = stream.Streams('Test Points') 
        return

    @property
    def testpoints(self):
        if len(self._testpoints) == 0:
            self._testpoints.append(self.v_in)

            u_stream = self.v_in.copy('v(u)') 
            self._testpoints.append(u_stream)

            y_stream = self.v_in.copy('v(y)')
            self._testpoints.append(y_stream)

        return self._testpoints
    
    def process(self, ignored_stream):
        self._testpoints.reset()
        
        vin = self.testpoints[0].samples
        u = self.testpoints[1].samples
        y = self.testpoints[2].samples
        
        for n in range(1, len(vin)):
            u[n] = 0.5 * ( vin[n] - y[n-1] ) + u[n-1]
            y[n] = ( 1.0 if u[n] > 0.0 else -1.0 )

        self.result_stream.samples = y

        return self.result_stream
        
def _first_order(t, vin):
    y = np.zeros( len(t), dtype=float)
    u = np.zeros( len(t), dtype=float)

    for n in range(1, len(vin)):
        u[n] = 0.5 * ( vin[n] - y[n-1] ) + u[n-1]
        y[n] = ( 1.0 if u[n] > 0.0 else -1.0 )

    return (vin, u, y), ('v(in)', 'v(u)', 'v(y)')

def _first_order_unscaled(t, vin):
    y = np.zeros( len(t), dtype=float)
    u = np.zeros( len(t), dtype=float)

    # vin = vin/256
    for n in range(1, len(vin)):
        u[n] = ( vin[n] - y[n-1] ) + u[n-1]
        y[n] = ( 1.0 if u[n] > 0.0 else -1.0 )

    return (vin, u, y), ('v(in)', 'v(u)', 'v(y)')


def _second_order(t, vin):
    y = np.zeros( len(t), dtype=float)
    u = np.zeros( len(t), dtype=float)
    v = np.zeros( len(t), dtype=float)

    for n in range(1, len(vin)):
        u[n] = 0.5 * ( vin[n] - y[n-1] ) + u[n-1]
        v[n] = 0.5 * ( u[n] - y[n-1] ) + v[n-1]
        y[n] = ( 1.0 if v[n] > 0.0 else -1.0 )

    return (vin, u, v, y), ('v(in)', 'v(u)', 'v(v)', 'v(y)')

def _second_order_unscaled(t, vin):
    y = np.zeros( len(t), dtype=float)
    u = np.zeros( len(t), dtype=float)
    v = np.zeros( len(t), dtype=float)

    for n in range(1, len(vin)):
        u[n] = ( vin[n] - y[n-1] ) + u[n-1]
        v[n] = ( u[n] - y[n-1] ) + v[n-1]
        y[n] = ( 1.0 if v[n] > 0.0 else -1.0 )

    return (vin, u,v, y), ('v(in)', 'v(u)', 'v(v)', 'v(y)')

def _mash_1_1_unscaled(t, vin):
    e1 = np.zeros( len(t), dtype=float)
    y2d = np.zeros( len(t), dtype=float)
    y = np.zeros( len(t), dtype=float)

    # MASH-(1)-1 : signal modulator
    (_, u1, y1), _ = _first_order_unscaled(t, vin)

    for n in range(1, len(vin)):
        e1[n] = y1[n-1] - u1[n]

    # MASH-1-(1) : noise modulator
    (_, _, y2), _ = _first_order_unscaled(t, e1)

    # reconstruction
    for n in range(1, len(vin)):
        y2d[n] = y2[n] - y2[n-1]
        y[n] = y1[n] - y2d[n]

    return (vin, e1, y), ('v(in)', 'e(1)', 'v(y)')


def _mash_1_1(t, vin):
    e1 = np.zeros( len(t), dtype=float)
    y2d = np.zeros( len(t), dtype=float)
    y = np.zeros( len(t), dtype=float)

    # MASH-(1)-1 : signal modulator
    (_, u1, y1), _ = _first_order(t, vin)

    # MASH-1-(1) : noise modulator
    for n in range(1, len(vin)):
        e1[n] = y1[n-1] - u1[n]

    (_, _, y2), _ = _first_order(t, e1)

    # reconstruction
    for n in range(1, len(vin)):
        y2d[n] = 1.0 * (y2[n] - y2[n-1])
        y[n] = y1[n] - y2d[n]

    return (vin, e1, y), ('v(in)', 'e(1)', 'v(y)')


def _mash_2_1(t, vin):
    e1 = np.zeros( len(t), dtype=float)
    y2d = np.zeros( len(t), dtype=float)
    y2dd = np.zeros( len(t), dtype=float)
    y = np.zeros( len(t), dtype=float)

    # MASH-(2)-1 : signal modulator
    (_, u1, v1, y1), _ = _second_order(t, vin)

    for n in range(1, len(vin)):
        e1[n] = y1[n-1] - u1[n]

    # MASH-2-(1) : noise modulator
    (_, _, y2), _ = _first_order(t, e1)

    # reconstruction
    for n in range(1, len(vin)):
        y2d[n] = y2[n] - y2[n-1]
        y2dd[n] = y2d[n] - y2d[n-1]
        y[n] = y1[n] - y2dd[n]

    return (vin, e1, y), ('v(in)', 'e(1)', 'v(y)')

# filters.py - StreamTestBench - IIR filter blocks
import numpy as np

# Copyright (c) 2024 Coburn Wightman
# AGPL-3.0-or-later

import StreamTestBench.core.block as block


class IntegerIIR(block.Block):
    # https://electronics.stackexchange.com/a/30384
    def __init__(self, name, input_stream, filter_factor):
        super().__init__('First Order Integer IIR')
        
        self.input_stream = input_stream
        self.result_stream = input_stream.copy(name)
        self.filter_factor = filter_factor

        # ask input_stream to alert us to any updates
        self.input_stream.add_listener(self)

        return

    def process(self, ignored_stream):
        filter_value = 0.001

        self.result_stream.samples[0] = filter_value

        for i in range(1, self.input_stream.sample_count):
            filter_value += (self.input_stream.samples[i] - filter_value) / self.filter_factor
            self.result_stream.samples[i] = filter_value

        return self.result_stream

    
class FloatIIR(block.Block):
    def __init__(self, name, input_stream, cutoff_frequency):
        super().__init__('First Order IIR')

        self.input_stream = input_stream
        self.result_stream = input_stream.copy(name)
        self.cutoff_frequency = cutoff_frequency

        # ask input_stream to alert us to any updates
        self.input_stream.add_listener(self)
        self.cutoff_frequency.add_listener(self)

        return

    def process(self, ignored_stream):
        # https://electronics.stackexchange.com/a/31907
        # One-time calculations(can be pre-calculated at compile-time and loaded with constants)
        decay_factor = np.exp(-2.0 * np.pi * self.cutoff_frequency.value * self.input_stream.delta_t)
        amplitude_factor = (1.0 - decay_factor)

        # Filter Loop Function ----- THIS IS IT -----
        moving_average = 0.0
        for i in range(0, self.input_stream.sample_count):
            moving_average *= decay_factor
            moving_average += amplitude_factor * self.input_stream.samples[i]
            self.result_stream.samples[i] = moving_average

        return self.result_stream

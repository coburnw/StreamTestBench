# multipole.py - StreamTestBench -  A model of an IIR filter

# Copyright (c) 2024 Coburn Wightman
# AGPL-3.0-or-later

import importlib
import numpy as np

import StreamTestBench.core.stream as stream
import StreamTestBench.core.block as block
# import StreamTestBench.blocks.math as math
import StreamTestBench.blocks.filters as filters
import StreamTestBench.gui.bench as bench
import StreamTestBench.gui.sources as sources
import StreamTestBench.gui.sinks as sinks
import StreamTestBench.gui.parameters as parameters


def reload():
    print('reloading filters')
    importlib.reload(filters)
    return


class Shift(block.Block):
    def __init__(self, name, input_stream, shift_count):
        super().__init__('Shift')
        self.input_stream = input_stream
        self.result_stream = input_stream.copy(name)
        self.shift_value = 2**shift_count

        self.input_stream.add_listener(self)
        return

    def process(self, junk):
        if self.shift_value > 0:
            np.multiply(self.input_stream.samples, self.shift_value, out=self.result_stream.samples, casting='unsafe')
        elif self.shift_value < 0:
            np.divide(self.input_stream.samples, self.shift_value, out=self.result_stream.samples, casting='unsafe')
            # self.result_stream.samples = np.right_shift(self.p2.stream.samples, shift_value).astype(np.int8)
        else:
            self.result_stream.samples = self.input_stream.samples

        return self.result_stream


class Cast(block.Block):
    def __init__(self, name, input_stream, dtype):
        super().__init__('Resize')

        self.input_stream = input_stream
        self.result_stream = input_stream.copy(name, dtype=dtype)

        self.input_stream.add_listener(self)
        return

    def process(self, junk):
        np.copyto(self.result_stream.samples, self.input_stream.samples, casting='unsafe')
        return self.result_stream


class ThreePoleIIR(block.Block):
    def __init__(self, name, input_stream, filter_parameter, pole_parameter):
        super().__init__('MultiPole Integer IIR')

        self.input_stream = input_stream
        self.result_stream = input_stream.copy(name)
        self.filter_factor = filter_parameter
        self.pole_count = pole_parameter

        self.p1 = filters.IntegerIIR('p1', self.input_stream, self.filter_factor)
        self.p2 = filters.IntegerIIR('p2', self.p1.stream, self.filter_factor)
        self.p3 = filters.IntegerIIR('p3', self.p2.stream, self.filter_factor)

        # register with sources to alert us to any change
        self.pole_count.add_listener(self)
        self.p3.stream.add_listener(self)
        return

    def process(self, event):
        # print(type(event))
        samples = self.input_stream.samples
        if self.pole_count.value == 1:
            samples = self.p1.stream.samples
        elif self.pole_count.value == 2:
            samples = self.p2.stream.samples
        elif self.pole_count.value == 3:
            samples = self.p3.stream.samples

        # copy the result of the selected order to the result stream
        self.result_stream.samples = samples
        return self.result_stream


if __name__ == '__main__':

    # assign stream parameters
    fc = 60            # frequency of interest in hz
    osr = 32           # over sampling ratio. (f_sampling / f_nyquist)
    dt = 1/(fc*2)/osr  # sample interval accounting for both nyquist and osr
    N = 2048           # stream sample count
    dtype = np.int8   # numpy dtype: np.int8, np.int16, np.int32, np.float64

    # the stream all others are based on
    stream_template = stream.Stream('default', dt, N, osr, dtype)

    # configure sources
    signal = sources.FunctionGenerator('Signal', stream_template, offset=0, max_frequency=2*fc)
    signal.shape = 'sine'

    noise = sources.FunctionGenerator('Noise', stream_template)
    noise.shape = 'random'

    # --- wire in our dut process
    channel = signal  # math.Add('S+N', signal.stream, noise.stream)

    valstep = [0,1,2,3,4,5,6,7,8]
    filter_setting = parameters.SliderParameter('Cutoff', min_val=0, max_val=8, valstep=valstep)

    polestep = [0,1,2,3]
    pole_setting = parameters.SliderParameter('Poles', min_val=0, max_val=3, valstep=polestep)

    shift_count = 7
    resized_input = Cast('int16', channel.stream, np.int16)
    filter_input = Shift('shift_left', resized_input.stream, shift_count)

    filter_output = ThreePoleIIR('3p', filter_input.stream, filter_setting.parameter, pole_setting.parameter)

    shifted_output = Shift('shift_right', filter_output.stream, -shift_count)
    result = Cast('int8', shifted_output.stream, np.int8)

    dut = result

    # filter_setting = parameters.SliderParameter('Cutoff Frequency', 100, 5000)
    # dut = filters.FloatIIR('filtered', channel.stream, filter_setting.parameter)

    testpoints = stream.Streams('sig+noise')
    testpoints.append(signal.stream)
    testpoints.append(noise.stream)
    testpoints.append(channel.stream)
    testpoints.append(dut.stream)

    # configure sinks
    xy1 = sinks.XYDisplay(dut.stream)
    sa1 = sinks.SpectrumAnalyzer(dut.stream)
    tp1 = sinks.TestPoints(testpoints)

    # Layout Test Bench Display
    test_bench = bench.Bench('Stream Testbench')
    test_bench.on_reset(reload)

    top_shelf = bench.Shelf('Output', height=1)
    top_shelf.append(xy1, width=1.0)
    top_shelf.append(sa1, width=1.0)
    test_bench.append(top_shelf)

    mid_shelf = bench.Shelf('Process', height=1)
    mid_shelf.append(filter_setting, width=0.10)
    mid_shelf.append(pole_setting, width=0.10)
    mid_shelf.append(tp1, width=1.0)
    test_bench.append(mid_shelf)

    bot_shelf = bench.Shelf('Input', height=1)
    bot_shelf.append(signal, width=1.0)
    bot_shelf.append(noise, width=1.0)
    test_bench.append(bot_shelf)

    test_bench.activate(dut.name)


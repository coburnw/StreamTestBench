# filter.py - StreamTestBench -  A model of an IIR filter

# Copyright (c) 2024 Coburn Wightman
# AGPL-3.0-or-later

import importlib
import numpy as np

import StreamTestBench.core.stream as stream
import StreamTestBench.blocks.math as math
import StreamTestBench.blocks.filters as filters
import StreamTestBench.gui.bench as bench
import StreamTestBench.gui.sources as sources
import StreamTestBench.gui.sinks as sinks
import StreamTestBench.gui.parameters as parameters


def reload():
    print('reloading filters')
    importlib.reload(filters)
    return


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
    channel = signal # math.Add('S+N', signal.stream, noise.stream)

    valstep = [0,1,2,3,4,5,6,7,8]
    filter_setting = parameters.SliderParameter('Window Factor', min_val=0, max_val=8, valstep=valstep)
    dut = filters.IntegerIIR('filtered', channel.stream, filter_setting.parameter)

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
    mid_shelf.append(filter_setting, width=0.20)
    mid_shelf.append(tp1, width=1.0)
    test_bench.append(mid_shelf)

    bot_shelf = bench.Shelf('Input', height=1)
    bot_shelf.append(signal, width=1.0)
    bot_shelf.append(noise, width=1.0)
    test_bench.append(bot_shelf)

    test_bench.activate(dut.name)

    

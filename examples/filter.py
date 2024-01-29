# filter.py - StreamTestBench -  A model of an IIR filter

# Copyright (c) 2024 Coburn Wightman
# AGPL-3.0-or-later

import importlib

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
    fc = 1000      # frequency of interest in hz
    osr = 32       # over sampling ratio. number of samples per cycle of fc
    dt = 1/fc/osr  # time in seconds between samples
    N = 2048       # stream sample count
    n_bit = 0      # integer sample resolution in number of bits, 0=float

    # the stream all others are based on
    stream_template = stream.Stream('default', dt, N, osr, n_bit)

    # configure sources
    signal = sources.FunctionGenerator('Signal', stream_template, offset=0.0)
    signal.shape = 'sine'
    
    noise = sources.FunctionGenerator('Noise', stream_template)
    noise.shape = 'random'

    # --- wire in our dut process
    testpoints = stream.Streams('sig+noise')
    testpoints.append(signal.stream)
    testpoints.append(noise.stream)
    
    channel = math.Add('channel', signal.stream, noise.stream)
    testpoints.append(channel.stream)

    cutoff_frequency = parameters.SliderParameter('Cutoff Frequency', 100, 1000)
    dut = filters.FloatIIR('filtered', channel.stream, cutoff_frequency.parameter)

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
    mid_shelf.append(cutoff_frequency, width=0.20)
    mid_shelf.append(tp1, width=1.0)
    test_bench.append(mid_shelf)

    bot_shelf = bench.Shelf('Input', height=1)
    bot_shelf.append(signal, width=1.0)
    bot_shelf.append(noise, width=1.0)
    test_bench.append(bot_shelf)

    test_bench.activate(dut.name)

    

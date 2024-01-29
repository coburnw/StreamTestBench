# bridge.py - StreamTestBench -  A model of a full wave bridge

# Copyright (c) 2024 Coburn Wightman
# AGPL-3.0-or-later

import StreamTestBench.core.stream as stream
import StreamTestBench.blocks.math as math
import StreamTestBench.blocks.filters as filters
import StreamTestBench.gui.bench as bench
import StreamTestBench.gui.sinks as sinks
import StreamTestBench.gui.sources as sources

if __name__ == '__main__':

    # assign stream parameters
    fc = 60        # frequency of interest in hz
    osr = 128      # over sampling ratio. number of samples per cycle of fc
    dt = 1/fc/osr  # time in seconds between samples
    N = 2048       # stream sample count
    n_bit = 0      # integer sample resolution in number of bits, 0=float

    # the stream all others are based on
    stream_template = stream.Stream('default', dt, N, osr, n_bit)

    # configure sources
    carrier = sources.FunctionGenerator('Carrier', stream_template)
    carrier.shape = 'sine'
    
    modulation = sources.FunctionGenerator('Modulation', stream_template)
    modulation.shape = 'triangle'

    # --- wire in our dut process
    testpoints = stream.Streams('full-wave rectifier')
    testpoints.append(carrier.stream)

    rectifier = math.Absolute('rectified', carrier.stream)
    testpoints.append(rectifier.stream)

    dut = filters.FloatIIR('filtered', rectifier.stream, 25)
    testpoints.append(dut.stream)

    # configure sinks
    xy1 = sinks.XYDisplay(dut.stream)
    sa1 = sinks.SpectrumAnalyzer(dut.stream)
    tp1 = sinks.TestPoints(testpoints)

    # Layout Test Bench Display
    test_bench = bench.Bench('Stream Testbench')

    top_shelf = bench.Shelf('Output', height=1)
    top_shelf.append(xy1, width=1.0)
    top_shelf.append(sa1, width=1.0)
    test_bench.append(top_shelf)

    if len(tp1) > 0:
        mid_shelf = bench.Shelf('Process', height=1)
        mid_shelf.append(tp1, width=1.0)
        test_bench.append(mid_shelf)

    bot_shelf = bench.Shelf('Input', height=1)
    bot_shelf.append(carrier, width=1.0)
    bot_shelf.append(bench.BlankPanel(), width=1.0)
    test_bench.append(bot_shelf)

    test_bench.activate(dut.name)
    

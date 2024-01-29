# analysis.py - StreamTestBench -  Delta Sigma Modulator visualization

# Copyright (c) 2024 Coburn Wightman
# AGPL-3.0-or-later

# Copyright (c) 2018 Harnesser@github
# MIT License

import importlib

import StreamTestBench.core.stream as stream
import StreamTestBench.blocks.dsm as dsm
import StreamTestBench.gui.bench as bench
import StreamTestBench.gui.sources as sources
import StreamTestBench.gui.sinks as sinks

def reload():
    print('reloading dsm')
    importlib.reload(dsm)
    return


if __name__ == '__main__':

    # assign stream parameters
    fc = 60        # frequency of interest in hz
    osr = 32       # over sampling ratio. number of samples per cycle of fc
    dt = 1/fc/osr  # time in seconds between samples
    N = 2048       # stream sample count
    n_bit = 0      # integer sample resolution in number of bits, 0=float

    # construct a stream template from which each stream is copied from
    stream_template = stream.Stream('default', dt, N, osr, n_bit)

    # configure sources
    vin = sources.FunctionGenerator('v(in)', stream_template)
    vin.shape = 'sine'
    
    # --- wire in our dut block
    dut = dsm.FirstOrder('v(out)', vin.stream)

    # configure sinks
    xy1 = sinks.XYDisplay(dut.stream)
    sa1 = sinks.SpectrumAnalyzer(dut.stream)
    tp1 = sinks.TestPoints(dut.testpoints)

    # Layout Test Bench Display
    test_bench = bench.Bench('Stream Testbench')
    test_bench.on_reset(reload)

    top_shelf = bench.Shelf('Output', height=1)
    top_shelf.append(xy1, width=1.0)
    top_shelf.append(sa1, width=1.0)
    test_bench.append(top_shelf)

    if len(tp1) > 0:
        mid_shelf = bench.Shelf('Process', height=1)
        mid_shelf.append(tp1, width=1.0)
        test_bench.append(mid_shelf)

    bot_shelf = bench.Shelf('Input', height=1)
    bot_shelf.append(vin, width=1.0)
    bot_shelf.append(bench.BlankPanel(), width=1.0)
    test_bench.append(bot_shelf)

    test_bench.activate(dut.name)
    

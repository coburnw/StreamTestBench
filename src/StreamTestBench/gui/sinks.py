# sinks.py - StreamTestBench - Stream consumers, typically instruments with displays

# Copyright (c) 2024 Coburn Wightman
# AGPL-3.0-or-later

# Copyright (c) 2018 Harnesser@github
# MIT License

import numpy as np

import StreamTestBench.gui.bench as bench

class SpectrumPanel(bench.Panel):
    def __init__(self):
        super().__init__()
        
        self.osr = 32

        return
    
    def place_on(self, figure):
        self.fig = figure
        
        self.ax = self.fig.add_subplot() # FFT of bitstream
        self.ax.set_xscale('log')
        # ax.set_ylim(-140, 0)

        return

    def update(self, stream):
        self.ax.clear()
        (ms_spec, ms_freqs, trace ) = self.ax.magnitude_spectrum(
            stream.samples,
            Fs=1.0/stream.delta_t,
            window = np.ones(stream.samples.shape),
            scale='dB',
            linewidth=0.4)

        # Calculate bandwidth and snr
        f_bw, snr = self._snr(ms_spec, ms_freqs, stream.osr)

        # attach the vertical bandwidth line
        self.ax.axvline(x=f_bw, alpha=0.75, color='lightgrey', zorder=0)

        # add title
        title = "SNR = {:0.2f}dB, OSR = {}".format(snr, stream.osr)
        self.ax.set_title(title)

        return

    def _snr(self, mg_spec, mg_freqs, osr):
        """ Get SNR in basband """
        # input is single-sided
        # assume coherent input signal so power in 1 bin
        N = len(mg_spec)
        #print(N)

        # Bandwidth
        bwi = int(np.ceil(N/osr))
        f_bw = mg_freqs[bwi]

        # total power
        boi_spec = mg_spec[:bwi]
        total_power = boi_spec ** 2.0
        
        # signal
        signal_index = np.argmax(total_power)
        signal_power = total_power[signal_index]
        
        # noise
        total_power[signal_index] = 0.0
        noise_power = sum(total_power)

        # ratio
        snr = 20.0 * np.log10(signal_power/noise_power)
        
        return f_bw, snr

            
class SpectrumAnalyzer(SpectrumPanel):
    def __init__(self, stream):
        super().__init__()

        self.stream = stream
        self.stream.add_listener(self)
        
        return

            
class XYDisplay(bench.Panel):
    def __init__(self, stream):
        super().__init__()
        
        self.stream = stream

        self.fig = None
        self.trace = None
        
        return

    def place_on(self, figure):
        self.fig = figure
        
        axplot = self.fig.add_subplot()
        axplot.set_title(self.stream.name)

        fs = self.stream.full_scale * 1.1  # give a little margin
        axplot.set_ylim(bottom=-fs, top=fs)
        self.trace, = axplot.step(self.stream.time_series,
                                  self.stream.samples,
                                  lw=2, color='red')

        self.stream.add_listener(self)

        return

    def update(self, stream):
        self.trace.set_ydata(stream.samples)
        self.fig.canvas.draw_idle()

        return
    
class TestPoints(bench.Panel):
    def __init__(self, streams):
        super().__init__()
        
        self.streams = streams

        self.fig = None
        self.curves = None
        self.delta_row = None
        
        return

    def __len__(self):
        if self.streams is None:
            return 0

        return len(self.streams)
    
    def place_on(self, figure):
        self.fig = figure

        # build plot itself
        axplot = self.fig.add_subplot()
        axplot.set_title(self.streams.name)
        
        # determine row spacing
        # axplot.set_xlim(0, Tmax)
        dmin = -2  # data.min()
        dmax = 2  # data.max()
        self.delta_row = (dmax - dmin) * 0.7  # Crowd them a bit.

        numRows = len(self.streams)
        y0 = dmin
        y1 = (numRows - 1) * self.delta_row + dmax
        
        self.curves = []
        names = []
        tick_locations = []
        for i in range(numRows):
            names.append(self.streams[i].name)
            tick_locations.append( i*self.delta_row)

            t = self.streams[i].time_series
            offset_data = self.streams[i].samples + (i*self.delta_row)
            curve, = axplot.step(t, offset_data, linewidth=0.5)
            self.curves.append(curve)

        # Set the yticks to use axes coordinates on the y axis
        axplot.set_ylim(y0, y1)
        axplot.set_yticks(tick_locations)
        axplot.set_yticklabels(names)
        axplot.set_xlabel('Time (s)')

        self.streams.add_listener(self)
        
        return

    def update(self, streams):
        for i in range(0, len(self.curves)):
            offset_data = streams[i].samples + (i*self.delta_row)
            self.curves[i].set_ydata(offset_data)
            
        self.fig.canvas.draw_idle()
        
        return
    

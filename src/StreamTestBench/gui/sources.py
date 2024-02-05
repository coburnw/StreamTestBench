# sources.py - StreamTestBench - Stream sources like function generators

# Copyright (c) 2024 Coburn Wightman
# AGPL-3.0-or-later

# Copyright (c) 2018 Harnesser@github
# MIT License

# import numpy as np

from matplotlib.widgets import Slider, RadioButtons

import StreamTestBench.gui.bench as bench
import StreamTestBench.gui.sinks as sinks
import StreamTestBench.core.waveform as waveform


class FunctionGenerator(bench.Panel):
    def __init__(self, name, template_stream, shape='sine', offset=0):
        super().__init__()
        
        self.stream = template_stream.copy(name)
        self.sfreq = None
        self.samp = None

        self._shape = shape
        self._shapes = ['sine', 'square', 'triangle', 'random', 'pulse']

        self._offset = offset
        self.shape = shape

        return

    @property
    def shape(self):
        return self._shape

    @shape.setter
    def shape(self, shape):

        if shape == 'sine':
            self.gen = waveform.SineWaveForm(self.stream, self._offset)
        elif shape == 'square':
            self.gen = waveform.SquareWaveForm(self.stream, self._offset)
        elif shape == 'triangle':
            self.gen = waveform.TriangleWaveForm(self.stream, self._offset)
        elif shape == 'random':
            self.gen = waveform.RandomWaveForm(self.stream, self._offset)
        elif shape == 'pulse':
            self.gen = waveform.PulseWaveForm(self.stream, self._offset)
        else:
            err_str = "'{}'. Unrecognized waveform shape. Expected one of {}.".format(self._shape, self._shapes)
            raise ValueError(err_str)

        self._shape = shape

        return
    
    def place_on(self, figure):
        figs = figure.subfigures(nrows=2, ncols=2,
                                 height_ratios=[4, 1],
                                 width_ratios=[4, 1])

        self.xy = sinks.XYDisplay(self.stream)
        self.xy.place_on(figs[0][0])

        fig = figs[1][0]
        axcolor = 'lightgoldenrodyellow'
        axfreq = fig.add_axes([0.15, 0.4, 0.65, 0.2], facecolor=axcolor)
        axamp = fig.add_axes([0.15, 0.7, 0.65, 0.2], facecolor=axcolor)

        f0 = 0.3 * self.gen.max_frequency
        a0 = 0.8 * self.gen.max_amplitude
        self.sfreq = Slider(axfreq, 'Freq', 0.0, self.gen.max_frequency*2, valinit=f0)
        self.samp = Slider(axamp, 'Amp', 0.0, self.gen.max_amplitude, valinit=a0)
        self.sfreq.on_changed(self.slider_change)
        self.samp.on_changed(self.slider_change)

        fig = figs[0][1]
        ax = fig.add_axes([0.0, 0.1, 0.9, 0.8], facecolor=axcolor)
        ax.set_facecolor(axcolor)
        shape_index = self._shapes.index(self.shape)
        self.radio = RadioButtons(ax, self._shapes, active=shape_index)
        self.radio.on_clicked(self.wave_change)

        # force an update to load display
        self.slider_change()
        return

    def wave_change(self, event):
        print(event)
        self.shape = event

        self.slider_change()
        return

    def slider_change(self, event=None):
        amp = self.samp.val
        freq = self.sfreq.val

        stream = self.gen.generate(freq, amp)
        stream.update_listeners()

        return
    
    def reset(self, event):
        self.sfreq.reset()
        self.samp.reset()
        return


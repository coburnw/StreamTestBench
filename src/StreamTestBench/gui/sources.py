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

class Generator(bench.Panel):
    def __init__(self, name, template_stream):
        super().__init__()
        
        self.stream = template_stream.copy(name)
        self._gen = None

        self._xy_display = None
        self._x_slider = None
        self._y_slider = None
        self._x_param_name = 'X Param'
        self._y_param_name = 'Y Parm'
        self._max_x = None
        self._max_y = None

        self._shape = None
        self._shape_buttons = None
        self._shapes = []

        return

    @property
    def shape(self):
        return self._shape

    @shape.setter
    def shape(self, shape):
        self._gen = self.generator(shape)
        self._shape = shape

        if self._x_slider is not None:
            self._x_slider.valmax = self._max_x
            self._x_slider.ax.set_xlim(self._x_slider.valmin, self._x_slider.valmax)
            self._x_slider.set_val(self._max_x/2)

        return

    def generator(self, shape):
        raise NotImplementedError

    def place_on(self, figure):
        figs = figure.subfigures(nrows=2, ncols=2,
                                 height_ratios=[4, 1],
                                 width_ratios=[4, 1])

        self._xy_display = sinks.XYDisplay(self.stream)
        self._xy_display.place_on(figs[0][0])

        fig = figs[1][0]
        ax_color = 'lightgoldenrodyellow'
        _x_param_axes = fig.add_axes([0.15, 0.4, 0.65, 0.2], facecolor=ax_color)
        _y_param_axes = fig.add_axes([0.15, 0.7, 0.65, 0.2], facecolor=ax_color)

        default_x = 0.3 * self._max_x
        default_y = 0.8 * self._max_y

        self._x_slider = Slider(_x_param_axes, self._x_param_name, 0.0, self._max_x, valinit=default_x)
        self._y_slider = Slider(_y_param_axes, self._y_param_name, 0.0, self._max_y, valinit=default_y)
        self._x_slider.on_changed(self._slider_change)
        self._y_slider.on_changed(self._slider_change)

        fig = figs[0][1]
        ax = fig.add_axes([0.0, 0.1, 0.9, 0.8], facecolor=ax_color)
        ax.set_facecolor(ax_color)
        shape_index = self._shapes.index(self.shape)
        self._shape_buttons = RadioButtons(ax, self._shapes, active=shape_index)
        self._shape_buttons.on_clicked(self._shape_change)

        # force an update to load display
        self._shape_change(self._shape)
        return

    def _shape_change(self, event):
        print(event)
        self.shape = event

        self._slider_change()
        return

    def _slider_change(self, event=None):
        x_val = self._x_slider.val
        y_val = self._y_slider.val

        stream = self._gen.generate(x_val, y_val)
        stream.update_listeners()

        return
    
    def reset(self, event):
        self._x_slider.reset()
        self._y_slider.reset()
        return


class FunctionGenerator(Generator):
    def __init__(self, name, template_stream, shape='sine', offset=0, max_frequency=None):
        super().__init__(name, template_stream)

        self._x_param_name = 'Frequency'
        self._y_param_name = 'Amplitude'

        self._max_x = max_frequency
        self._max_y = None

        self._shapes = ['sine', 'square', 'triangle', 'random']
        self._offset = offset

        self._shape = shape

        return

    def generator(self, shape):
        if shape not in self._shapes:
            err_str = "'{}'. Unrecognized waveform shape. Expected one of {}.".format(self._shape, self._shapes)
            raise ValueError(err_str)

        gen = None
        if shape == 'sine':
            gen = waveform.SineWave(self.stream, self._offset)
        elif shape == 'square':
            gen = waveform.SquareWave(self.stream, self._offset)
        elif shape == 'triangle':
            gen = waveform.TriangleWave(self.stream, self._offset)
        elif shape == 'random':
            gen = waveform.RandomWave(self.stream, self._offset)

        self._max_x = gen.max_frequency
        self._max_y = gen.max_amplitude

        return gen


class PulseGenerator(Generator):
    def __init__(self, name, template_stream, shape='rectangle', offset=0, max_width=1):
        super().__init__(name, template_stream)

        self._x_param_name = 'Width'
        self._y_param_name = 'Amplitude'

        self._max_x = max_width
        self._max_y = None

        self._shapes = ['rectangle', 'sinc', 'step']
        self._offset = offset

        self._shape = shape

        return

    def generator(self, shape):
        if shape not in self._shapes:
            err_str = "'{}'. Unrecognized pulse shape. Expected one of {}.".format(self._shape, self._shapes)
            raise ValueError(err_str)

        gen = None
        if shape == 'rectangle':
            gen = waveform.RectanglePulse(self.stream, self._offset)
        elif shape == 'sinc':
            gen = waveform.SincPulse(self.stream, self._offset)
        elif shape == 'step':
            gen = waveform.StepPulse(self.stream, self._offset)

        self._max_x = gen.max_width
        self._max_y = gen.max_amplitude

        return gen


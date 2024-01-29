# parameters.py - StreamTestBench -

# Copyright (c) 2024 Coburn Wightman
# AGPL-3.0-or-later

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from matplotlib.transforms import Bbox
from StreamTestBench.core.stream import Listener
import StreamTestBench.gui.bench as bench

class Parameter(Listener):
    """
    a variable that remains constant through a single stream process.
    A single element analog to stream.
    """

    def __init__(self, name, value=1):
        super().__init__()

        self._name = name
        self._value = value

        return

    def update_listeners(self, obj=None):
        """ Alert listeners of a change to parameter value.

        Subclass calls update_listener to alert all consumers of change in value.

        Args:
            obj: None or empty.

        Returns:

        """

        if obj is not None:
            raise ValueError('a parameter references itself')

        super().update_listeners(self)
        return

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        self.update_listeners()

        return


class SliderParameter(bench.Panel):
    def __init__(self, name, min_val, max_val):
        super().__init__()

        self.min_val = min_val
        self.max_val = max_val

        default_value = (max_val + min_val) / 2
        self.parameter = Parameter(name, default_value)

        return

    @property
    def value(self):
        return self.parameter.value

    def place_on(self, figure):
        fig = figure.subfigures(nrows=1, ncols=1, height_ratios=[1])
                                 # wspace=0.1, hspace=0.1)

        # fig = figs[0]

        axcolor = 'lightgoldenrodyellow'
        box = Bbox.from_bounds(0.45, 0.15, 0.1, 0.7)
        ax = fig.add_axes(box, facecolor=axcolor)

        self.slider = Slider(ax, self.parameter.name, self.min_val, self.max_val,
                           valinit=self.parameter.value, orientation='vertical')
        self.slider.on_changed(self.slider_change)

        # force an update to load display
        self.slider_change()
        return

    def slider_change(self, event=None):
        self.parameter.value = self.slider.val

        return

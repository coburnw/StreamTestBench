# source.py - StreamTestBench - Base class for stream based signal sources

# Copyright (c) 2024 Coburn Wightman
# AGPL-3.0-or-later

import numpy as np


class Source():
    def __init__(self, stream):
        self._stream = stream

        return

    @property
    def full_scale(self):
        return self._stream.full_scale

    @property
    def sample_count(self):
        return self._stream.sample_count

    @property
    def delta_t(self):
        return self._stream.delta_t

    @property
    def max_frequency(self):
        return self._stream.max_frequency

    @property
    def max_amplitude(self):
        return self._stream.full_scale

    def phase_series(self, frequency):
        # this is an accumulation of phase thru total time_series
        # perhaps this should be converted to a repeating phase instead?
        float_array = 2 * np.pi * frequency * self._stream.time_series
        return float_array

    def amplitude_series(self, frequency):
        raise NotImplemented

    def generate(self, frequency, amplitude):
        raise NotImplemented

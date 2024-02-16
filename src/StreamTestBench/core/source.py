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
    def max_amplitude(self):
        return self._stream.full_scale

    def amplitude_series(self, frequency):
        raise NotImplemented

    def generate(self, frequency, amplitude):
        raise NotImplemented

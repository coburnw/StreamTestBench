# waveform.py - StreamTestBench - Various stream waveforms for signal generation

# Copyright (c) 2024 Coburn Wightman
# AGPL-3.0-or-later

import numpy as np
import StreamTestBench.core.source as source


class WaveForm(source.Source):
    def __init__(self, stream, offset=0):
        super().__init__(stream)

        self._frequency = 1
        self._amplitude = 1
        self._offset = offset

        return

    @property
    def frequency(self):
        return self._frequency

    @property
    def amplitude(self):
        return self._amplitude

    @property
    def offset(self):
        return self._offset

    def sine_series(self, frequency):
        # Many periodic signals are derived from a sine. compute a sine series with peak value of full-scale
        float_array = np.sin(self.phase_series(frequency)) * self._stream.full_scale
        return float_array

    def amplitude_series(self, frequency):
        raise NotImplemented

    def generate(self, frequency, amplitude):
        # frequency in cycles per second
        # amplitude in fraction of full-scale
        self._frequency = frequency
        self._amplitude = amplitude

        # compute an input signal with peak value of full-scale
        float_array = self.amplitude_series(frequency)

        if self._stream.bit_count == 0:
            # float scale to amplitude
            v_array = float_array * self._amplitude + self._offset
        else:
            # use integer math to scale to amplitude
            int_array = float_array.astype(int) * int(self._amplitude)
            v_array = np.right_shift(int_array, self._stream.bit_count)

        self._stream.samples = v_array

        return self._stream

class SineWaveForm(WaveForm):
    def amplitude_series(self, frequency):
        float_array = self.sine_series(frequency)
        return float_array


class SquareWaveForm(WaveForm):
    def amplitude_series(self, frequency):
        float_array = np.sign(self.sine_series(frequency))
        return float_array


class TriangleWaveForm(WaveForm):
    def amplitude_series(self, frequency):
        # https://stackoverflow.com/a/19374586
        float_array = (2 / np.pi) * np.arcsin(self.sine_series(frequency))
        return float_array


class RandomWaveForm(WaveForm):
    def amplitude_series(self, frequency=None):
        float_array = np.random.uniform(-1, 1, size=self._stream.sample_count)
        return float_array


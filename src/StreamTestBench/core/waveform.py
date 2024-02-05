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
        # Many periodic signals are derived from a sine. compute a sine series with range +/- 1
        float_array = np.sin(self.phase_series(frequency))
        return float_array

    def amplitude_series(self, frequency):
        """
        calculate a proto waveform specific to this generator.

        Args:
            frequency: Waveform frequency
        Returns:
            (numpy float array): array of amplitude values with range of +/- 1
        """
        raise NotImplemented

    def generate(self, frequency, amplitude):
        """
        Generates a waveform given its frequency and amplitude

        Args:
            frequency: frequency of waveform in Hertz
            amplitude: scale value of waveform with range of 0 to full_scale

        Returns:
            (Stream): the resulting waveform (uint broken)
        """
        self._frequency = frequency
        self._amplitude = amplitude

        # compute an input signal with peak value of full-scale. cast to output array dtype
        float_array = self.amplitude_series(frequency)
        np.multiply(float_array, self._amplitude, out=self._stream.samples, casting='unsafe')

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


class PulseWaveForm(WaveForm):
    def amplitude_series(self, frequency=None):
        float_array = np.zeros(self._stream.sample_count)
        float_array[int(self._stream.sample_count/2)] = 1
        return float_array

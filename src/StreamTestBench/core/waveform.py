# waveform.py - StreamTestBench - Various stream waveforms for signal generation

# Copyright (c) 2024 Coburn Wightman
# AGPL-3.0-or-later

import numpy as np
import StreamTestBench.core.source as source


class Wave(source.Source):
    def __init__(self, stream, offset=0):
        super().__init__(stream)

        self._frequency = 1
        self._amplitude = 1
        self._offset = offset

        return

    @property
    def amplitude(self):
        return self._amplitude

    @property
    def offset(self):
        return self._offset

    @property
    def frequency(self):
        return self._frequency

    @property
    def max_frequency(self):
        return self._stream.max_frequency

    def phase_series(self, frequency):
        # this is an accumulation of phase thru total time_series
        # perhaps this should be converted to a repeating phase instead?
        float_array = 2 * np.pi * frequency * self._stream.time_series
        return float_array

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


class SineWave(Wave):
    def amplitude_series(self, frequency):
        float_array = self.sine_series(frequency)
        return float_array


class SquareWave(Wave):
    def amplitude_series(self, frequency):
        float_array = np.sign(self.sine_series(frequency))
        return float_array


class TriangleWave(Wave):
    def amplitude_series(self, frequency):
        # https://stackoverflow.com/a/19374586
        float_array = (2 / np.pi) * np.arcsin(self.sine_series(frequency))
        return float_array


class RandomWave(Wave):
    def amplitude_series(self, frequency=None):
        float_array = np.random.uniform(-1, 1, size=self._stream.sample_count)
        return float_array


class Pulse(source.Source):
    def __init__(self, stream, offset=0):
        super().__init__(stream)

        self._width = 1
        self._amplitude = 1
        self._offset = offset

        return

    @property
    def width(self):
        """

        Returns:
            Width of pulse in number of samples

        """
        return self._width

    @property
    def max_width(self):
        return int(self._stream.sample_count / 10)

    @property
    def offset(self):
        return self._offset

    @property
    def amplitude(self):
        return self._amplitude

    def amplitude_series(self, frequency):
        """
        calculate a proto waveform specific to this generator.

        Args:
            frequency: Waveform frequency
        Returns:
            (numpy float array): array of amplitude values with range of +/- 1
        """
        raise NotImplemented

    def generate(self, width, amplitude):
        """
        Generates a pulse given its width and amplitude

        Args:
            width: width of pulse in number of samples
            amplitude: scale value of waveform with range of 0 to full_scale

        Returns:
            (Stream): the resulting waveform (uint broken)
        """
        self._width = width
        self._amplitude = amplitude

        # compute an input signal with peak value of full-scale. cast to output array dtype
        float_array = self.amplitude_series(width)
        np.multiply(float_array, self._amplitude, out=self._stream.samples, casting='unsafe')

        return self._stream


class RectanglePulse(Pulse):
    def amplitude_series(self, width):
        float_array = np.zeros(self._stream.sample_count)
        # width = (width /10

        pulse_start = int(self._stream.sample_count/2) - int(width/2)
        pulse_end = int(pulse_start + width)
        for i in range(pulse_start, pulse_end):
            float_array[i] = 1

        return float_array


class StepPulse(Pulse):
    def amplitude_series(self, width):
        float_array = np.zeros(self._stream.sample_count)

        pulse_start = int(self._stream.sample_count/2)
        pulse_end = self._stream.sample_count
        for i in range(pulse_start, pulse_end):
            float_array[i] = 1

        return float_array


class SincPulse(Pulse):
    @property
    def max_width(self):
        return 2 * self._stream.fc

    def amplitude_series(self, width):
        sample_count = self._stream.sample_count
        float_array = np.zeros(sample_count)

        if width < 0.001:
            width = 0.001

        bandwidth = width

        for i in range(sample_count):
            t = (i - int(sample_count/2)) * self.delta_t
            if t == 0:
                float_array[i] = 1
            else:
                x = 2 * bandwidth * np.pi * t

                float_array[i] = np.sin(x)/x

        return float_array



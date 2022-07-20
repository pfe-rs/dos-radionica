#!/usr/bin/env python

import numpy as np
from scipy.io import wavfile
from scipy.signal import find_peaks
from matplotlib import pyplot as plt


class DTMF:

    frequency_column = [1209, 1336, 1477, 1633]
    frequency_row = [697, 770, 852, 941]
    keys = [
        '1', '2', '3', 'A',
        '4', '5', '6', 'B',
        '7', '8', '9', 'C',
        '*', '0', '#', 'D'
    ]

    @staticmethod
    def freq(key: str) -> (int, int):
        index = DTMF.keys.index(key)
        row, column = (index // 4), (index % 4)
        return DTMF.frequency_row[row], DTMF.frequency_column[column]

    @staticmethod
    def key(f1: int, f2: int) -> str:
        # f1 - frequency row
        # f2 - frequency column
        if f1 > f2:
            f1, f2 = f2, f1
        row = DTMF.frequency_row.index(f1)
        column = DTMF.frequency_column.index(f2)
        return DTMF.keys[row * 4 + column] or None

    @staticmethod
    def encode(values: str, baud_rate: int = 1, sample_rate: int = 44100, pauses: bool = True) -> np.array:

        assert baud_rate > 0
        assert sample_rate >= 3266

        signal_out = np.arange(
            0,
            len(values) / baud_rate,
            1 / sample_rate, dtype=np.dtype('f4')
        )
        w = int(1.0 / baud_rate * sample_rate)

        for i in range(len(values)):
            f1, f2 = DTMF.freq(values[i])

            signal_f1 = np.sin(
                2 * np.pi * f1 *
                signal_out[i * w: (i+1) * w]
            )
            signal_f2 = np.sin(
                2 * np.pi * f2 *
                signal_out[i * w: (i+1) * w]
            )

            signal_out[i * w: (i+1) * w] = (signal_f1 + signal_f2) / 2

            if pauses:
                # pause length = 10% baud interval
                signal_out[i * w: i * w + int(w/10)] = 0

        return signal_out

    @staticmethod
    def decode(signal: np.array, baud_rate: int = 1, sample_rate: int = 44100) -> str:

        assert baud_rate > 0
        assert sample_rate >= 3266

        values = ''

        w = int(1.0 / baud_rate * sample_rate)
        length = int(signal.size / w)

        def get_peak_freq(signal: np.array, freq_list: list[int], freq_ratio: float) -> int:
            f_max = None
            a_max = 0
            for f in freq_list:
                a = np.max(signal[
                    int(f * freq_ratio - 1): int(f * freq_ratio + 2)
                ])
                if a > a_max:
                    f_max = f
                    a_max = a
            return f_max

        def get_peaks_freqs(signal: np.array):

            amp = np.abs(np.fft.fft(signal))
            freq = np.fft.fftfreq(signal.shape[-1], d=1/sample_rate)
            ratio = freq.size / sample_rate
            amp, _ = np.array_split(amp, 2)
            freq, _ = np.array_split(freq, 2)

            f1 = get_peak_freq(amp, DTMF.frequency_column, ratio)
            f2 = get_peak_freq(amp, DTMF.frequency_row, ratio)

            return f1, f2

        for i in range(length):
            f1, f2 = get_peaks_freqs(signal[i * w: (i+1) * w])
            k = DTMF.key(f1, f2)
            values += k

        return values

    @staticmethod
    def to_file(filename: str, values: str, baud_rate: int, sample_rate: int, pauses: bool):
        wavfile.write(
            filename, sample_rate,
            DTMF.encode(values, baud_rate, sample_rate, pauses)
        )

    @staticmethod
    def from_file(filename: str, baud_rate: int) -> str:
        sample_rate, signal = wavfile.read(filename)
        return DTMF.decode(
            signal, baud_rate, sample_rate
        )


if __name__ == '__main__':

    filename = 'sample.wav'
    values = '142357*86AB90#CD'
    baud_rate = 8
    sample_rate = 4000
    pauses = True

    DTMF.to_file(filename, values, baud_rate, sample_rate, pauses)
    print(DTMF.from_file(filename, baud_rate) == values)

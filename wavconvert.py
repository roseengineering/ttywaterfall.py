
import wave
import sys
import numpy as np
import argparse

BLOCK_SIZE = 2**18

def parse_args():
    formatter_class = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser(formatter_class=formatter_class)
    parser.add_argument('--input', required=True, help='input 16-bit wav file')
    parser.add_argument('--output', required=True, help='output 8-bit wav file')
    return parser.parse_args()

def convert(args):
    # find peak
    sample_peak = 0
    with wave.open(args.input, "rb") as wav_in:
        params = wav_in.getparams()
        num_channels = wav_in.getnchannels()
        sample_width = wav_in.getsampwidth()
        if sample_width != 2:
            raise ValueError('16-bit only supported')
        num_frames = BLOCK_SIZE // num_channels // sample_width
        while buf := wav_in.readframes(num_frames):
            samples = np.frombuffer(buf, dtype='h')
            sample_peak = np.maximum(sample_peak, np.max(np.abs(samples)).astype(int))
    print(f'Peak sample has a value of {sample_peak}')

    # read input
    with wave.open(args.output, "wb") as wav_out:
        wav_out.setparams(params)
        wav_out.setsampwidth(1)
        with wave.open(args.input, "rb") as wav_in:
            while buf := wav_in.readframes(num_frames):
                samples = np.frombuffer(buf, dtype='h')
                samples = samples.astype(np.float32)
                # rounding avoids mirror artifacts
                samples = np.round(samples / sample_peak * 127.5 + 128.0)
                samples = samples.astype('B')
                wav_out.writeframes(samples.tobytes())

if __name__ == '__main__':
    convert(parse_args())


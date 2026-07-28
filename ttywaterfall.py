#!/bin/env python

import signal
import socket
import sys
import os
import urllib.request
import argparse
import numpy as np

TOTAL_CROP = .2
BLOCK_SIZE = 2**13

COLORMAP = [
    [170, 0, 255],
    [166, 0, 254],
    [163, 0, 253],
    [160, 0, 252],
    [157, 0, 251],
    [154, 0, 250],
    [151, 0, 249],
    [148, 0, 248],
    [145, 0, 247],
    [142, 0, 246],
    [138, 0, 245],
    [135, 0, 245],
    [132, 0, 244],
    [129, 0, 243],
    [126, 0, 242],
    [123, 0, 241],
    [120, 0, 240],
    [117, 0, 239],
    [114, 0, 238],
    [110, 0, 237],
    [107, 0, 236],
    [104, 0, 235],
    [101, 0, 235],
    [98, 0, 234],
    [95, 3, 234],
    [93, 7, 235],
    [91, 11, 236],
    [88, 16, 237],
    [86, 20, 238],
    [83, 24, 239],
    [81, 28, 240],
    [78, 33, 241],
    [76, 37, 241],
    [73, 41, 242],
    [71, 45, 243],
    [68, 49, 244],
    [66, 54, 245],
    [64, 58, 246],
    [61, 62, 247],
    [59, 66, 248],
    [56, 71, 249],
    [54, 75, 250],
    [51, 79, 251],
    [49, 83, 251],
    [46, 88, 252],
    [44, 92, 253],
    [41, 96, 254],
    [39, 100, 253],
    [38, 104, 251],
    [36, 107, 250],
    [34, 111, 248],
    [32, 115, 246],
    [31, 118, 244],
    [29, 122, 242],
    [27, 126, 240],
    [25, 130, 238],
    [23, 133, 237],
    [22, 137, 235],
    [20, 141, 233],
    [18, 144, 231],
    [16, 148, 229],
    [15, 152, 227],
    [13, 156, 225],
    [11, 159, 224],
    [9, 163, 222],
    [8, 167, 220],
    [6, 170, 218],
    [4, 174, 216],
    [2, 178, 214],
    [0, 181, 213],
    [0, 184, 211],
    [0, 184, 209],
    [0, 184, 207],
    [0, 185, 204],
    [0, 185, 202],
    [0, 185, 200],
    [0, 185, 198],
    [0, 186, 196],
    [0, 186, 194],
    [0, 186, 192],
    [0, 187, 190],
    [0, 187, 188],
    [0, 187, 186],
    [0, 188, 184],
    [0, 188, 182],
    [0, 188, 180],
    [0, 188, 178],
    [0, 189, 176],
    [0, 189, 174],
    [0, 189, 172],
    [0, 190, 170],
    [0, 190, 168],
    [0, 190, 166],
    [0, 191, 164],
    [0, 191, 160],
    [0, 191, 156],
    [0, 192, 153],
    [0, 192, 149],
    [0, 193, 146],
    [0, 193, 142],
    [0, 193, 139],
    [0, 194, 135],
    [0, 194, 132],
    [0, 194, 128],
    [0, 195, 125],
    [0, 195, 121],
    [0, 196, 118],
    [0, 196, 114],
    [0, 196, 110],
    [0, 197, 107],
    [0, 197, 103],
    [0, 198, 100],
    [0, 198, 96],
    [0, 198, 93],
    [0, 199, 89],
    [0, 199, 86],
    [0, 200, 82],
    [4, 200, 80],
    [9, 201, 77],
    [13, 202, 75],
    [17, 203, 72],
    [21, 204, 69],
    [26, 205, 67],
    [30, 206, 64],
    [34, 207, 62],
    [39, 208, 59],
    [43, 209, 56],
    [47, 210, 54],
    [52, 210, 51],
    [56, 211, 49],
    [60, 212, 46],
    [65, 213, 43],
    [69, 214, 41],
    [73, 215, 38],
    [78, 216, 36],
    [82, 217, 33],
    [86, 218, 31],
    [90, 219, 28],
    [95, 220, 25],
    [99, 220, 23],
    [102, 221, 22],
    [106, 222, 21],
    [109, 222, 20],
    [112, 223, 19],
    [115, 223, 18],
    [118, 224, 17],
    [122, 224, 16],
    [125, 225, 15],
    [128, 225, 14],
    [131, 226, 13],
    [134, 227, 12],
    [138, 227, 11],
    [141, 228, 10],
    [144, 228, 9],
    [147, 229, 8],
    [150, 229, 7],
    [153, 230, 6],
    [157, 231, 5],
    [160, 231, 4],
    [163, 232, 3],
    [166, 232, 2],
    [169, 233, 1],
    [173, 233, 0],
    [176, 233, 0],
    [180, 232, 0],
    [183, 231, 0],
    [187, 230, 0],
    [190, 229, 0],
    [194, 229, 0],
    [197, 228, 0],
    [200, 227, 0],
    [204, 226, 0],
    [207, 225, 0],
    [211, 224, 0],
    [214, 223, 0],
    [218, 223, 0],
    [221, 222, 0],
    [225, 221, 0],
    [228, 220, 0],
    [232, 219, 0],
    [235, 218, 0],
    [239, 217, 0],
    [242, 216, 0],
    [246, 216, 0],
    [249, 215, 0],
    [253, 214, 0],
    [255, 212, 0],
    [255, 211, 0],
    [255, 209, 0],
    [255, 207, 0],
    [255, 205, 0],
    [255, 203, 0],
    [255, 201, 0],
    [255, 200, 0],
    [255, 198, 0],
    [255, 196, 0],
    [255, 194, 0],
    [255, 192, 0],
    [255, 190, 0],
    [255, 188, 0],
    [255, 187, 0],
    [255, 185, 0],
    [255, 183, 0],
    [255, 181, 0],
    [255, 179, 0],
    [255, 177, 0],
    [255, 175, 0],
    [255, 174, 0],
    [255, 172, 0],
    [255, 170, 0],
    [255, 167, 0],
    [255, 164, 0],
    [255, 162, 0],
    [255, 159, 0],
    [255, 156, 0],
    [255, 153, 0],
    [255, 151, 0],
    [255, 148, 0],
    [255, 145, 0],
    [255, 143, 0],
    [255, 140, 0],
    [255, 137, 0],
    [255, 135, 0],
    [255, 132, 0],
    [255, 129, 0],
    [255, 127, 0],
    [255, 124, 0],
    [255, 121, 0],
    [255, 119, 0],
    [255, 116, 0],
    [255, 113, 0],
    [255, 111, 0],
    [254, 108, 0],
    [252, 103, 0],
    [251, 98, 0],
    [249, 94, 0],
    [247, 89, 0],
    [245, 84, 0],
    [243, 79, 0],
    [241, 75, 0],
    [240, 70, 0],
    [238, 65, 0],
    [236, 61, 0],
    [234, 56, 0],
    [232, 51, 0],
    [231, 47, 0],
    [229, 42, 0],
    [227, 37, 0],
    [225, 32, 0],
    [223, 28, 0],
    [222, 23, 0],
    [220, 18, 0],
    [218, 14, 0],
    [216, 9, 0],
    [214, 4, 0],
    [213, 0, 0],
]

def parse_args():
    formatter_class = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser(formatter_class=formatter_class)
    parser.add_argument('--step', default=1024, type=int, help='step')
    parser.add_argument('--host', default='127.0.0.1', help='server host')
    parser.add_argument('--port', default=1234, type=int, help='server port')
    parser.add_argument('--url', help='url for cu8 stream')
    parser.add_argument('--filename', help='cu8 pcm file')
    return parser.parse_args()


def dbv(x):
    return 20 * np.log10(np.maximum(x, 1e-12))

    
class Waterfall:
    def __init__(self, width, step):
        crop = round((width / (1 - TOTAL_CROP) - width) / 2)
        size = width + 2 * crop
        self._crop = crop
        self._frame = np.zeros(2 * size, dtype=np.float32)
        self._power = np.zeros(size, dtype=np.float32)
        self._window = np.blackman(size).astype(np.float32)
        self._step = step
        self._count = 0
        self._index = 0

    def update(self, arr):
        i = 0
        while i < len(arr):
            n = min(len(self._frame) - self._index, len(arr) - i)
            self._frame[self._index:self._index+n] = arr[i:i+n]
            self._index += n
            i += n
            if self._index == len(self._frame):
                self.process()
                self._index = 0

    def waterfall_line(self, ps):
            ps -= np.min(ps)
            d = (len(COLORMAP) * ps / np.max(ps)).astype(int)
            d = np.minimum(d, len(COLORMAP) - 1)
            d = [ '\033[48;2;{};{};{}m \033[0m'.format(*COLORMAP[i]) for i in d ]
            return ''.join(d)

    def process(self):
        arr = self._frame[::2] + 1j * self._frame[1::2]
        self._power += np.abs(np.fft.fft(arr * self._window))
        self._count += 1
        if self._count == self._step:
            ps = np.fft.fftshift(self._power) / self._count
            ps = ps[self._crop:-self._crop]
            ps = dbv(ps)
            sys.stdout.write('\n' + self.waterfall_line(ps))
            self._power[:] = 0
            self._count = 0


class Client:
    def __init__(self, args):
        self._args = args

    def screen_size(self, *args):
        self._width = os.get_terminal_size(sys.stdout.fileno()).columns

    def loop_forever(self):
        args = self._args
        self.screen_size()
        signal.signal(signal.SIGWINCH, self.screen_size)
        if args.filename is not None:
            sock = open(args.filename, 'rb')
        elif args.url is not None:
            req = urllib.request.Request(args.url)
            sock = urllib.request.urlopen(req)
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
            sock.connect((args.host, args.port))
            sock = sock.makefile('rb')
        try:
            width = None
            while True:
                if width is None or width != self._width:
                    self._waterfall = Waterfall(self._width, args.step)
                    width = self._width
                buf = sock.read(BLOCK_SIZE)
                if buf == b'':
                    break
                arr = np.frombuffer(buf, dtype='B').astype(np.float32)
                self._waterfall.update(arr - 128)
        except socket.error as e:
            print(f'\nSocket error: {e}')
        except KeyboardInterrupt:
            pass
        finally:
            sock.close()
        print()


def main(args):
    client = Client(args)
    client.loop_forever()


if __name__ == '__main__':
    main(parse_args())


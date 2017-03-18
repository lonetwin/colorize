#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
colorize standard input by rows or (space separated) columns

Example usage:

output alternate rows in different colors
  $ ls -l | colorize.py -a

output each column from stdin in a different color
  $ tail -f logfile | colorize.py

output the first 3 columns in different colors and all subsequent text in one color
  $ tail -f logfile | colorize.py 3

filter the output of tail -f, coloring lines from each file in different color
  $ tail -f first.log second.log | colorize.py -t
"""

# The MIT License (MIT)
#
# Copyright (c) 2017 Steven Fernandez
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import unicode_literals
import argparse
import io
import re
import sys

from itertools import cycle
try:
    from future_builtins import zip
except ImportError:
    pass

__version__ = "0.2"


class Colors(object):
    """Namespace to hold colors function definitions
    """

    __slots__ = []

    def _create_color_func(code, bold=False):
        def color_func(text):
            code_str = '1;{}'.format(code) if bold else code
            return "\033[{}m{}\033[0m".format(code_str, text)
        return color_func

    # add any colors you might need.
    red = staticmethod(_create_color_func(31))
    green = staticmethod(_create_color_func(32))
    yellow = staticmethod(_create_color_func(33))
    blue = staticmethod(_create_color_func(34))
    purple = staticmethod(_create_color_func(35))
    cyan = staticmethod(_create_color_func(36))
    grey = staticmethod(_create_color_func(37))
    white = staticmethod(_create_color_func(40, True))


class HelpFormatterMixin(argparse.RawDescriptionHelpFormatter,
                         argparse.ArgumentDefaultsHelpFormatter):
    pass


def main(args):
    supported_colors = sorted(name for name in dir(Colors)
                              if callable(getattr(Colors, name)) and not name.startswith('_'))

    parser = argparse.ArgumentParser(description="Colorize standard input by rows or (space separated) columns."
                                                 " Default mode is to color columns.",
                                     epilog="These colors are supported: %s" % ', '.join(
                                         getattr(Colors, name)(name) for name in supported_colors),
                                     formatter_class=HelpFormatterMixin)

    group = parser.add_mutually_exclusive_group()

    group.add_argument('-c', '--column-colors', help="colors to use for column mode.", nargs="?",
                       type=lambda o: o.split(','), const=",".join(supported_colors),
                       default=",".join(supported_colors), metavar="color,color...")
    group.add_argument('-a', '--alternate', help="alternate mode.", nargs="?", type=lambda o: o.split(','),
                       default=False, const='white,grey', metavar="color,color...")
    group.add_argument('-t', '--tail', help="tail mode.", nargs="?", type=lambda o: o.split(','),
                       default=False, const=",".join(supported_colors), metavar="color,color...")
    parser.add_argument('max_colors', nargs='?', default=0, type=int)

    opts = parser.parse_args(args)

    # change stdin and stdout to line buffered mode
    stdin = io.open(sys.stdin.fileno(), 'r', 1)
    stdout = io.open(sys.stdout.fileno(), 'w', 1)

    if opts.alternate:
        colors = cycle(getattr(Colors, color) for color in (opts.alternate or supported_colors))
        stdout.writelines(color(line) for color, line in zip(colors, stdin))
    elif opts.tail:
        colors = cycle(getattr(Colors, color) for color in (opts.tail or supported_colors))
        path_to_color = {}   # dict to keep track of colors assigned to files
        color = next(colors)
        for line in stdin:
            if line.startswith("==> "):
                path = line.split()[1]
                # - get the color assigned to this path or set a new one
                # if one hasn't been assigned yet
                color = path_to_color.setdefault(path, next(colors))
            stdout.write(color(line))
    else:
        # default column coloring mode
        for line in stdin:
            # - start new color cycle for each line
            colors = cycle(getattr(Colors, color) for color in (opts.column_colors or supported_colors))
            # - split the line into max_split parts and zip(colors, parts)
            for color, word in zip(colors, filter(None, re.split(r'(\S+\s+)', line, opts.max_colors))):
                stdout.write(color(word))

if __name__ == '__main__':
    main(sys.argv[1:])

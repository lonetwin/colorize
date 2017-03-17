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
import sys
import re
import io

from itertools import cycle
try:
    from future_builtins import zip
except ImportError:
    pass

__version__ = "0.1"

def create_color_func(code, bold=False):
    def color_func(text):
        code_str = '1;{}'.format(code) if bold else code
        return "\033[{}m{}\033[0m".format(code_str, text)
    return color_func

# add any colors you might need.
red    = create_color_func(31)
green  = create_color_func(32)
yellow = create_color_func(33)
blue   = create_color_func(34)
purple = create_color_func(35)
cyan   = create_color_func(36)
grey   = create_color_func(37)
white  = create_color_func(40, True)


if __name__ == '__main__':
    alternate_mode = tail_mode = False

    if '-a' in sys.argv:
        alternate_mode = True
    elif '-t' in sys.argv:
        tail_mode = True

    # change stdin and stdout to line buffered mode
    stdin = io.open(sys.stdin.fileno(), 'r', 1)
    stdout = io.open(sys.stdout.fileno(), 'w', 1)

    if alternate_mode:
        colors = cycle((grey, white))
        stdout.writelines(color(line) for color, line in zip(colors, stdin))
    elif tail_mode:
        colors = cycle((red, green, yellow, blue, purple, cyan, grey, white))
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
        max_split = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 0
        for line in stdin:
            # - start new color cycle for each line
            colors = cycle((red, green, yellow, blue, purple, cyan, grey, white))
            # - split the line into max_split parts and zip(colors, parts)
            for color, word in zip(colors, filter(None, re.split('(\S+\s+)', line, max_split))):
                stdout.write(color(word))

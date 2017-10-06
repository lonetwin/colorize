#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

"""
colorize standard input by rows or (space separated) columns
"""

from __future__ import unicode_literals
import argparse
import functools
import io
import re
import sys

from itertools import cycle
try:
    from future_builtins import zip
except ImportError:
    pass

__version__ = "0.4"


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


def split_by_widths(input_string, widths, maxsplit=None):
    """Yields `maxsplit` sub-strings split at specified widths or space.

    Yields a list of strings obtained by splitting input string
    according to specified widths. If any element in the widths list is
    false-y, split the string up to and including the next spaces.

    If maxsplit is not None, input_string will be split into maxsplit
    parts (even if specified widths are greater than maxsplit)

    :param string input_string: Input string to split
    :param list widths: list of widths to use for splitting input_string
    :param int|None maxsplit: Max number of parts to split input_string in

    >>> list(split_by_widths('ABBCCC DDDD EEEEE', [1, 2, 3, None, 0]))
    ['A', 'BB', 'CCC', ' DDDD ', 'EEEEE']
    >>> list(split_by_widths('A BB CCC DDDD', [1, 2, 3, 4], maxsplit=2))
    ['A', ' BB CCC DDDD']
    >>> list(split_by_widths('', [2]))
    ['']
    >>> list(split_by_widths('A', [2]))
    ['A']
    >>> list(split_by_widths(' A', [2], 10))
    [' A']
    >>> list(split_by_widths(' A B ', [2], 10))
    [' A', ' B ']
    >>> list(split_by_widths(' A B CCC DDD EEE', [2, 1, 0, None], 5))
    [' A', ' ', 'B ', 'CCC ', 'DDD EEE']
    """
    start = 0
    widths = widths[:maxsplit-1] if maxsplit else widths
    for width in widths:
        if width:
            substr = input_string[start:start+width]
        else:
            matches = re.split('(\s*\S+\s+)', input_string[start:], maxsplit=1)
            substr = ''.join(matches[:2]) if len(matches) > 2 else ''.join(matches)
            width = len(substr)
        yield substr
        start += width

    # finally yield rest of the string, in case all widths were not specified
    if start < len(input_string):
        yield input_string[start:]


def main(args):
    color_func = functools.partial(getattr, Colors)

    supported_colors = sorted(name for name in dir(Colors)
                              if callable(color_func(name)) and not name.startswith('_'))

    parser = argparse.ArgumentParser(description="Colorize standard input by rows or (space separated) columns."
                                                 " Default mode is to color columns.",
                                     epilog="These colors are supported: %s" % ', '.join(
                                         color_func(name)(name) for name in supported_colors),
                                     formatter_class=HelpFormatterMixin)

    group = parser.add_mutually_exclusive_group()

    group.add_argument('-c', '--column-colors',  nargs="?", type=lambda o: o.split(','),
                       const=",".join(supported_colors), default=",".join(supported_colors),
                       metavar="color,color...",
                       help=("colors to use for column mode, in the order specified. "
                             "Column widths can be provided as a suffix separated by a `:`"
                             " (eg: red:10,blue,green:20...).")
                      )

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
        colors = cycle(color_func(name) for name in (opts.alternate or supported_colors))
        stdout.writelines(color(line) for color, line in zip(colors, stdin))
    elif opts.tail:
        colors = cycle(color_func(name) for name in (opts.tail or supported_colors))
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
        column_colors = opts.column_colors or supported_colors
        if any(':' in option for option in column_colors):
            # - split by width
            column_colors, widths = zip(*((color, int(width or 0)) for opt in column_colors for color, _, width in [opt.partition(':')]))
            split_func = functools.partial(split_by_widths, widths=widths, maxsplit=opts.max_colors)
        else:
            split_func = functools.partial(re.split, r'(\S+\s+)', maxsplit=opts.max_colors)

        # default column coloring mode
        for line in stdin:
            # - start new color cycle for each line
            default_colors = iter(supported_colors)
            colors = cycle(color_func(name or next(default_colors)) for name in column_colors)
            # - split the line into max_split parts and zip(colors, parts)
            for color, word in zip(colors, filter(None, split_func(line))):
                stdout.write(color(word))

if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        # avoid printing the traceback when tail mode is interrupted
        pass

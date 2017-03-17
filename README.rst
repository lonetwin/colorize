colorize
========

\*nixy filter that adds color to its standard input by rows or (space separated) columns


Example usage

* output alternate rows in different colors::

  $ ls -l | colorize.py -a

* output each column from stdin in a different color::

  $ tail -f logfile | colorize.py

* output the first 3 columns in different colors and all subsequent text in one color::

  $ tail -f logfile | colorize.py 3

* filter the output of tail -f, coloring lines from each file in different color::

  $ tail -f first.log second.log | colorize.py -t


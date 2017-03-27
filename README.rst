colorize
========

\*nixy filter that adds color to its standard input by rows or columns


Example usage

* output alternate rows in different colors::

  $ ls -l | colorize.py -a
  $ ls -l | colorize.py -a green,blue

* output each space separated column from stdin in a different color::

  $ tail -f logfile | colorize.py
  $ tail -f logfile | colorize.py -c green,blue,red,yellow

* output the first 3 space separated columns in different colors and all subsequent text in one color::

  $ tail -f logfile | colorize.py 3
  $ tail -f logfile | colorize.py -c green,blue,red 3

* output the columns specified by widths in different colors::

  # - The first 10 characters is green, the next 12 in red, followed by space
  # separated columns alternating in green and red
  $ tail -f logfile | colorize.py -c green:10,red:12

  # - The first 10 characters in green, the next 12 in red, all subsequent text in yellow
  $ tail -f logfile | colorize.py -c green:10,red:12,yellow 3

  # - The first 10 characters in the default first color (blue), the next 12 in green,
  # the next space separated column in red, the subsequent text in yellow
  $ tail -f logfile | colorize.py -c :10,green:12,red,yellow 4


* filter the output of tail -f, coloring lines from each file in different color::

  $ tail -f first.log second.log | colorize.py -t
  $ tail -f first.log second.log | colorize.py -t green,yellow


Demo
====
|demo|


.. |demo| image:: https://asciinema.org/a/107799.png
          :target: https://asciinema.org/a/107799?speed=2

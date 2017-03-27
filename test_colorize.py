#!/usr/bin/env python
# -*- coding: utf-8 -*-
import doctest
import unittest
from subprocess import Popen, PIPE

import colorize

Colors = colorize.Colors


class TestColorize(unittest.TestCase):

    def setUp(self):
        self.exe = "./colorize.py"
        self.input_lines = '\n'.join(["aaa bbb ccc ddd", "AAA BBB CCC DDD", "000 111 222 333"])
        self.proc = None

    def tearDown(self):
        self.proc.terminate()
        self.proc.wait()

    def check(self, cmdline, expected, input_lines=None):
        input_lines = input_lines if input_lines else self.input_lines
        self.proc = Popen(cmdline, stdin=PIPE, stdout=PIPE, universal_newlines=True)
        self.proc.stdin.write(input_lines)
        self.proc.stdin.close()
        self.assertEqual(self.proc.stdout.read(), expected)

    def test_default_action(self):
        expected = "".join([
            Colors.blue("aaa ") + Colors.cyan("bbb ") + Colors.green("ccc ") + Colors.grey("ddd\n"),
            Colors.blue("AAA ") + Colors.cyan("BBB ") + Colors.green("CCC ") + Colors.grey("DDD\n"),
            Colors.blue("000 ") + Colors.cyan("111 ") + Colors.green("222 ") + Colors.grey("333")
        ])
        self.check([self.exe], expected)

    def test_max_colors(self):
        expected = "".join([
            Colors.blue("aaa ") + Colors.cyan("bbb ccc ddd\n"),
            Colors.blue("AAA ") + Colors.cyan("BBB CCC DDD\n"),
            Colors.blue("000 ") + Colors.cyan("111 222 333")
        ])
        self.check([self.exe, "1"], expected)

    def test_custom_column_colors(self):
        expected = "".join([
            Colors.red("aaa ") + Colors.green("bbb ") + Colors.blue("ccc ") + Colors.red("ddd\n"),
            Colors.red("AAA ") + Colors.green("BBB ") + Colors.blue("CCC ") + Colors.red("DDD\n"),
            Colors.red("000 ") + Colors.green("111 ") + Colors.blue("222 ") + Colors.red("333")
        ])
        self.check([self.exe, "-c", "red,green,blue"], expected)

    def test_custom_column_colors_and_max_colors(self):
        expected = "".join([
            Colors.red("aaa ") + Colors.green("bbb ccc ddd\n"),
            Colors.red("AAA ") + Colors.green("BBB CCC DDD\n"),
            Colors.red("000 ") + Colors.green("111 222 333")
        ])
        self.check([self.exe, "-c", "red,green", "1"], expected)

    def test_only_widths(self):
        expected = "".join([
            Colors.blue("aaa bb") + Colors.cyan("b ") + Colors.blue("ccc ddd\n"),
            Colors.blue("AAA BB") + Colors.cyan("B ") + Colors.blue("CCC DDD\n"),
            Colors.blue("000 11") + Colors.cyan("1 ") + Colors.blue("222 333"),
        ])
        self.check([self.exe, "-c", ":6,"], expected)

    def test_width_and_max_colors(self):
        expected = "".join([
            Colors.blue("aaa bb") + Colors.cyan("b ccc ddd\n"),
            Colors.blue("AAA BB") + Colors.cyan("B CCC DDD\n"),
            Colors.blue("000 11") + Colors.cyan("1 222 333"),
        ])
        self.check([self.exe, "-c", ":6,", "2"], expected)

    def test_width_and_custom_colors(self):
        expected = "".join([
            Colors.blue("aaa bb") + Colors.red("b c") + Colors.yellow("cc ") + Colors.blue("ddd\n"),
            Colors.blue("AAA BB") + Colors.red("B C") + Colors.yellow("CC ") + Colors.blue("DDD\n"),
            Colors.blue("000 11") + Colors.red("1 2") + Colors.yellow("22 ") + Colors.blue("333"),
        ])
        self.check([self.exe, "-c", ":6,red:3,yellow"], expected)

    def test_width_custom_colors_and_max_colors(self):
        expected = "".join([
            Colors.blue("aaa bb") + Colors.red("b c") + Colors.yellow("cc ddd\n"),
            Colors.blue("AAA BB") + Colors.red("B C") + Colors.yellow("CC DDD\n"),
            Colors.blue("000 11") + Colors.red("1 2") + Colors.yellow("22 333"),
        ])
        self.check([self.exe, "-c", ":6,red:3,yellow", "3"], expected)

    def test_alternate_mode(self):
        expected = "".join([
            Colors.white("aaa bbb ccc ddd\n"),
            Colors.grey("AAA BBB CCC DDD\n"),
            Colors.white("000 111 222 333")
        ])
        self.check([self.exe, "-a"], expected)

    def test_alternate_mode_custom_colors(self):
        expected = "".join([
            Colors.red("aaa bbb ccc ddd\n"),
            Colors.green("AAA BBB CCC DDD\n"),
            Colors.red("000 111 222 333")
        ])
        self.check([self.exe, "-a", "red,green"], expected)

    def test_tailf_mode(self):
        self.maxDiff = None
        input_lines = "\n".join([
            "==> /path/to/first.log <==",
            "",
            "2015-01-01 00:00:01 [INFO] Something odd happened here",
            "2015-01-01 00:00:01 [INFO] Something odd happened here",
            "",
            "==> /path/to/second.log <==",
            "",
            "2015-01-01 00:00:01 [INFO] Something odd happened here",
            "2015-01-01 00:00:01 [INFO] Something odd happened here",
        ])
        expected = "".join([
            Colors.cyan("==> /path/to/first.log <==\n"),
            Colors.cyan("\n"),
            Colors.cyan("2015-01-01 00:00:01 [INFO] Something odd happened here\n"),
            Colors.cyan("2015-01-01 00:00:01 [INFO] Something odd happened here\n"),
            Colors.cyan("\n"),
            Colors.green("==> /path/to/second.log <==\n"),
            Colors.green("\n"),
            Colors.green("2015-01-01 00:00:01 [INFO] Something odd happened here\n"),
            Colors.green("2015-01-01 00:00:01 [INFO] Something odd happened here"),
        ])
        self.check([self.exe, "-t"], expected, input_lines)


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(colorize))
    return tests

if __name__ == '__main__':
    unittest.main()

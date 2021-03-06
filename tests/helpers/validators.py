import argparse
import datetime
import unittest

from ripe.atlas.tools.helpers.validators import ArgumentType


class TestArgumentTypeHelper(unittest.TestCase):

    def test_path(self):

        self.assertEqual("/tmp", ArgumentType.path("/tmp"))

        with self.assertRaises(argparse.ArgumentTypeError):
            ArgumentType.path("/not/a/real/place")

    def test_country_code(self):

        self.assertEqual("CA", ArgumentType.country_code("CA"))
        self.assertEqual("CA", ArgumentType.country_code("ca"))
        self.assertEqual("CA", ArgumentType.country_code("Ca"))
        self.assertEqual("CA", ArgumentType.country_code("cA"))

        for value in ("CAN", "Canada", "can", "This isn't even a country"):
            with self.assertRaises(argparse.ArgumentTypeError):
                ArgumentType.country_code(value)

    def test_comma_separated_integers(self):

        self.assertEqual(
            [1, 2, 3], ArgumentType.comma_separated_integers("1,2,3"))

        self.assertEqual(
            [1, 2, 3], ArgumentType.comma_separated_integers("1, 2, 3"))

        self.assertEqual([1], ArgumentType.comma_separated_integers("1"))

        with self.assertRaises(argparse.ArgumentTypeError):
            ArgumentType.comma_separated_integers("1,2,3,pizza!")

    def test_datetime(self):

        d = datetime.datetime(2015, 12, 1)

        self.assertEqual(d, ArgumentType.datetime("2015-12-1"))
        self.assertEqual(d, ArgumentType.datetime("2015-12-1T00"))
        self.assertEqual(d, ArgumentType.datetime("2015-12-1T00:00"))
        self.assertEqual(d, ArgumentType.datetime("2015-12-1T00:00:00"))
        self.assertEqual(d, ArgumentType.datetime("2015-12-1"))
        self.assertEqual(d, ArgumentType.datetime("2015-12-1 00"))
        self.assertEqual(d, ArgumentType.datetime("2015-12-1 00:00"))
        self.assertEqual(d, ArgumentType.datetime("2015-12-1 00:00:00"))

        with self.assertRaises(argparse.ArgumentTypeError):
            ArgumentType.datetime("yesterday")

        with self.assertRaises(argparse.ArgumentTypeError):
            ArgumentType.datetime("Definitely not a date, or even a time")

    def test_integer_range(self):

        self.assertEqual(1, ArgumentType.integer_range(1, 10)("1"))
        self.assertEqual(10, ArgumentType.integer_range(1, 10)("10"))
        self.assertEqual(1, ArgumentType.integer_range(-1, 1)("1"))
        self.assertEqual(-1, ArgumentType.integer_range(-1, 1)("-1"))

        for value in ("0", "11", "-1"):
            with self.assertRaises(argparse.ArgumentTypeError):
                ArgumentType.integer_range(1, 10)(value)

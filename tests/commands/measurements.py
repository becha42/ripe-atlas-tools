import collections
import datetime
import unittest

# Python 3 comes with mock in unittest
try:
    from unittest import mock
except ImportError:
    import mock

from ripe.atlas.tools.commands.measurements import Command

from ..base import capture_sys_output


class FakeGen(object):
    """
    A rip-off of the code used for testing probes, but a little prettier.
    """

    Measurement = collections.namedtuple("Measurement", (
        "id", "type", "status", "status_id", "meta_data", "destination_name",
        "description"
    ))

    def __init__(self):
        self.data = [
            self.Measurement(
                id=1, type="ping", status="Ongoing", status_id=2,
                meta_data={"status": {"name": "Ongoing", "id": 2}},
                destination_name="Name 1", description="Description 1",
            ),
            self.Measurement(
                id=2, type="ping", status="Ongoing", status_id=2,
                meta_data={"status": {"name": "Ongoing", "id": 2}},
                destination_name="Name 2", description="Description 2",
            ),
            self.Measurement(
                id=3, type="ping", status="Ongoing", status_id=2,
                meta_data={"status": {"name": "Ongoing", "id": 2}},
                destination_name="Name 3", description="Description 3",
            ),
            self.Measurement(
                id=4, type="ping", status="Ongoing", status_id=2,
                meta_data={"status": {"name": "Ongoing", "id": 2}},
                destination_name="Name 4", description="Description 4",
            ),
            self.Measurement(
                id=5, type="ping", status="Ongoing", status_id=2,
                meta_data={"status": {"name": "Ongoing", "id": 2}},
                destination_name="Name 5", description="Description 5",
            ),
        ]
        self.total_count = 5

    def __iter__(self):
        return self

    # Python 3 compatibility
    def __next__(self):
        return self.next()

    def next(self):
        if not self.data:
            raise StopIteration()
        else:
            return self.data.pop(0)


class TestMeasurementsCommand(unittest.TestCase):

    def setUp(self):
        self.cmd = Command()

    @mock.patch("ripe.atlas.tools.commands.measurements.MeasurementRequest")
    def test_with_empty_args(self, mock_request):

        mock_request.return_value = FakeGen()

        with capture_sys_output() as (stdout, stderr):
            self.cmd.init_args([])
            self.cmd.run()

        expected_content = (
            "\n"
            "Id      Type       Description                                           Status\n"
            "===============================================================================\n"
            "1       ping       Description 1                                        Ongoing\n"
            "2       ping       Description 2                                        Ongoing\n"
            "3       ping       Description 3                                        Ongoing\n"
            "4       ping       Description 4                                        Ongoing\n"
            "5       ping       Description 5                                        Ongoing\n"
            "===============================================================================\n"
            "                                              Showing 5 of 5 total measurements\n"
            "\n"
        )
        self.assertEqual(
            set(stdout.getvalue().split("\n")),
            set(expected_content.split("\n"))
        )
        self.assertEqual(
            self.cmd.arguments.field, ("id", "type", "description", "status"))

    @mock.patch("ripe.atlas.tools.commands.measurements.MeasurementRequest")
    def test_get_line_items(self, mock_request):

        self.cmd.init_args([])
        self.cmd.run()  # Forces the defaults
        self.assertEqual(
            self.cmd._get_line_items(FakeGen.Measurement(
                id=1, type="ping", status="Ongoing", status_id=2,
                meta_data={"status": {"name": "Ongoing", "id": 2}},
                destination_name="Name 1", description="Description 1",
            )),
            [1, "ping", "Description 1", "Ongoing"]
        )

        self.cmd.init_args([
            "--field", "id",
            "--field", "status"
        ])
        self.assertEqual(
            self.cmd._get_line_items(FakeGen.Measurement(
                id=1, type="ping", status="Ongoing", status_id=2,
                meta_data={"status": {"name": "Ongoing", "id": 2}},
                destination_name="Name 1", description="Description 1",
            )),
            [1, "Ongoing"]
        )

        self.cmd.init_args([
            "--field", "url",
        ])
        self.assertEqual(
            self.cmd._get_line_items(FakeGen.Measurement(
                id=1, type="ping", status="Ongoing", status_id=2,
                meta_data={"status": {"name": "Ongoing", "id": 2}},
                destination_name="Name 1", description="Description 1",
            )),
            ["https://atlas.ripe.net/measurements/1/"]
        )

    def test_get_filters(self):
        self.cmd.init_args([
            "--search", "the force is strong with this one",
            "--status", "ongoing",
            "--af", "6",
            "--type", "ping",
            "--started-before", "2015-01-01",
            "--started-after", "2014-01-01",
            "--stopped-before", "2015-01-01",
            "--stopped-after", "2014-01-01",
        ])
        self.assertEqual(self.cmd._get_filters(), {
            "search": "the force is strong with this one",
            "status__in": (2,),
            "af": 6,
            "type": "ping",
            "start_time__lt": datetime.datetime(2015, 1, 1),
            "start_time__gt": datetime.datetime(2014, 1, 1),
            "stop_time__lt": datetime.datetime(2015, 1, 1),
            "stop_time__gt": datetime.datetime(2014, 1, 1),
        })

    def test_get_colour_from_status(self):
        self.assertEqual(self.cmd._get_colour_from_status(0), "blue")
        self.assertEqual(self.cmd._get_colour_from_status(1), "blue")
        self.assertEqual(self.cmd._get_colour_from_status(2), "green")
        self.assertEqual(self.cmd._get_colour_from_status(4), "yellow")
        self.assertEqual(self.cmd._get_colour_from_status(5), "red")
        self.assertEqual(self.cmd._get_colour_from_status(6), "red")
        self.assertEqual(self.cmd._get_colour_from_status(7), "red")
        self.assertEqual(self.cmd._get_colour_from_status("XXX"), "white")

    def test_fail_arguments(self):
        expected_failures = (
            ("--status", "not a status"),
            ("--not-an-option",),
            ("--af", "5"),
            ("--type", "not a type"),
            ("--field", "not a field"),
        )
        for failure in expected_failures:
            with capture_sys_output() as (stdout, stderr):
                with self.assertRaises(SystemExit):
                    self.cmd.init_args(failure)

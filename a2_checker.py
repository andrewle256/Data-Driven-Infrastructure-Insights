"""A simple checker for functions in bridge_functions.py."""


from typing import Any
import unittest
import checker
import bridge_functions as bf


FILENAME = 'bridge_functions.py'
PYTA_CONFIG = 'pyta/a2_pyta.txt'
TARGET_LEN = 79
SEP = '='

CONSTANTS = {
    'ID_INDEX': 0,
    'NAME_INDEX': 1,
    'HIGHWAY_INDEX': 2,
    'LAT_INDEX': 3,
    'LON_INDEX': 4,
    'YEAR_INDEX': 5,
    'LAST_MAJOR_INDEX': 6,
    'LAST_MINOR_INDEX': 7,
    'NUM_SPANS_INDEX': 8,
    'SPAN_DETAILS_INDEX': 9,
    'LENGTH_INDEX': 10,
    'LAST_INSPECTED_INDEX': 11,
    'BCIS_INDEX': 12,
    'FROM_SEP': '=',
    'TO_SEP': ';',
    'HIGH_PRIORITY_BCI': 60,
    'MEDIUM_PRIORITY_BCI': 70,
    'LOW_PRIORITY_BCI': 100,
    'HIGH_PRIORITY_RADIUS': 500,
    'MEDIUM_PRIORITY_RADIUS': 250,
    'LOW_PRIORITY_RADIUS': 100,
    'EARTH_RADIUS': 6371
}


class CheckTest(unittest.TestCase):
    """Sanity checker for assignment functions."""

    def setUp(self):
        """Sample data for testing."""

        self.sample_bridges = [
            [1, 'Highway 24 Underpass at Highway 403', '403', 43.167233,
             -80.275567, '1965', '2014', '2009', 4,
             [12.0, 19.0, 21.0, 12.0], 65.0, '04/13/2012',
             [72.3, 69.5, 70.0, 70.3, 70.5, 70.7, 72.9]],
            [2, 'WEST STREET UNDERPASS', '403', 43.164531, -80.251582,
             '1963', '2014', '2007', 4, [
                 12.2, 18.0, 18.0, 12.2], 61.0,
             '04/13/2012', [71.5, 68.1, 69.0, 69.4, 69.4, 70.3,
                            73.3]],
            [3, 'STOKES RIVER BRIDGE', '6', 45.036739, -81.33579, '1958',
             '2013', '', 1, [16.0], 18.4, '08/28/2013',
             [85.1, 67.8, 67.4, 69.2, 70.0, 70.5, 75.1, 90.1]]
        ]

    def test_get_bridge(self) -> None:
        """Function get_bridge."""

        self._check_bridge(bf.get_bridge, [self.sample_bridges, 1])

    def test_get_average_bci(self) -> None:
        """Function get_average_bci."""

        self._check(bf.get_average_bci, [self.sample_bridges, 1], float)

    def test_get_total_length_on_hwy(self) -> None:
        """Function get_total_length_on_hwy."""

        self._check(bf.get_total_length_on_hwy,
                    [self.sample_bridges, '403'], float)

    def test_get_distance_between(self) -> None:
        """Function get_distance_between."""

        self._check(bf.get_distance_between,
                    [self.sample_bridges[0],
                     self.sample_bridges[1]], float)

    def test_get_closest_bridge(self) -> None:
        """Function get_closest_bridge."""

        self._check(bf.get_closest_bridge,
                    [self.sample_bridges, 1], int)

    def test_get_bridges_in_radius(self) -> None:
        """Function get_bridges_in_radius."""

        self._check_list(bf.get_bridges_in_radius,
                         [self.sample_bridges, 43.10, -80.15, 50])

    def test_get_bridges_with_bci_below(self) -> None:
        """Function get_bridges_with_bci_below."""

        self._check_list(bf.get_bridges_with_bci_below,
                         [self.sample_bridges, [1, 2], 72])

    def test_get_bridges_containing(self) -> None:
        """Function get_bridges_containing."""

        self._check_list(bf.get_bridges_containing,
                         [self.sample_bridges, '403'])

    def test_assign_inspectors(self) -> None:
        """Function assign_inspectors."""

        def list_list_int(obj):
            msg = "assign_inspectors should return a list[list[int]]"

            def list_int(obj):
                return (isinstance(obj, list)
                        and all(map(lambda o: isinstance(o, int), obj)))

            if not (isinstance(obj, list) and all(map(list_int, obj))):
                return (False, msg)
            return (True, '')

        print('\nChecking assign_inspectors...')
        result = checker.type_check_full(
            bf.assign_inspectors, [self.sample_bridges, [[43.10, -80.15]], 2],
            list_list_int)
        self.assertTrue(result[0], result[1])
        print('  check complete')

    def test_inspect_bridges(self) -> None:
        """Function inspect_bridges."""

        self._check(bf.inspect_bridges,
                    [self.sample_bridges, [1], '09/15/2018', 71.9], type(None))

    def test_add_rehab(self) -> None:
        """Function add_rehab."""

        self._check(bf.add_rehab,
                    [self.sample_bridges, 1, '2023', False], type(None))

    def test_format_data(self) -> None:
        """Function format_data."""

        sample = [
            ['1 -  32/', 'Highway 24 Underpass at Highway 403', '403',
             '43.167233', '-80.275567', '1965', '2014', '2009', '4',
             'Total=64  (1)=12;(2)=19;(3)=21;(4)=12;', '65', '04/13/2012',
             '72.3', '', '72.3', '', '69.5', '', '70', '', '70.3', '', '70.5',
             '', '70.7', '72.9', ''],
            ['1 -  43/', 'WEST STREET UNDERPASS', '403', '43.164531',
             '-80.251582', '1963', '2014', '2007', '4',
             'Total=60.4  (1)=12.2;(2)=18;(3)=18;(4)=12.2;', '61',
             '04/13/2012', '71.5', '', '71.5', '', '68.1', '', '69', '',
             '69.4', '', '69.4', '', '70.3', '73.3', ''],
            ['2 -   4/', 'STOKES RIVER BRIDGE', '6', '45.036739', '-81.33579',
             '1958', '2013', '', '1', 'Total=16  (1)=16;', '18.4',
             '08/28/2013', '85.1', '85.1', '', '67.8', '', '67.4', '', '69.2',
             '70', '70.5', '', '75.1', '', '90.1', '']]

        self._check(bf.format_data, [sample], type(None))

    def test_check_constants(self) -> None:
        """Values of constants."""

        print('\nChecking that constants refer to their original values...')
        self._check_constants(CONSTANTS, bf)
        print('  check complete.')

    def _check(self, func: callable, args: list, ret_type: type) -> None:
        """Check that func called with arguments args returns a value of type
        ret_type. Display the progress and the result of the check.

        """

        print(f'\nChecking {func.__name__}...')
        result = checker.type_check_simple(func, args, ret_type)
        self.assertTrue(result[0], result[1])
        print('  check complete')

    def _check_list(self, func: callable, args: list) -> None:
        """Check that func called with arguments args returns a list[int].
        Display the progress and the result of the check.

        """

        print(f'\nChecking {func.__name__}...')
        result = checker.returns_list_of(func, args, int)
        self.assertTrue(result[0], result[1])
        print('  check complete')

    def _check_bridge(self, func: callable, args: list) -> None:
        """Check that func called with arguments args returns a valid bridge
        record. Display the progress and the result of the check.

        """

        print(f'\nChecking {func.__name__}...')
        result = checker.type_check_full(func, args, _is_bridge)
        self.assertTrue(result[0], result[1])
        print('  check complete')

    def _check_constants(self, constants: dict[str, object], mod: Any) -> None:
        """Check that, for each (name, value) pair in constants, the value of
        a variable named name in module mod is value.
        """

        for name, expected in constants.items():
            actual = getattr(mod, name)
            msg = (f'The value of constant {name} should be '
                   '{expected} but is {actual}.')
            self.assertEqual(expected, actual, msg)


def _is_bridge(obj: Any) -> bool:
    """Return True iff obj is a valid bridge record."""

    msg = 'The return value should be a list'
    if not isinstance(obj, list):
        return (False, msg)
    if len(obj) != 13:
        return (False, msg + ' of length 13')

    correct_types = (int, str, str, float, float, str, str, str, int,
                     list, float, str, list)
    for (i, correct_type) in enumerate(correct_types):
        if not isinstance(obj[i], correct_type):
            msg += (f' and the value at index {i}'
                    f' should be a {correct_type.__name__}')
            return (False, msg)
    return (True, '')


checker.ensure_no_io('bridge_functions')
print(''.center(TARGET_LEN, SEP))
print(' Start: checking coding style '.center(TARGET_LEN, SEP))
checker.run_pyta(FILENAME, PYTA_CONFIG)
print(' End checking coding style '.center(TARGET_LEN, SEP))

print(' Start: checking type contracts '.center(TARGET_LEN, SEP))
unittest.main(exit=False)
print(' End checking type contracts '.center(TARGET_LEN, SEP))

print('\nScroll up to see ALL RESULTS:')
print('  - checking coding style')
print('  - checking type contract\n')

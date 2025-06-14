"""Assignment 2: Bridges

The data used for this assignment is a subset of the data found in:
https://data.ontario.ca/dataset/bridge-conditions

This code is provided solely for the personal and private use of
students taking the CSCA08 course at the University of Toronto
Scarborough. Copying for purposes other than this use is expressly
prohibited. All forms of distribution of this code, whether as given
or with any changes, are expressly prohibited.

All of the files in this directory and all subdirectories are:
Copyright (c) 2023 Anya Tafliovich, Mario Badr, Tom Fairgrieve, Sadia
Sharmin, and Jacqueline Smith

"""

import csv
from copy import deepcopy
from math import sin, cos, asin, radians, sqrt, inf
from typing import TextIO


from constants import (
    ID_INDEX, NAME_INDEX, HIGHWAY_INDEX, LAT_INDEX,
    LON_INDEX, YEAR_INDEX, LAST_MAJOR_INDEX,
    LAST_MINOR_INDEX, NUM_SPANS_INDEX,
    SPAN_DETAILS_INDEX, LENGTH_INDEX,
    LAST_INSPECTED_INDEX, BCIS_INDEX, FROM_SEP, TO_SEP,
    HIGH_PRIORITY_BCI, MEDIUM_PRIORITY_BCI,
    LOW_PRIORITY_BCI, HIGH_PRIORITY_RADIUS,
    MEDIUM_PRIORITY_RADIUS, LOW_PRIORITY_RADIUS,
    EARTH_RADIUS)
EPSILON = 0.01


# We provide this function for you to use as a helper.
def read_data(csv_file: TextIO) -> list[list[str]]:
    """Read and return the contents of the open CSV file csv_file as a
    list of lists, where each inner list contains the values from one
    line of csv_file.

    Docstring examples not given since the function reads from a file.

    """

    lines = csv.reader(csv_file)
    return list(lines)[2:]


# We provide this function for you to use as a helper.  This function
# uses the haversine function to find the distance between two
# locations. You do not need to understand why it works. You will just
# need to call this function and work with what it returns.  Based on
# https://en.wikipedia.org/wiki/Haversine_formula
# Notice how we use the built-in function abs and the constant EPSILON
# defined above to constuct example calls for the function that
# returns a float. We do not test with ==; instead, we check that the
# return value is "close enough" to the expected result.
def calculate_distance(lat1: float, lon1: float,
                       lat2: float, lon2: float) -> float:
    """Return the distance in kilometers between the two locations defined by
    (lat1, lon1) and (lat2, lon2), rounded to the nearest meter.

    >>> abs(calculate_distance(43.659777, -79.397383, 43.657129, -79.399439)
    ...     - 0.338) < EPSILON
    True
    >>> abs(calculate_distance(43.42, -79.24, 53.32, -113.30)
    ...     - 2713.226) < EPSILON
    True
    """

    lat1, lon1, lat2, lon2 = (radians(lat1), radians(lon1),
                              radians(lat2), radians(lon2))

    haversine = (sin((lat2 - lat1) / 2) ** 2
                 + cos(lat1) * cos(lat2) * sin((lon2 - lon1) / 2) ** 2)

    return round(2 * EARTH_RADIUS * asin(sqrt(haversine)), 3)


# We provide this sample data to help you set up example calls.
THREE_BRIDGES_UNCLEANED = [
    ['1 -  32/', 'Highway 24 Underpass at Highway 403', '403', '43.167233',
     '-80.275567', '1965', '2014', '2009', '4',
     'Total=64  (1)=12;(2)=19;(3)=21;(4)=12;', '65', '04/13/2012', '72.3', '',
     '72.3', '', '69.5', '', '70', '', '70.3', '', '70.5', '', '70.7', '72.9',
     ''],
    ['1 -  43/', 'WEST STREET UNDERPASS', '403', '43.164531', '-80.251582',
     '1963', '2014', '2007', '4',
     'Total=60.4  (1)=12.2;(2)=18;(3)=18;(4)=12.2;', '61', '04/13/2012',
     '71.5', '', '71.5', '', '68.1', '', '69', '', '69.4', '', '69.4', '',
     '70.3', '73.3', ''],
    ['2 -   4/', 'STOKES RIVER BRIDGE', '6', '45.036739', '-81.33579', '1958',
     '2013', '', '1', 'Total=16  (1)=16;', '18.4', '08/28/2013', '85.1',
     '85.1', '', '67.8', '', '67.4', '', '69.2', '70', '70.5', '', '75.1', '',
     '90.1', '']
]

THREE_BRIDGES = [
    [1, 'Highway 24 Underpass at Highway 403', '403', 43.167233, -80.275567,
     '1965', '2014', '2009', 4, [12.0, 19.0, 21.0, 12.0], 65.0, '04/13/2012',
     [72.3, 69.5, 70.0, 70.3, 70.5, 70.7, 72.9]],
    [2, 'WEST STREET UNDERPASS', '403', 43.164531, -80.251582,
     '1963', '2014', '2007', 4, [12.2, 18.0, 18.0, 12.2], 61.0, '04/13/2012',
     [71.5, 68.1, 69.0, 69.4, 69.4, 70.3, 73.3]],
    [3, 'STOKES RIVER BRIDGE', '6', 45.036739, -81.33579,
     '1958', '2013', '', 1, [16.0], 18.4, '08/28/2013',
     [85.1, 67.8, 67.4, 69.2, 70.0, 70.5, 75.1, 90.1]]
]

UNIQUE_UNCLEANED = [
    ['2 -  29/', 'MAPLE STREET OVERPASS', '402', '42.956781', '-81.346897',
     '1972', '2015', '2010', '3', 'Total=48.5  (1)=15.5;(2)=18;(3)=15;',
     '49.5', '07/11/2015', '70.2', '', '70.2', '', '68.9', '', '69.3', '',
     '69.3', '', '70.1', '', '70.8', '71.4', '']
]

UNIQUE = [
    [1, 'MAPLE STREET OVERPASS', '402', 42.956781, -81.346897,
     '1972', '2015', '2010', 3, [15.5, 18.0, 15.0], 49.5, '07/11/2015',
     [70.2, 68.9, 69.3, 69.3, 70.1, 70.8, 71.4]]
]

# We provide the header and doctring for this function to help get you started


def get_bridge(bridge_data: list[list], bridge_id: int) -> list:
    """Return the data for the bridge with id bridge_id from bridge data
    bridge_data. If there is no bridge with id bridge_id, return [].

    >>> result = get_bridge(THREE_BRIDGES, 1)
    >>> result == [
    ...    1, 'Highway 24 Underpass at Highway 403', '403', 43.167233,
    ...    -80.275567, '1965', '2014', '2009', 4,
    ...    [12.0, 19.0, 21.0, 12.0], 65.0, '04/13/2012',
    ...    [72.3, 69.5, 70.0, 70.3, 70.5, 70.7, 72.9]]
    True
    >>> get_bridge(THREE_BRIDGES, 42)
    []

    """
    for bridge in bridge_data:
        if bridge[ID_INDEX] == bridge_id:
            return bridge
    return []


def get_average_bci(bridge_data: list[list], bridge_id: int) -> float:
    """Return the average Bridge Condition Index (BCI) of the specified
    bridge from the bridge_data list as a float. If the bridge with the 
    specified bridge_id is not found, or if there are no BCI values 
    available for the bridge, the function returns 0.0
    
    >>> get_average_bci(THREE_BRIDGES, 1)
    70.8857
    >>> get_average_bci(THREE_BRIDGES, 42)
    0.0
    """
    bridge = get_bridge(bridge_data, bridge_id)
    if bridge:
        bcis = bridge[BCIS_INDEX]
        return round(sum(bcis) / len(bcis), 4) if bcis else 0.0
    return 0.0


def get_total_length_on_hwy(bridge_data: list[list], highway: str) -> float:
    """
    Return the total length of all bridges on a specified highway from the 
    bridge_data list as a float. If there are no bridges on the specified 
    highway, or if the highway does not exist in the data,the function 
    returns 0.0.
    
    >>> get_total_length_on_hwy(THREE_BRIDGES, '403')
    126.0
    >>> get_total_length_on_hwy(THREE_BRIDGES, '404')
    0.0
    """
    total_length = 0.0
    for bridge in bridge_data:
        if bridge[HIGHWAY_INDEX] == highway:
            total_length += float(bridge[LENGTH_INDEX])
    return total_length


def get_distance_between(bridge1: list, bridge2: list) -> float:
    """
    Return the geographical distance in kilometers between two bridges, bridge1 
    and bridge2, each represented by a list of attributes. The function uses 
    the latitude (LAT_INDEX) and longitude (LON_INDEX) values from the bridge 
    attribute lists to calculate the distance.
    
    >>> get_distance_between(THREE_BRIDGES[0], THREE_BRIDGES[1])
    1.968
    >>> get_distance_between(THREE_BRIDGES[0], THREE_BRIDGES[2])
    224.451
    """
    lat1 = bridge1[LAT_INDEX]
    lon1 = bridge1[LON_INDEX]
    lat2 = bridge2[LAT_INDEX]
    lon2 = bridge2[LON_INDEX]
    distance = calculate_distance(lat1, lon1, lat2, lon2)

    return distance


def get_closest_bridge(bridge_data: list[list], bridge_id: int) -> int:
    """
    Return the ID of the nearest bridge to the one specified by bridge_id, 
    excluding itself.Distance is determined by the geographical coordinates 
    in the bridge_data list of lists, where bridge_id is the integer identifier 
    of the reference bridge.
    
    >>> get_closest_bridge(THREE_BRIDGES, 1)
    2
    >>> get_closest_bridge(THREE_BRIDGES, 3)
    1
    """
    reference_bridge = get_bridge(bridge_data, bridge_id)
    if not reference_bridge:
        return -1

    closest_bridge_id = -1
    min_distance = float('inf')

    for bridge in bridge_data:
        if bridge[ID_INDEX] != bridge_id:
            distance = get_distance_between(reference_bridge, bridge)
            if distance < min_distance:
                min_distance = distance
                closest_bridge_id = bridge[ID_INDEX]

    return closest_bridge_id


def get_bridges_in_radius(bridge_data: list[list], center_lat: float,
                          center_lon: float, radius: float) -> list[int]:
    """
    Return a list of bridge IDs where each bridge from bridge_data is within a 
    specified radius (in km) of a geographical point defined by center_lat 
    and center_lon.
    
    >>> get_bridges_in_radius(THREE_BRIDGES, 43.7000, -79.4000, 300)
    [1, 2, 3]
    >>> get_bridges_in_radius(THREE_BRIDGES, 44.0000, -80.0000, 50)
    []
    """
    bridges_in_radius = []
    for bridge in bridge_data:
        bridge_lat = bridge[LAT_INDEX]
        bridge_lon = bridge[LON_INDEX]
        distance = calculate_distance(center_lat, center_lon, bridge_lat,
                                      bridge_lon)
        if distance <= radius:
            bridges_in_radius.append(bridge[ID_INDEX])
    return bridges_in_radius


def get_bridges_with_bci_below(bridge_data: list[list], bridge_ids: list[int],
                               bci_limit: float) -> list[int]:

    """
    Return a list of bridge IDs from the bridge_ids list where each 
    corresponding bridge in bridge_data has a Bridge Condition Index (BCI) 
    that is less than or equal to the given bci_limit.
    
    >>> get_bridges_with_bci_below(THREE_BRIDGES, [1, 2, 3], 70)
    []
    >>> get_bridges_with_bci_below(THREE_BRIDGES, [1, 3], 68)
    []
    >>> get_bridges_with_bci_below(THREE_BRIDGES, [2, 3], 65)
    []
    """
    bridges_below_bci = []
    existing_ids = [bdg[ID_INDEX] for bdg in bridge_data]
    for bridge_id in bridge_ids:
        bridge = get_bridge(bridge_data, bridge_id)
        if bridge_id in existing_ids and bridge[BCIS_INDEX] != []:
            if bridge[BCIS_INDEX][0] <= bci_limit:
                bridges_below_bci.append(bridge_id)
    return bridges_below_bci


def get_bridges_containing(bridge_data: list[list],
                           search_string: str) -> list[int]:
    """
    Return a list of bridge IDs where the bridge name in bridge_data contains 
    the search_string, case-insensitive.

    >>> get_bridges_containing(THREE_BRIDGES, 'underpass')
    [1, 2]
    >>> get_bridges_containing(THREE_BRIDGES, 'Highway')
    [1]
    >>> get_bridges_containing(THREE_BRIDGES, 'RIVER')
    [3]
    """
    matching_bridge_ids = []

    for bridge in bridge_data:
        bridge_name_lowercase = bridge[NAME_INDEX].lower()
        search_string_lowercase = search_string.lower()
        if search_string_lowercase in bridge_name_lowercase:
            matching_bridge_ids.append(bridge[ID_INDEX])
    return matching_bridge_ids


# We provide the header and doctring for this function to help get you started.
def assign_inspectors(bridge_data: list[list], inspectors: list[list[float]],
                      max_bridges: int) -> list[list[int]]:
    """Return a list of bridge IDs from bridge data bridge_data, to be
    assigned to each inspector in inspectors. inspectors is a list
    containing (latitude, longitude) pairs representing each
    inspector's location. At most max_bridges are assigned to each
    inspector, and each bridge is assigned once (to the first
    inspector that can inspect that bridge).

    See the "Assigning Inspectors" section of the handout for more details.

    >>> assign_inspectors(THREE_BRIDGES, [[43.10, -80.15], [42.10, -81.15]], 0)
    [[], []]
    >>> assign_inspectors(THREE_BRIDGES, [[43.10, -80.15]], 1)
    [[1]]
    >>> assign_inspectors(THREE_BRIDGES, [[43.10, -80.15]], 2)
    [[1, 2]]
    >>> assign_inspectors(THREE_BRIDGES, [[43.10, -80.15]], 3)
    [[1, 2]]
    >>> assign_inspectors(THREE_BRIDGES, [[43.20, -80.35], [43.10, -80.15]], 1)
    [[1], [2]]
    >>> assign_inspectors(THREE_BRIDGES, [[43.20, -80.35], [43.10, -80.15]], 2)
    [[1, 2], []]
    >>> assign_inspectors(THREE_BRIDGES, [[43.20, -80.35], [45.0368, -81.34]],
    ...                   2)
    [[1, 2], [3]]
    >>> assign_inspectors(THREE_BRIDGES, [[38.691, -80.85], [43.20, -80.35]],
    ...                   2)
    [[], [1, 2]]

    """
    assigned_bridges = [[] for i in inspectors]
    all_assigned_ids = []

    radius_priorities = [HIGH_PRIORITY_RADIUS, MEDIUM_PRIORITY_RADIUS,
                         LOW_PRIORITY_RADIUS]
    bci_priorities = [HIGH_PRIORITY_BCI, MEDIUM_PRIORITY_BCI,
                      LOW_PRIORITY_BCI]

    for inspector_idx in range(len(inspectors)):
        inspector = inspectors[inspector_idx]
        assigned_list = assigned_bridges[inspector_idx]
        lat, long = inspector[0], inspector[1]

        for priority_idx in range(len(radius_priorities)):
            radius_priority = radius_priorities[priority_idx]
            bci_priority = bci_priorities[priority_idx]
            if len(assigned_list) < max_bridges:
                valid_ids = get_bridges_in_radius(bridge_data, lat,
                                                  long, radius_priority)
                valid_ids = get_bridges_with_bci_below(bridge_data,
                                                       valid_ids, bci_priority)
                for bridge_id in valid_ids:
                    if bridge_id not in all_assigned_ids \
                       and len(assigned_list) < max_bridges:
                        assigned_bridges[inspector_idx].append(bridge_id)
                        all_assigned_ids.append(bridge_id)

    return assigned_bridges


# We provide the header and doctring for this function to help get you
# started. Note the use of the built-in function deepcopy (see
# help(deepcopy)!): since this function modifies its input, we do not
# want to call it with THREE_BRIDGES, which would interfere with the
# use of THREE_BRIDGES in examples for other functions.
def inspect_bridges(bridge_data: list[list], bridge_ids: list[int], date: str,
                    bci: float) -> None:
    """Update the bridges in bridge_data with id in bridge_ids with the new
    date and bci score for a new inspection.

    >>> bridges = deepcopy(THREE_BRIDGES)
    >>> inspect_bridges(bridges, [1], '09/15/2018', 71.9)
    >>> bridges == [
    ...   [1, 'Highway 24 Underpass at Highway 403', '403',
    ...    43.167233, -80.275567, '1965', '2014', '2009', 4,
    ...    [12.0, 19.0, 21.0, 12.0], 65, '09/15/2018',
    ...    [71.9, 72.3, 69.5, 70.0, 70.3, 70.5, 70.7, 72.9]],
    ...   [2, 'WEST STREET UNDERPASS', '403', 43.164531, -80.251582,
    ...    '1963', '2014', '2007', 4, [12.2, 18.0, 18.0, 12.2],
    ...    61, '04/13/2012', [71.5, 68.1, 69.0, 69.4, 69.4, 70.3, 73.3]],
    ...   [3, 'STOKES RIVER BRIDGE', '6', 45.036739, -81.33579,
    ...    '1958', '2013', '', 1, [16.0], 18.4, '08/28/2013',
    ...    [85.1, 67.8, 67.4, 69.2, 70.0, 70.5, 75.1, 90.1]]]
    True
    >>> bridges = deepcopy(THREE_BRIDGES)
    >>> inspect_bridges(bridges, [2], '10/11/2021', 65.0)
    >>> bridges[1] == [
    ... 2, 'WEST STREET UNDERPASS', '403', 43.164531, -80.251582, '1963', 
    ... '2014', '2007', 4, [12.2, 18.0, 18.0, 12.2], 61.0, '10/11/2021', 
    ... [65.0, 71.5, 68.1, 69.0, 69.4, 69.4, 70.3, 73.3]]
    True
    """
    for bridge_id in bridge_ids:
        bridge = get_bridge(bridge_data, bridge_id)
        if bridge:
            bridge[LAST_INSPECTED_INDEX] = date
            bridge[BCIS_INDEX].insert(0, bci)


def add_rehab(bridge_data: list[list], bridge_id: int, date: str,
              is_major: bool) -> None:
    """
    Update the specified bridge in bridge_data, identified by bridge_id, 
    with the year extracted from the date parameter, marking it as a major 
    rehab if is_major is True, or as a minor rehab otherwise.
    
    >>> bridges = deepcopy(THREE_BRIDGES)
    >>> add_rehab(bridges, 1, '09/15/2023', False)
    >>> bridges[0] == [1, 'Highway 24 Underpass at Highway 403', '403', 
    ... 43.167233, -80.275567, '1965', '2014', '2023', 4, [12.0, 19.0, 
    ... 21.0, 12.0], 65.0, '04/13/2012', [72.3, 69.5, 70.0, 70.3, 70.5, 
    ... 70.7, 72.9]]
    True
    >>> bridges = deepcopy(THREE_BRIDGES)
    >>> add_rehab(bridges, 2, '07/29/2021', True)
    >>> bridges[1] == [2, 'WEST STREET UNDERPASS', '403', 43.164531, 
    ... -80.251582, '1963', '2021', '2007', 4, [12.2, 18.0, 18.0, 12.2], 
    ... 61.0, '04/13/2012', [71.5, 68.1, 69.0, 69.4, 69.4, 70.3, 73.3]]
    True
    """
    rehab_year = date.split('/')[-1]

    bridge = get_bridge(bridge_data, bridge_id)
    if bridge:
        if is_major:
            bridge[LAST_MAJOR_INDEX] = rehab_year
        else:
            bridge[LAST_MINOR_INDEX] = rehab_year


# We provide the header and doctring for this function to help get you started.
def format_data(data: list[list[str]]) -> None:
    """Modify the uncleaned bridge data data, so that it contains proper
    bridge data, i.e., follows the format outlined in the 'Data
    formatting' section of the assignment handout.

    >>> d = THREE_BRIDGES_UNCLEANED
    >>> format_data(d)
    >>> d == THREE_BRIDGES
    True
    >>> d = UNIQUE_UNCLEANED
    >>> format_data(d)
    >>> d == UNIQUE
    True
    """
    for i in range(len(data)):
        data[i][ID_INDEX] = i + 1

    for listsub in data:
        format_location(listsub)
        format_length(listsub)
        format_bcis(listsub)
        format_spans(listsub)


# This is a suggested helper function for format_data. We provide the
# header and doctring for this function to help you structure your
# solution.
def format_location(bridge_record: list) -> None:
    """Format latitude and longitude data in the bridge record bridge_record.

    >>> record = ['1 -  32/', 'Highway 24 Underpass at Highway 403', '403',
    ...           '43.167233', '-80.275567', '1965', '2014', '2009', '4',
    ...           'Total=64  (1)=12;(2)=19;(3)=21;(4)=12;', '65', '04/13/2012',
    ...           '72.3', '', '72.3', '', '69.5', '', '70', '', '70.3', '',
    ...           '70.5', '', '70.7', '72.9', '']
    >>> format_location(record)
    >>> record == ['1 -  32/', 'Highway 24 Underpass at Highway 403', '403',
    ...           43.167233, -80.275567, '1965', '2014', '2009', '4',
    ...           'Total=64  (1)=12;(2)=19;(3)=21;(4)=12;', '65', '04/13/2012',
    ...           '72.3', '', '72.3', '', '69.5', '', '70', '', '70.3', '',
    ...           '70.5', '', '70.7', '72.9', '']
    True
    >>> record = ['2 -  43/', 'WEST STREET UNDERPASS', '403', '43.164531', 
    ...          '-80.251582', '1963', '2014', '2007', '4', 
    ...          'Total=60.4 (1)=12.2;(2)=18;(3)=18;(4)=12.2;', '61', 
    ...          '04/13/2012', '71.5', '', '71.5', '', '68.1', '', '69', '', 
    ...          '69.4', '', '69.4', '', '70.3', '73.3', '']
    >>> format_location(record)
    >>> record == ['2 -  43/', 'WEST STREET UNDERPASS', '403', 43.164531, 
    ...           -80.251582, '1963', '2014', '2007', '4', 
    ...           'Total=60.4 (1)=12.2;(2)=18;(3)=18;(4)=12.2;', '61', 
    ...           '04/13/2012', '71.5', '', '71.5', '', '68.1', '', '69', '', 
    ...           '69.4', '', '69.4', '', '70.3', '73.3', '']
    True
    """
    bridge_record[LAT_INDEX] = float(bridge_record[LAT_INDEX])
    bridge_record[LON_INDEX] = float(bridge_record[LON_INDEX])


# This is a suggested helper function for format_data. We provide the
# header and doctring for this function to help you structure your
# solution.
def format_spans(bridge_record: list) -> None:
    """Format the bridge spans data in the bridge record bridge_record.

    >>> record = ['1 -  32/', 'Highway 24 Underpass at Highway 403', '403',
    ...           '43.167233', '-80.275567', '1965', '2014', '2009', '4',
    ...           'Total=64  (1)=12;(2)=19;(3)=21;(4)=12;', '65', '04/13/2012',
    ...           '72.3', '', '72.3', '', '69.5', '', '70', '', '70.3', '',
    ...           '70.5', '', '70.7', '72.9', '']
    >>> format_spans(record)
    >>> record == ['1 -  32/', 'Highway 24 Underpass at Highway 403', '403',
    ...           '43.167233', '-80.275567', '1965', '2014', '2009', 4,
    ...           [12.0, 19.0, 21.0, 12.0], '65', '04/13/2012',
    ...           '72.3', '', '72.3', '', '69.5', '', '70', '', '70.3', '',
    ...           '70.5', '', '70.7', '72.9', '']
    True
    >>> record = ['2 -  43/', 'WEST STREET UNDERPASS', '403', '43.164531', 
    ...          '-80.251582', '1963', '2014', '2007', '3', 
    ...          'Total=48  (1)=16;(2)=16;(3)=16;', '61', '04/13/2012', '71.5', 
    ...          '', '71.5', '', '68.1', '', '69', '', '69.4', '', '69.4', '', 
    ...          '70.3', '73.3', '']
    >>> format_spans(record)
    >>> record == ['2 -  43/', 'WEST STREET UNDERPASS', '403', '43.164531', 
    ...           '-80.251582', '1963', '2014', '2007', 3, [16.0, 16.0, 16.0], 
    ...           '61', '04/13/2012', '71.5', '', '71.5', '', '68.1', '', '69', 
    ...           '', '69.4', '', '69.4', '', '70.3', '73.3', '']
    True
    """
    if isinstance(bridge_record[SPAN_DETAILS_INDEX], list):
        return

    span_details_str = bridge_record[SPAN_DETAILS_INDEX]
    if not span_details_str:
        bridge_record[NUM_SPANS_INDEX] = 0
        bridge_record[SPAN_DETAILS_INDEX] = []
        return

    span_details_str = bridge_record[SPAN_DETAILS_INDEX]
    span_details_str = span_details_str.split(" ")[-1]
    span_parts = span_details_str.strip().split(TO_SEP)
    span_lengths = [float(span_part.split(FROM_SEP)[1].strip())
                    for span_part in span_parts if span_part]
    bridge_record[NUM_SPANS_INDEX] = len(span_lengths)
    bridge_record[SPAN_DETAILS_INDEX] = span_lengths


# This is a suggested helper function for format_data. We provide the
# header and doctring for this function to help you structure your
# solution.
def format_length(bridge_record: list) -> None:
    """Format the bridge length data in the bridge record bridge_record.

    >>> record = ['1 -  32/', 'Highway 24 Underpass at Highway 403', '403',
    ...           '43.167233', '-80.275567', '1965', '2014', '2009', '4',
    ...           'Total=64  (1)=12;(2)=19;(3)=21;(4)=12;', '65', '04/13/2012',
    ...           '72.3', '', '72.3', '', '69.5', '', '70', '', '70.3', '',
    ...           '70.5', '', '70.7', '72.9', '']
    >>> format_length(record)
    >>> record == ['1 -  32/', 'Highway 24 Underpass at Highway 403', '403',
    ...            '43.167233', '-80.275567', '1965', '2014', '2009', '4',
    ...            'Total=64  (1)=12;(2)=19;(3)=21;(4)=12;', 65, '04/13/2012',
    ...            '72.3', '', '72.3', '', '69.5', '', '70', '', '70.3', '',
    ...            '70.5', '', '70.7', '72.9', '']
    True
    >>> record = ['2 -  43/', 'WEST STREET UNDERPASS', '403', '43.164531', 
    ...           '-80.251582', '1963', '2014', '2007', '3', 
    ...           'Total=48  (1)=16;(2)=16;(3)=16;', '61.2', '04/13/2012', 
    ...           '71.5', '', '71.5', '', '68.1', '', '69', '', '69.4', '', 
    ...           '69.4', '', '70.3', '73.3', '']
    >>> format_length(record)
    >>> record == ['2 -  43/', 'WEST STREET UNDERPASS', '403', '43.164531', 
    ...            '-80.251582', '1963', '2014', '2007', '3', 
    ...            'Total=48  (1)=16;(2)=16;(3)=16;', 61.2, '04/13/2012', 
    ...            '71.5', '', '71.5', '', '68.1', '', '69', '', '69.4', '', 
    ...            '69.4', '', '70.3', '73.3', '']
    True
    """
    length_str = bridge_record[LENGTH_INDEX]
    bridge_record[LENGTH_INDEX] = float(length_str) if length_str else 0


# This is a suggested helper function for format_data. We provide the
# header and doctring for this function to help you structure your
# solution.
def format_bcis(bridge_record: list) -> None:
    """Format the bridge BCI data in the bridge record bridge_record.
    
    >>> record = ['1 -  32/', 'Highway 24 Underpass at Highway 403', '403',
    ...           '43.167233', '-80.275567', '1965', '2014', '2009', '4',
    ...           'Total=64  (1)=12;(2)=19;(3)=21;(4)=12;', '65', '04/13/2012',
    ...           '72.3', '', '72.3', '', '69.5', '', '70', '', '70.3', '',
    ...           '70.5', '', '70.7', '72.9', '']
    >>> format_bcis(record)
    >>> record == ['1 -  32/', 'Highway 24 Underpass at Highway 403', '403',
    ...           '43.167233', '-80.275567', '1965', '2014', '2009', '4',
    ...           'Total=64  (1)=12;(2)=19;(3)=21;(4)=12;', '65', '04/13/2012',
    ...           [72.3, 69.5, 70.0, 70.3, 70.5, 70.7, 72.9]]
    True
    >>> record = ['2 -  30/', 'SAUBLE RIVER BRIDGE, WEST OF ALLENFORD', 
    ...           '21', '44.532425',  '-81.196354', '2014', '', '', '1', 
    ...           'Total=32  (1)=32;', '33.1', '07/25/2013', '60.9' , 
    ...           '60.9' , '', '61.8', '', '63.2', '', '65' , '64.3', 
    ...           '64.1', '', '66.7', '', '67.1', '']
    >>> format_bcis(record)
    >>> record == ['2 -  30/', 'SAUBLE RIVER BRIDGE, WEST OF ALLENFORD',
    ...            '21', '44.532425', '-81.196354', '2014', '', '', '1',
    ...            'Total=32  (1)=32;', '33.1', '07/25/2013',
    ...            [60.9, 61.8, 63.2, 65.0, 64.3, 64.1, 66.7, 67.1]]
    True
    """
    bcis = []
    for value in bridge_record[BCIS_INDEX + 1:]:
        if value != '':
            bcis.append(float(value))
    bridge_record[BCIS_INDEX:] = [bcis]


if __name__ == '__main__':
    import doctest
    doctest.testmod()

    # To test your code with larger lists, you can uncomment the code below to
    # read data from the provided CSV file.
    # with open('bridge_data.csv', encoding='utf-8') as bridge_data_file:
    #     BRIDGES = read_data(bridge_data_file)
    # format_data(BRIDGES)

    # For example:
    # print(get_bridge(BRIDGES, 3))
    # EXPECTED = [3, 'NORTH PARK STEET UNDERPASS', '403', 43.165918, -80.263791,
    #             '1962', '2013', '2009', 4, [12.2, 18.0, 18.0, 12.2], 60.8,
    #             '04/13/2012', [71.4, 69.9, 67.7, 68.9, 69.1, 69.9, 72.8]]
    # print('Testing get_bridge: ', get_bridge(BRIDGES, 3) == EXPECTED)

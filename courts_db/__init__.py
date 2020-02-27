from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

from .utils import load_courts_db, gather_regexes, make_court_dictionary
from string import Template, punctuation
from glob import iglob
from io import open

from datetime import datetime
import json
import os
import re
import six

try:
    courts = load_courts_db()
    court_dict = make_court_dictionary(courts)
    regexes = gather_regexes(courts)
except:
    pass


def find_court_ids_by_name(court_str):

    if not type(court_str) == six.text_type:
        court_str = unicode(court_str)

    assert (
        type(court_str) == six.text_type
    ), "court_str is not a text type, it's of type %s" % type(court_str)

    court_matches = set()
    for regex, court_id, court_name, court_type in regexes:
        match = re.search(regex, court_str)
        if match:
            court_matches.add(court_id)

    return list(court_matches)


def filter_courts_by_date(matches, date_found, strict_dates=False):
    """ Filter IDs by date found.

    Strict dates should be more useful as dates are filled in.
    :param matches:
    :param date_found: datetime object
    :param strict_dates: Boolean that helps tell the sytsem how to handle
    null dates in courts-db
    :return: List of court IDs matched
    """
    assert (
        type(date_found) is datetime
    ), "date_found is not a date object, it's of type %s" % type(date_found)

    results = [court for court in courts if court["id"] in matches]
    filtered_results = []
    for result in results:
        for date_object in result["dates"]:
            date_start = date_object["start"]
            date_end = date_object["end"]
            if strict_dates == False:
                if date_start == None:
                    date_start = "1600-01-01"
                if date_end == None:
                    date_end = "2100-01-01"
            if strict_dates:
                if date_start == None:
                    continue
                if date_end == None:
                    date_end = "2100-01-01"

            date_start = datetime.strptime(date_start, "%Y-%m-%d")
            date_end = datetime.strptime(date_end, "%Y-%m-%d")

            if date_start <= date_found <= date_end:
                filtered_results.append(result["id"])

    return filtered_results


def filter_courts_by_bankruptcy(matches, bankruptcy):
    results = [court for court in courts if court["id"] in matches]
    if bankruptcy:
        return [
            court["id"] for court in results if court["type"] == "bankruptcy"
        ]
    return [court["id"] for court in results if court["type"] != "bankruptcy"]


def find_court_by_id(court_id):
    return [court for court in courts if court["id"] == court_id]


def find_court(
    court_str, bankruptcy=None, date_found=None, strict_dates=False
):
    """

    :param court_str:
    :param bankruptcy:
    :param state:
    :param date_found:
    :param strict:
    :return:
    """

    matches = find_court_ids_by_name(court_str)
    if bankruptcy is not None:
        matches = filter_courts_by_bankruptcy(
            matches=matches, bankruptcy=bankruptcy
        )
    if date_found:
        matches = filter_courts_by_date(
            matches=matches, date_found=date_found, strict_dates=strict_dates
        )

    return matches

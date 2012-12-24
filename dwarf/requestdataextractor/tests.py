"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

from requestdataextractor.extractors import (detect_browser,
                                        detect_OS,
                                        detect_browser_and_OS,
                                        detect_country_location_with_geoip)
from requestdataextractor.test_data import test_data


class ExtractorTest(TestCase):

    def test_browser_detection(self):
        for i in test_data:
            self.assertEqual(i[0], detect_browser(i[2]))

    def test_OS_detection(self):
        for i in test_data:
            self.assertEqual(i[1], detect_OS(i[2]))

    def test_OS_browser_detail_detection(self):
        for i in test_data:
            correct_tuple = (i[3], i[0], i[1])
            self.assertEqual(correct_tuple, detect_browser_and_OS(i[2]))

    def test_detect_country_location_with_geoip(self):
        ip = "72.14.207.99"
        correct_res = {'country_code': 'US', 'country_name': 'United States'}

        result = detect_country_location_with_geoip(ip)

        self.assertEqual(correct_res, result)

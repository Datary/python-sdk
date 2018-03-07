# -*- coding: utf-8 -*-
"""
Datary python sdk Requests test file
"""
import mock
import requests

from datary.test.test_datary import DataryTestCase
from datary.test.mock_requests import MockRequestResponse


class DataryRequestsTestCase(DataryTestCase):
    """
    DataryRequests Test case
    """

    @mock.patch('datary.requests.requests.requests')
    @mock.patch('datary.requests.requests.time')
    def test_request(self, mock_time, mock_requests):
        """
        Test get_request
        =============   =============   =======================================
        Parameter       Type            Description
        =============   =============   =======================================
        mock_request    mock            Mock datary.requests.requests.request
                                        function
        =============   =============   =======================================
        """

        mock_requests.get.return_value = MockRequestResponse(
            "ok", headers={'x-set-token': self.test_token})
        mock_requests.post.return_value = MockRequestResponse(
            "ok", headers={'x-set-token': self.test_token})
        mock_requests.put.return_value = MockRequestResponse(
            "ok", headers={'x-set-token': self.test_token})
        mock_requests.delete.return_value = MockRequestResponse(
            "ok", headers={'x-set-token': self.test_token})

        # test GET
        result1 = self.datary.request(self.url, 'GET')
        self.assertEqual(result1.text, 'ok')

        # test POST
        result2 = self.datary.request(self.url, 'POST')
        self.assertEqual(result2.text, 'ok')

        # test PUT
        result3 = self.datary.request(self.url, 'PUT')
        self.assertEqual(result3.text, 'ok')

        # test DELETED
        result4 = self.datary.request(self.url, 'DELETE')
        self.assertEqual(result4.text, 'ok')

        # test UNKNOWK http method
        with self.assertRaises(Exception):
            self.datary.request(self.url, 'UNKWOWN')

        # test status code wrong
        mock_requests.get.return_value = MockRequestResponse(
            "err", status_code=500)
        result5 = self.datary.request(self.url, 'GET')
        self.assertEqual(result5, None)

        # test status code 429
        responses_429_test = [
            MockRequestResponse(
                "Request limit exceeded, must wait for XX seconds",
                status_code=429),
            MockRequestResponse(
                "Request limit exceeded, must wait for XX seconds",
                status_code=429),
            MockRequestResponse(
                "Request limit exceeded, must wait for XX seconds",
                status_code=429),
            MockRequestResponse(
                "Everything OK",
                status_code=200)
            ]

        mock_requests.get.side_effect = iter(responses_429_test)

        result7 = self.datary.request(self.url, 'GET')
        self.assertEqual(result7, None)

        # upgrade tries limit
        self.datary.tries_limit = 4
        mock_requests.get.side_effect = iter(responses_429_test)

        result8 = self.datary.request(self.url, 'GET')
        self.assertEqual(result8.text, 'Everything OK')

        self.assertEqual(mock_time.sleep.call_count, 3+3)

        mock_requests.get.side_effect = requests.RequestException('err')
        result6 = self.datary.request(self.url, 'GET')
        self.assertEqual(result6, None)

        self.assertEqual(mock_requests.get.call_count, 10)
        self.assertEqual(mock_requests.post.call_count, 1)
        self.assertEqual(mock_requests.put.call_count, 1)
        self.assertEqual(mock_requests.delete.call_count, 1)

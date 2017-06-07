# -*- coding: utf-8 -*-
"""
Datary python sdk Auth test file
"""
import mock

from datary import Datary
from datary.test.test_datary import DataryTestCase
from datary.test.mock_requests import MockRequestResponse


class DataryAuthTestCase(DataryTestCase):
    """
    DataryAuth Test case
    """

    @mock.patch('datary.Datary.request')
    def test_get_user_token(self, mock_request):

        # Assert init class data & token introduced by args
        self.assertEqual(self.datary.username, self.test_username)
        self.assertEqual(self.datary.password, self.test_password)
        self.assertEqual(self.datary.token, self.test_token)
        self.assertEqual(mock_request.call_count, 0)

        # Assert get token in __init__
        mock_request.return_value = MockRequestResponse(
            "", headers={'x-set-token': self.test_token})
        self.datary = Datary(**{'username': 'pepe', 'password': 'pass'})
        self.assertEqual(mock_request.call_count, 1)

        # Assert get token by the method without args.
        mock_request.return_value = MockRequestResponse(
            "", headers={'x-set-token': self.test_token})
        token1 = self.datary.get_user_token()
        self.assertEqual(token1, self.test_token)

        # Assert get token by method     with args.
        mock_request.return_value = MockRequestResponse(
            "", headers={'x-set-token': '456'})
        token2 = self.datary.get_user_token('maria', 'pass2')
        self.assertEqual(token2, '456')

        mock_request.return_value = MockRequestResponse("", headers={})
        token3 = self.datary.get_user_token('maria', 'pass2')
        self.assertEqual(token3, '')

        self.assertEqual(mock_request.call_count, 4)

    @mock.patch('datary.requests.requests.requests')
    def test_sign_out(self, mock_request):

        # Fail sign out
        mock_request.get.return_value = MockRequestResponse(
            "Err", status_code=500)
        self.datary.sign_out()
        self.assertEqual(self.datary.token, self.test_token)
        self.assertEqual(mock_request.get.call_count, 1)

        # reset mock
        mock_request.get.reset_mock()

        # Succes sign out
        mock_request.get.return_value = MockRequestResponse(
            "OK", status_code=200)
        self.assertEqual(self.datary.token, self.test_token)
        self.datary.sign_out()
        self.assertEqual(self.datary.token, None)
        self.assertEqual(mock_request.get.call_count, 1)

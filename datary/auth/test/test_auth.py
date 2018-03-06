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

    def setUp(self):
        self.test_token = '123'
        self.test_username = 'pepe'
        self.test_password = 'pass'
        self.test_commit_limit = 30

        self.test_token2 = '456'
        self.test_username2 = 'manolo'
        self.test_password2 = 'ssap'
        self.test_commit_limit2 = 12

    @mock.patch('datary.requests.requests.requests.post')
    def test_properties(self, mock_request):
        """
        Test Datary auth getter/setter properties
        """

        mock_request.return_value = MockRequestResponse(
            "", headers={'x-set-token': self.test_token})
        self.datary = Datary(**{
            'username': self.test_username,
            'password': self.test_password})
        self.assertEqual(mock_request.call_count, 1)

        self.assertEqual(self.datary.username, self.test_username)
        self.assertEqual(self.datary.password, self.test_password)
        self.assertEqual(self.datary.token, self.test_token)
        self.assertEqual(self.datary.commit_limit, self.test_commit_limit)
        self.assertIn(
            self.datary.token, self.datary.headers.get('Authorization'))

        self.datary.username = self.test_username2
        self.datary.password = self.test_password2
        self.datary.token = self.test_token2
        self.datary.commit_limit = self.test_commit_limit2

        self.assertEqual(self.datary.username, self.test_username2)
        self.assertEqual(self.datary.password, self.test_password2)
        self.assertEqual(self.datary.token, self.test_token2)
        self.assertEqual(self.datary.commit_limit, self.test_commit_limit2)
        self.assertIn(
            self.datary.token, self.datary.headers.get('Authorization'))

        # no username sig-in
        self.datary.username = None
        self.datary.token = None
        self.datary.sign_in()
        self.assertEqual(self.datary.token, None)

        # no password sig-in
        self.datary.username = 'pepe'
        self.datary.password = None
        self.datary.token = None
        self.datary.sign_in()
        self.assertEqual(self.datary.token, None)

    @mock.patch('datary.auth.DataryAuth.delete_member_session')
    def test_sign_out(self, mock_delete_member_session):

        self.datary.sign_out()
        self.assertEqual(mock_delete_member_session.call_count, 1)

    @mock.patch('datary.requests.requests.requests.delete')
    def test_delete_member_session(self, mock_request):
        # Fail sign out
        mock_request.return_value = MockRequestResponse(
            "Err", status_code=500)
        self.datary.delete_member_session()
        self.assertEqual(self.datary.token, self.test_token)
        self.assertEqual(mock_request.call_count, 1)

        # reset mock
        mock_request.reset_mock()

        # Succes sign out
        mock_request.return_value = MockRequestResponse(
            "OK", status_code=200)

        self.assertEqual(self.datary.token, self.test_token)
        self.datary.delete_member_session()
        self.assertEqual(self.datary.token, None)
        self.assertEqual(mock_request.call_count, 1)

# ##########################################################################
#                           DEPRECATED
# ##########################################################################

    @mock.patch('datary.requests.requests.requests.post')
    def test_get_connection_sign_in(self, mock_request):
        """
        Test datary auth get_user_token
        """

        # init datary
        self.datary = Datary(**{
            'username': self.test_username,
            'password': self.test_password,
            'token': self.test_token})

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
        token1 = self.datary.get_connection_sign_in()
        self.assertEqual(token1, self.test_token)

        # Assert get token by method     with args.
        mock_request.return_value = MockRequestResponse(
            "", headers={'x-set-token': '456'})
        token2 = self.datary.get_connection_sign_in('maria', 'pass2')
        self.assertEqual(token2, '456')

        mock_request.return_value = MockRequestResponse("", headers={})
        token3 = self.datary.get_connection_sign_in('maria', 'pass2')
        self.assertEqual(token3, '')

        self.assertEqual(mock_request.call_count, 4)

    @mock.patch('datary.requests.requests.requests.get')
    def test_get_connection_sign_out(self, mock_request):
        """
        Test datary auth sign_out
        """

        # init datary
        self.datary = Datary(**{
            'username': self.test_username,
            'password': self.test_password,
            'token': self.test_token})

        # Fail sign out
        mock_request.return_value = MockRequestResponse(
            "Err", status_code=500)
        self.datary.get_connection_sign_out()
        self.assertEqual(self.datary.token, self.test_token)
        self.assertEqual(mock_request.call_count, 1)

        # reset mock
        mock_request.reset_mock()

        # Succes sign out
        mock_request.return_value = MockRequestResponse(
            "OK", status_code=200)

        self.assertEqual(self.datary.token, self.test_token)
        self.datary.get_connection_sign_out()
        self.assertEqual(self.datary.token, None)
        self.assertEqual(mock_request.call_count, 1)

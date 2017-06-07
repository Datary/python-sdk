# -*- coding: utf-8 -*-
"""
Datary python sdk Add Operation test file
"""
import mock

from datary.test.test_datary import DataryTestCase
from datary.test.mock_requests import MockRequestResponse


class DataryAddOperationTestCase(DataryTestCase):
    """
    AddOperation Test case
    """

    @mock.patch('datary.Datary.request')
    def test_add_dir(self, mock_request):
        """
        Test add_dir
        """
        mock_request.return_value = MockRequestResponse("")
        self.datary.add_dir(self.json_repo.get(
            'workdir', {}).get('uuid'), 'path', 'dirname')
        mock_request.return_value = None
        self.datary.add_dir(self.json_repo.get(
            'workdir', {}).get('uuid'), 'path', 'dirname')
        self.assertEqual(mock_request.call_count, 2)

    @mock.patch('datary.Datary.request')
    def test_add_file(self, mock_request):
        """
        Test add_file
        """
        mock_request.return_value = MockRequestResponse("")
        self.datary.add_file(self.json_repo.get(
            'workdir', {}).get('uuid'), self.element)
        mock_request.return_value = None
        self.datary.add_file(self.json_repo.get(
            'workdir', {}).get('uuid'), self.element)
        self.assertEqual(mock_request.call_count, 2)

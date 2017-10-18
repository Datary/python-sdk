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

        # small element
        self.datary.add_file(self.json_repo.get(
            'workdir', {}).get('uuid'), self.element)

        # update element meta size
        self.element['data']['meta']['size'] = 999999999

        self.datary.add_file(self.json_repo.get(
            'workdir', {}).get('uuid'), self.element)

        self.element['data']['meta']['size'] = 222

        mock_request.return_value = None
        self.datary.add_file(self.json_repo.get(
            'workdir', {}).get('uuid'), self.element)

        self.assertEqual(mock_request.call_count, 3)
        self.assertTrue("'Content-Type': 'application/x-www-form-urlencoded'" in str(mock_request.call_args_list[0]))
        self.assertTrue("'Content-Type': 'application/x-www-form-urlencoded'" in str(mock_request.call_args_list[1]))

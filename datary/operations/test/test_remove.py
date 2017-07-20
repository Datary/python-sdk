# -*- coding: utf-8 -*-
"""
Datary python sdk Remove Operation test file
"""
import mock

from datary.test.test_datary import DataryTestCase
from datary.test.mock_requests import MockRequestResponse


class DataryRemoveOperationTestCase(DataryTestCase):
    """
    RemoveOperation Test case
    """

    @mock.patch('datary.Datary.request')
    def test_delete_dir(self, mock_request):
        mock_request.return_value = MockRequestResponse("")
        self.datary.delete_dir(self.json_repo.get(
            'workdir', {}).get('uuid'), "path", "dirname")
        mock_request.return_value = None
        self.datary.delete_dir(self.json_repo.get(
            'workdir', {}).get('uuid'), "path", "dirname")
        self.assertEqual(mock_request.call_count, 2)

    @mock.patch('datary.Datary.request')
    def test_delete_file(self, mock_request):
        """
        Test operation remove delete_file
        """
        mock_request.return_value = MockRequestResponse("")
        self.datary.delete_file(self.json_repo.get(
            'workdir', {}).get('uuid'), self.element)
        mock_request.return_value = None
        self.datary.delete_file(self.json_repo.get(
            'workdir', {}).get('uuid'), self.element)
        self.assertEqual(mock_request.call_count, 2)

    @mock.patch('datary.Datary.request')
    def test_delete_inode(self, mock_request):
        """
        Test operation remove delete_inode
        """
        mock_request.return_value = MockRequestResponse("")
        self.datary.delete_inode(self.json_repo.get(
            'workdir', {}).get('uuid'), self.inode)
        mock_request.return_value = None
        self.datary.delete_inode(self.json_repo.get(
            'workdir', {}).get('uuid'), self.inode)
        self.assertEqual(mock_request.call_count, 2)

        mock_request.side_effect = Exception('Test Err exception')
        with self.assertRaises(Exception):
            self.datary.delete_inode(
                self.json_repo.get('workdir', {}).get('uuid'), self.inode)

    @mock.patch('datary.Datary.request')
    def test_clear_index(self, mock_request):
        """
        Test operation remove clear_index
        """
        mock_request.return_value = MockRequestResponse("", json={})
        original = self.datary.clear_index(self.wdir_uuid)
        self.assertEqual(mock_request.call_count, 1)
        self.assertEqual(original, True)

        mock_request.reset_mock()
        mock_request.return_value = None
        original2 = self.datary.clear_index(self.wdir_uuid)
        self.assertEqual(mock_request.call_count, 1)
        self.assertEqual(original2, False)

    @mock.patch('datary.Datary.delete_file')
    @mock.patch('datary.Datary.get_wdir_filetree')
    @mock.patch('datary.Datary.commit')
    @mock.patch('datary.Datary.clear_index')
    @mock.patch('datary.Datary.get_describerepo')
    def test_clean_repo(self, mock_get_describerepo, mock_clear_index,
                        mock_commit, mock_get_wdir_filetree, mock_delete_file):
        """
        Test operation remove clean_repo
        """

        mock_get_describerepo.return_value = self.json_repo
        mock_get_wdir_filetree.return_value = self.filetree

        self.datary.clean_repo(self.repo_uuid)

        self.assertEqual(mock_commit.call_count, 1)
        self.assertEqual(mock_delete_file.call_count, 3)
        self.assertEqual(mock_clear_index.call_count, 1)
        self.assertEqual(mock_get_describerepo.call_count, 1)
        self.assertEqual(mock_get_wdir_filetree.call_count, 1)

        # reset mocks
        mock_get_describerepo.reset_mock()
        mock_clear_index.reset_mock()
        mock_commit.reset_mock()
        mock_get_wdir_filetree.reset_mock()
        mock_delete_file.reset_mock()

        # describe repo retrieve None
        mock_get_wdir_filetree.return_value = self.filetree
        mock_get_describerepo.return_value = None

        self.datary.clean_repo(self.repo_uuid)

        self.assertEqual(mock_commit.call_count, 0)
        self.assertEqual(mock_delete_file.call_count, 0)
        self.assertEqual(mock_clear_index.call_count, 0)
        self.assertEqual(mock_get_describerepo.call_count, 1)
        self.assertEqual(mock_get_wdir_filetree.call_count, 0)

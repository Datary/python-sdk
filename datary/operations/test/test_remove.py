# -*- coding: utf-8 -*-
import mock

from datary.test.test_datary import DataryTestCase
from datary.test.mock_requests import MockRequestResponse


class DataryRemoveOperationTestCase(DataryTestCase):

    @mock.patch('datary.Datary.request')
    def test_delete_dir(self, mock_request):
        # TODO: Unkwnown api method changes??
        mock_request.return_value = MockRequestResponse("")
        self.datary.delete_dir(self.json_repo.get(
            'workdir', {}).get('uuid'), "path", "dirname")
        mock_request.return_value = None
        self.datary.delete_dir(self.json_repo.get(
            'workdir', {}).get('uuid'), "path", "dirname")
        self.assertEqual(mock_request.call_count, 2)

    @mock.patch('datary.Datary.request')
    def test_delete_file(self, mock_request):
        # TODO: Unkwnown api method changes??
        mock_request.return_value = MockRequestResponse("")
        self.datary.delete_file(self.json_repo.get(
            'workdir', {}).get('uuid'), self.element)
        mock_request.return_value = None
        self.datary.delete_file(self.json_repo.get(
            'workdir', {}).get('uuid'), self.element)
        self.assertEqual(mock_request.call_count, 2)

    @mock.patch('datary.Datary.request')
    def test_delete_inode(self, mock_request):
        mock_request.return_value = MockRequestResponse("")
        self.datary.delete_inode(self.json_repo.get(
            'workdir', {}).get('uuid'), self.inode)
        mock_request.return_value = None
        self.datary.delete_inode(self.json_repo.get(
            'workdir', {}).get('uuid'), self.inode)
        self.assertEqual(mock_request.call_count, 2)

        with self.assertRaises(Exception):
            self.datary.delete_inode(
                self.json_repo.get('workdir', {}).get('uuid'))

    @mock.patch('datary.Datary.request')
    def test_clear_index(self, mock_request):
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
    @mock.patch('datary.Datary.add_file')
    @mock.patch('datary.Datary.get_wdir_filetree')
    @mock.patch('datary.Datary.commit')
    @mock.patch('datary.Datary.clear_index')
    @mock.patch('datary.Datary.get_describerepo')
    def test_clean_repo(self, mock_get_describerepo, mock_clear_index,
                        mock_commit, mock_get_wdir_filetree, mock_add_file,
                        mock_delete_file):

        mock_get_describerepo.return_value = self.json_repo
        mock_get_wdir_filetree.return_value = self.filetree

        self.datary.clean_repo(self.repo_uuid)

        mock_get_describerepo.return_value = None
        self.datary.clean_repo(self.repo_uuid)

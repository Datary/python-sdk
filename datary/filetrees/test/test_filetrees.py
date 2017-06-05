# -*- coding: utf-8 -*-
import mock

from datary.test.test_datary import DataryTestCase
from datary.test.mock_requests import MockRequestResponse


class DataryFiletreesTestCase(DataryTestCase):

    @mock.patch('datary.Datary.request')
    def test_get_commit_filetree(self, mock_request):
        mock_request.return_value = MockRequestResponse("", json=self.wdir_json.get('filetree'))
        filetree = self.datary.get_commit_filetree(self.repo_uuid, self.commit_sha1)
        self.assertEqual(mock_request.call_count, 1)
        assert(isinstance(filetree, dict))

    @mock.patch('datary.Datary.request')
    def test_get_wdir_filetree(self, mock_request):
        mock_request.return_value = MockRequestResponse("", json=self.wdir_json.get('changes'))
        changes = self.datary.get_wdir_filetree(self.repo_uuid)
        self.assertEqual(mock_request.call_count, 1)
        assert(isinstance(changes, dict))

    @mock.patch('datary.Datary.request')
    @mock.patch('datary.Datary.get_describerepo')
    def test_get_wdir_changes(self, mock_describerepo, mock_request):
        mock_request.return_value = MockRequestResponse("", json=self.wdir_json.get('filetree'))
        filetree = self.datary.get_wdir_changes(self.wdir_uuid)
        self.assertEqual(mock_request.call_count, 1)
        assert(isinstance(filetree, dict))

        mock_describerepo.return_value = self.json_repo
        mock_request.return_value = MockRequestResponse("", json=self.wdir_json.get('filetree'))
        filetree = self.datary.get_wdir_changes(repo_uuid=self.repo_uuid)
        self.assertEqual(mock_request.call_count, 2)
        assert(isinstance(filetree, dict))

    def test_format_wdir_changes_to_filetreeformat(self):
        treeformated_changes = self.datary.format_wdir_changes_to_filetreeformat(self.changes.values())

        self.assertEqual(len(treeformated_changes.keys()), 3)
        self.assertEqual(treeformated_changes.get('a'), 'inode2_changes')
        self.assertEqual(treeformated_changes.get('b'), {'bb': 'inode1_changes'})
        self.assertEqual(treeformated_changes.get('d'), 'inode3_changes')
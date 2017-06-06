# -*- coding: utf-8 -*-
import mock

from datary.test.test_datary import DataryTestCase
from datary.test.mock_requests import MockRequestResponse


class DataryDatasetsTestCase(DataryTestCase):

    @mock.patch('datary.Datary.request')
    def test_get_metadata(self, mock_request):
        mock_request.return_value = MockRequestResponse("", json=self.metadata)
        metadata = self.datary.get_metadata(self.repo_uuid, self.dataset_uuid)
        self.assertEqual(mock_request.call_count, 1)
        assert(isinstance(metadata, dict))
        self.assertEqual(metadata, self.metadata)

        mock_request.return_value = None
        metadata2 = self.datary.get_metadata(self.repo_uuid, self.dataset_uuid)
        assert(isinstance(metadata2, dict))
        self.assertEqual(metadata2, {})

    @mock.patch('datary.Datary.request')
    def test_get_original(self, mock_request):

        mock_request.return_value = MockRequestResponse("", json=self.original)
        original = self.datary.get_original(self.dataset_uuid, self.repo_uuid)
        self.assertEqual(mock_request.call_count, 1)
        assert(isinstance(original, dict))
        self.assertEqual(original, self.original)

        mock_request.reset_mock()

        # not dataset_uuid, introduced
        original2 = self.datary.get_original(
            self.dataset_uuid, self.repo_uuid, self.wdir_uuid)
        self.assertEqual(mock_request.call_count, 1)
        assert(isinstance(original2, dict))
        self.assertEqual(original2, self.original)

        mock_request.reset_mock()

        # not dataset_uuid, introduced
        original3 = self.datary.get_original(
            self.dataset_uuid, wdir_uuid=self.wdir_uuid)
        self.assertEqual(mock_request.call_count, 1)
        assert(isinstance(original3, dict))
        self.assertEqual(original3, self.original)

        mock_request.reset_mock()
        mock_request.side_effect = iter(
            [None, MockRequestResponse("", json=self.original)])
        original4 = self.datary.get_original(self.dataset_uuid, self.repo_uuid)
        self.assertEqual(mock_request.call_count, 2)
        assert(isinstance(original4, dict))
        self.assertEqual(original4, self.original)

        mock_request.reset_mock()
        mock_request.side_effect = iter([None, None])
        original4b = self.datary.get_original(
            self.dataset_uuid, self.repo_uuid)
        self.assertEqual(mock_request.call_count, 2)
        assert(isinstance(original4b, dict))
        self.assertEqual(original4b, {})

        mock_request.reset_mock()
        # not dataset_uuid, introduced
        original5 = self.datary.get_original(None)
        self.assertEqual(mock_request.call_count, 0)
        assert(isinstance(original5, dict))
        self.assertEqual(original5, {})

    @mock.patch('datary.Datary.get_wdir_filetree')
    @mock.patch('datary.Datary.get_wdir_changes')
    def test_get_dataset_uuid(self, mock_get_wdir_changes,
                              mock_get_wdir_filetree):

        mock_get_wdir_filetree.return_value = self.filetree
        mock_get_wdir_changes.return_value = self.changes

        path = 'b'
        filename = 'bb'

        empty_result = self.datary.get_dataset_uuid(self.wdir_uuid)
        self.assertEqual(empty_result, None)

        from_changes_result = self.datary.get_dataset_uuid(
            self.wdir_uuid, path, filename)
        self.assertEqual(from_changes_result, 'inode1_changes')
        self.assertEqual(mock_get_wdir_filetree.call_count, 1)
        self.assertEqual(mock_get_wdir_changes.call_count, 1)

        mock_get_wdir_filetree.reset_mock()
        mock_get_wdir_changes.reset_mock()

        # retrive from filetree
        path = ''
        filename = 'c'

        from_commit_result = self.datary.get_dataset_uuid(
            self.wdir_uuid, path, filename)

        self.assertEqual(from_commit_result, 'c_sha1')
        self.assertEqual(mock_get_wdir_filetree.call_count, 1)
        self.assertEqual(mock_get_wdir_changes.call_count, 1)

        mock_get_wdir_filetree.reset_mock()
        mock_get_wdir_changes.reset_mock()

        # NOT exists
        path = 'bb'
        filename = 'b'

        no_result = self.datary.get_dataset_uuid(
            self.wdir_uuid, path, filename)
        self.assertEqual(no_result, None)
        self.assertEqual(mock_get_wdir_filetree.call_count, 1)
        self.assertEqual(mock_get_wdir_changes.call_count, 1)

    @mock.patch('datary.Datary.request')
    def test_get_commited_dataset_uuid(self, mock_request):

        # no args path and filename introduced
        mock_request.return_value = MockRequestResponse(
            "", json=self.dataset_uuid)
        result_no_pathname = self.datary.get_commited_dataset_uuid(
            self.wdir_uuid)
        self.assertEqual(result_no_pathname, {})
        self.assertEqual(mock_request.call_count, 0)

        # good case
        result = self.datary.get_commited_dataset_uuid(
            self.wdir_uuid, 'path', 'filename')
        self.assertEqual(result, self.dataset_uuid)
        self.assertEqual(mock_request.call_count, 1)

        # datary request return None
        mock_request.reset_mock()
        mock_request.return_value = None

        no_response_result = self.datary.get_commited_dataset_uuid(
            self.wdir_uuid, 'path', 'filename')
        self.assertEqual(no_response_result, {})
        self.assertEqual(mock_request.call_count, 1)

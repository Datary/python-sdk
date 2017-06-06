# -*- coding: utf-8 -*-
import mock

from unittest.mock import patch
from datary.test.test_datary import DataryTestCase
from datary.test.mock_requests import MockRequestResponse


class DataryCommitsTestCase(DataryTestCase):

    @mock.patch('datary.Datary.request')
    def test_commit(self, mock_request):

        # TODO: Review commit api method  return
        mock_request.return_value = MockRequestResponse("a")
        self.datary.commit(self.repo_uuid, "test commit msg")

        mock_request.return_value = None
        self.datary.commit(self.repo_uuid, "test commit msg")

        self.assertEqual(mock_request.call_count, 2)

    @mock.patch('datary.Datary.get_describerepo')
    @mock.patch('datary.Datary.get_commit_filetree')
    @mock.patch('datary.Datary.get_metadata')
    def test_recollect_last_commit(self, mock_metadata, mock_filetree,
                                   mock_get_describerepo):
        mock_filetree.return_value = self.filetree

        mock_get_describerepo.return_value = self.json_repo
        mock_metadata.return_value.json.return_value = self.metadata
        result = self.datary.recollect_last_commit({'uuid': self.repo_uuid})
        assert mock_filetree.called
        assert mock_get_describerepo.called

        mock_get_describerepo.return_value = None
        result2 = self.datary.recollect_last_commit({'uuid': self.repo_uuid})

        mock_filetree.return_value = None
        mock_get_describerepo.return_value = self.json_repo
        result3 = self.datary.recollect_last_commit({'uuid': self.repo_uuid})

        mock_get_describerepo.return_value = {}
        result4 = self.datary.recollect_last_commit({})

        mock_get_describerepo.return_value = {'apex': {}}
        result5 = self.datary.recollect_last_commit({})

        mock_get_describerepo.return_value = {'apex': {}}
        result6 = self.datary.recollect_last_commit({'apex': {}})

        assert isinstance(result, list)
        self.assertEqual(len(result), 3)

        for x in result:
            self.assertEqual(len(x), 4)

        assert isinstance(result2, list)
        assert isinstance(result3, list)
        assert isinstance(result4, list)
        assert isinstance(result5, list)
        assert isinstance(result6, list)
        self.assertEqual(result4, [])
        self.assertEqual(result5, [])
        self.assertEqual(result6, [])

    def test_make_index(self):
        lista = self.commit_test1
        result = self.datary.make_index(lista)
        expected_values = ['aa_sha1', 'caa_sha1', 'bb_sha1', 'dd_sha1']

        assert isinstance(result, dict)
        for element in result.values():
            assert element.get('sha1') in expected_values

    def test_compare_commits(self):
        expected = {
            'add': ['caa_sha1'],
            'delete': ['bb_sha1'],
            'update': ['dd2_sha1']
        }

        result = self.datary.compare_commits(
            self.commit_test1, self.commit_test2)

        self.assertEqual(len(result.get('add')), 1)
        self.assertEqual(len(result.get('update')), 1)
        self.assertEqual(len(result.get('delete')), 1)

        for k, v in expected.items():
            elements_sha1 = [element.get('sha1') for element in result.get(k)]
            for sha1 in v:
                sha1 in elements_sha1

        with patch('datary.Datary.make_index') as mock_makeindex:
            mock_makeindex.side_effect = Exception('Test Exception')
            result2 = self.datary.compare_commits(
                self.commit_test1, self.commit_test2)

            assert(isinstance(result2, dict))
            self.assertEqual(result2, {'update': [], 'delete': [], 'add': []})

    @mock.patch('datary.Datary.delete_file')
    @mock.patch('datary.Datary.add_file')
    @mock.patch('datary.Datary.modify_file')
    def test_add_commit(self, mock_modify, mock_add, mock_delete):
        self.datary.add_commit(
            wdir_uuid=self.json_repo.get('workdir').get('uuid'),
            last_commit=self.commit_test1,
            actual_commit=self.commit_test2,
            strict=True)

        self.assertEqual(mock_add.call_count, 1)
        self.assertEqual(mock_delete.call_count, 1)
        self.assertEqual(mock_modify.call_count, 1)

        mock_add.reset_mock()
        mock_modify.reset_mock()
        mock_delete.reset_mock()

        self.datary.add_commit(
            wdir_uuid=self.json_repo.get('workdir').get('uuid'),
            last_commit=self.commit_test1,
            actual_commit=self.commit_test2,
            strict=False)

        self.assertEqual(mock_add.call_count, 1)
        self.assertEqual(mock_delete.call_count, 0)
        self.assertEqual(mock_modify.call_count, 1)

    @mock.patch('datary.commits.commits.datetime')
    def test_commit_diff_tostring(self, mock_datetime):

        datetime_value = "12/03/1990-12:04"
        mock_datetime.now().strftime.return_value = datetime_value

        test_diff = {'add': [{'path': 'path1', 'filename': 'filename1'}, {
            'path': 'path2', 'filename': 'filename2'}]}
        test_diff_result = (
            'Changes at {}\nADD\n*****************\n+  path1/filename1\n+  '
            'path2/filename2\nDELETE\n*****************\nUPDATE\n***********'
            '******\n'.format(datetime_value))

        # Empty diff
        result = self.datary.commit_diff_tostring([])
        self.assertEqual(result, "")

        result2 = self.datary.commit_diff_tostring(test_diff)
        self.assertEqual(result2, test_diff_result)

        ex = Exception('test exception in datetime')
        mock_datetime.now().strftime.side_effect = ex
        result3 = self.datary.commit_diff_tostring(test_diff)
        self.assertEqual(result3, '')

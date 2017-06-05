# -*- coding: utf-8 -*-
import mock
import requests
import unittest
import collections

from unittest.mock import patch
from collections import OrderedDict
from datary import Datary, Datary_SizeLimitException
from datary.utils import nested_dict_to_list, flatten, get_dimension
from .mock_requests import MockRequestResponse


class DataryTestCase(unittest.TestCase):

    # default params to test Datary class
    test_username = 'pepe'
    test_password = 'pass'
    test_token = '123'

    params = {'username': test_username, 'password': test_password, 'token': test_token}
    datary = Datary(**params)

    url = 'http://datary.io/test'  # not exist, it's false
    repo_uuid = '1234-1234-21-asd-123'
    wdir_uuid = '4456-2123-55-as2-146'
    commit_sha1 = "3256-1125-23-ab3-246"
    dataset_uuid = "9132-3323-15-xs2-627"

    # old_ commit
    commit_test1 = [['a', 'aa', 'data_aa', 'aa_sha1'],
                    ['b', 'bb', 'data_bb', 'bb_sha1'],
                    ['d', 'dd', 'data_dd', 'dd_sha1']]

    # new_ commit
    commit_test2 = [['a', 'aa', 'data_aa', 'aa_sha1'],
                    ['c/a', 'caa', 'data_caa', 'caa_sha1'],
                    ['d', 'dd', 'data_dd', 'dd2_sha1']]

    element = {'path': 'a', 'filename': 'aa', 'data': {'kern': {'data_aa': []}, 'meta': {}}, 'sha1': 'aa_sha1'}

    original = {'__kern': {'data_aa': []}, '__meta': {}}

    inode = 'c46ac2d596ee898fd949c0bb0bb8f114482de450'

    json_repo = {
            "owner":   "b22x2h1h-23wf-1j56-253h-21c3u5st3851",
            "creator": "b22x2h1h-23wf-1j56-253h-21c3u5st3851",
            "name": "test_repo",
            "description": "test mocking repo",
            "workdir": {
              "uuid": "s2g5311h-2416-21h2-52u6-23asw22ha2134"
            },
            "apex": {'commit': '123'},
            "visibility": "public",
            "license": {
              "name": "cc-sa"
            },
            "category": "test",
            "status": "active",
            "uuid": "47eq5s12-5el1-2hq2-2ss1-egx517b1w967"
        }

    json_repo2 = {
            "owner":   "d1917c16-741c-11e6-8b77-86f30ca893d3",
            "creator": "d1917c16-741c-11e6-8b77-86f30ca893d3",
            "name": "test_repo2",
            "description": "test mocking repo 2",
            "workdir": {
              "uuid": "d191806c-741c-11e6-8b77-86f30ca893d3"
            },
            "apex": {},
            "visibility": "private",
            "license": {
              "name": "cc-test"
            },
            "category": "test",
            "status": "active",
            "uuid": "0dc6379e-741d-11e6-8b77-86f30ca893d3"
        }

    wdir_json = {
        "tree": "e2d2bcb88032930aacae64dc5d051ed0b03b6bde",
        "changes": {
            "removedElements": [],
            "renamedElements": [],
            "modifiedElements": [],
            "addedElements": []},
        "filetree": {
            "file_test1": "3a26a47b6e7f28c77380eccc8aec23sd6dc0201e",
            "folder_test1": {
                "file_test2": "3a26a47b6e7f28c77380eccc8aec23sd6dc0201e"
                }
            }
        }

    changes = {
        "removedElements": [
            {
                "dirname": "b",
                "basename": "bb",
                "inode": "inode1_changes"
            },
            {
                "dirname": "",
                "basename": "a",
                "inode": "inode2_changes"
            }],
        "renamedElements": [],
        "modifiedElements": [{
                "dirname": "b",
                "basename": "bb",
                "inode": "inode1_changes"
            }],
        "addedElements": [{
                "dirname": "",
                "basename": "d",
                "inode": "inode3_changes"
            }]
        }

    filetree = {
        '__self': '__self_sha1',
        'a': 'a_sha1',
        'b': {
            '__self': '__self_sha1',
            'bb': 'bb_sha1'},
        'c': 'c_sha1'
        }

    categories = [{
        "id": "business",
        "name": "Business",
        "href": "api.datary.io/search/categories/business",
        "icons": {"sm": None, "md": None, "lg": None},
        "locale": {"es-ES": "Negocios"}
        },
        {
        "id": "sports",
        "name": "Sports",
        "href": "api.datary.io/search/categories/sports",
        "icons": {"sm": None, "md": None, "lg": None},
        "locale": {"es-ES": "Deportes"}
        }]

    members = [
        {
            "uuid": "b71fb2a2-3b0a-452e-8479-d30f2b42f0a3",
            "username": "username1",
            "signedUpAt": "2016-04-05T19:55:45.315Z",
            "profile": {
                "displayName": "USERNAME 1",
                "avatar": {
                    "thumbnail": "test1.png",
                    "verbatim": "test1.png"
                }
            }
        },
        {
            "uuid": "b71fb2a2-3a0b-407e-9876-d7034b42f0a6",
            "username": "username2",
            "signedUpAt": "2017-02-05T19:55:45.315Z",
            "profile": {
                "displayName": "USERNAME 2",
                "avatar": {
                    "thumbnail": "test2.png",
                    "verbatim": "test2.png"
                }
            }
        },
    ]

    metadata = {"sha1": "sha1_value"}  # TODO: Update sha1 with similar one


##########################################################################
#                             Auth & Request
##########################################################################

    @mock.patch('datary.Datary.request')
    def test_get_user_token(self, mock_request):

        # Assert init class data & token introduced by args
        self.assertEqual(self.datary.username, self.test_username)
        self.assertEqual(self.datary.password, self.test_password)
        self.assertEqual(self.datary.token, self.test_token)
        self.assertEqual(mock_request.call_count, 0)

        # Assert get token in __init__
        mock_request.return_value = MockRequestResponse("", headers={'x-set-token': self.test_token})
        self.datary = Datary(**{'username': 'pepe', 'password': 'pass'})
        self.assertEqual(mock_request.call_count, 1)

        # Assert get token by the method without args.
        mock_request.return_value = MockRequestResponse("", headers={'x-set-token': self.test_token})
        token1 = self.datary.get_user_token()
        self.assertEqual(token1, self.test_token)

        # Assert get token by method     with args.
        mock_request.return_value = MockRequestResponse("", headers={'x-set-token': '456'})
        token2 = self.datary.get_user_token('maria', 'pass2')
        self.assertEqual(token2, '456')

        mock_request.return_value = MockRequestResponse("", headers={})
        token3 = self.datary.get_user_token('maria', 'pass2')
        self.assertEqual(token3, '')

        self.assertEqual(mock_request.call_count, 4)

    @mock.patch('datary.requests')
    def test_sign_out(self, mock_request):

        # Fail sign out
        mock_request.get.return_value = MockRequestResponse("Err", status_code=500)
        self.datary.sign_out()
        self.assertEqual(self.datary.token, self.test_token)
        self.assertEqual(mock_request.get.call_count, 1)

        # reset mock
        mock_request.get.reset_mock()

        # Succes sign out
        mock_request.get.return_value = MockRequestResponse("OK", status_code=200)
        self.assertEqual(self.datary.token, self.test_token)
        self.datary.sign_out()
        self.assertEqual(self.datary.token, None)
        self.assertEqual(mock_request.get.call_count, 1)

    @mock.patch('datary.requests')
    def test_request(self, mock_requests):

        mock_requests.get.return_value = MockRequestResponse("ok", headers={'x-set-token': self.test_token})
        mock_requests.post.return_value = MockRequestResponse("ok", headers={'x-set-token': self.test_token})
        mock_requests.delete.return_value = MockRequestResponse("ok", headers={'x-set-token': self.test_token})

        # test GET
        result1 = self.datary.request(self.url, 'GET')
        self.assertEqual(result1.text, 'ok')

        # test POST
        result2 = self.datary.request(self.url, 'POST')
        self.assertEqual(result2.text, 'ok')

        # test deleted
        result3 = self.datary.request(self.url, 'DELETE')
        self.assertEqual(result3.text, 'ok')

        # test UNKNOWK http method
        with self.assertRaises(Exception):
            self.datary.request(self.url, 'UNKWOWN')

        # test status code wrong
        mock_requests.get.return_value = MockRequestResponse("err", status_code=500)
        result4 = self.datary.request(self.url, 'GET')
        self.assertEqual(result4, None)

        mock_requests.get.side_effect = requests.RequestException('err')
        result5 = self.datary.request(self.url, 'GET')
        self.assertEqual(result5, None)

        self.assertEqual(mock_requests.get.call_count, 3)
        self.assertEqual(mock_requests.post.call_count, 1)
        self.assertEqual(mock_requests.delete.call_count, 1)


##########################################################################
#                             Repository Methods
##########################################################################

    @mock.patch('datary.Datary.request')
    @mock.patch('datary.Datary.get_describerepo')
    def test_create_repo(self, mock_describerepo, mock_request):
        mock_describerepo.return_value = MockRequestResponse("", json=self.json_repo)
        repo = self.datary.create_repo('repo_name', 'category_test', amount=1)
        repo2 = self.datary.create_repo('repo_nane', 'category_test', repo_uuid='123', amount=1)

        mock_request.side_effect = Exception('Amount not introduced')
        mock_describerepo.return_value = {}
        repo4 = self.datary.create_repo('repo_nane', 'category_test', repo_uuid='123')

        self.assertEqual(repo.json().get('uuid'), '47eq5s12-5el1-2hq2-2ss1-egx517b1w967')
        self.assertEqual(repo2.json().get('uuid'), '47eq5s12-5el1-2hq2-2ss1-egx517b1w967')
        self.assertEqual(mock_request.call_count, 1)
        self.assertEqual(mock_describerepo.call_count, 3)
        self.assertEqual(repo4, {})

    @mock.patch('datary.Datary.request')
    def test_describerepo(self, mock_request):

        # TODO: Review return of request and check test
        mock_request.return_value = MockRequestResponse("aaa", json=self.json_repo)
        repo = self.datary.get_describerepo(self.repo_uuid)
        self.assertEqual(mock_request.call_count, 1)
        assert isinstance(repo, dict)
        self.assertEqual(repo.get('name'), 'test_repo')

        mock_request.return_value = MockRequestResponse("", status_code=204, json=self.json_repo)
        repo2 = self.datary.get_describerepo(self.repo_uuid)
        assert isinstance(repo, dict)
        self.assertEqual(repo2.get('name'), 'test_repo')

        mock_request.return_value = MockRequestResponse("aaa", json=[self.json_repo, self.json_repo2])
        repo3 = self.datary.get_describerepo('0dc6379e-741d-11e6-8b77-86f30ca893d3')
        assert isinstance(repo, dict)
        self.assertEqual(repo3.get('name'), 'test_repo2')

        repo4 = self.datary.get_describerepo(repo_name='test_repo2')
        assert isinstance(repo, dict)
        self.assertEqual(repo4.get('name'), 'test_repo2')

        mock_request.return_value = MockRequestResponse("a", json=[])
        repo5 = self.datary.get_describerepo(repo_name='test_repo2')
        self.assertEqual(repo5, {})

        # check fail requests returns None
        mock_request.return_value = None
        repo6 = self.datary.get_describerepo(repo_name='test_repo2')
        self.assertEqual(repo6, {})

    @mock.patch('datary.Datary.request')
    def test_deleterepo(self, mock_request):

        mock_request.return_value = MockRequestResponse("Repo {} deleted".format('123'))
        result = self.datary.delete_repo(repo_uuid='123')
        self.assertEqual(result, 'Repo 123 deleted')

        with self.assertRaises(Exception):
            self.datary.delete_repo()


##########################################################################
#                             Filetree Methods
##########################################################################

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


##########################################################################
#                             Datasets Methods
##########################################################################

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
        original = self.datary.get_original(self.repo_uuid, self.dataset_uuid)
        self.assertEqual(mock_request.call_count, 1)
        assert(isinstance(original, dict))
        self.assertEqual(original, self.original)

        mock_request.return_value = None
        original2 = self.datary.get_original(self.repo_uuid, self.dataset_uuid)
        assert(isinstance(original2, dict))
        self.assertEqual(original2, {})

    @mock.patch('datary.Datary.get_wdir_filetree')
    @mock.patch('datary.Datary.get_wdir_changes')
    def test_get_dataset_uuid(self, mock_get_wdir_changes, mock_get_wdir_filetree):

        mock_get_wdir_filetree.return_value = self.filetree
        mock_get_wdir_changes.return_value = self.changes

        path = 'b'
        filename = 'bb'

        empty_result = self.datary.get_dataset_uuid(self.wdir_uuid)
        self.assertEqual(empty_result, None)

        from_changes_result = self.datary.get_dataset_uuid(self.wdir_uuid, path, filename)
        self.assertEqual(from_changes_result, 'inode1_changes')
        self.assertEqual(mock_get_wdir_filetree.call_count, 1)
        self.assertEqual(mock_get_wdir_changes.call_count, 1)

        mock_get_wdir_filetree.reset_mock()
        mock_get_wdir_changes.reset_mock()

        # retrive from filetree
        path = ''
        filename = 'c'

        from_commit_result = self.datary.get_dataset_uuid(self.wdir_uuid, path, filename)

        self.assertEqual(from_commit_result, 'c_sha1')
        self.assertEqual(mock_get_wdir_filetree.call_count, 1)
        self.assertEqual(mock_get_wdir_changes.call_count, 1)

        mock_get_wdir_filetree.reset_mock()
        mock_get_wdir_changes.reset_mock()

        # NOT exists
        path = 'bb'
        filename = 'b'

        no_result = self.datary.get_dataset_uuid(self.wdir_uuid, path, filename)
        self.assertEqual(no_result, None)
        self.assertEqual(mock_get_wdir_filetree.call_count, 1)
        self.assertEqual(mock_get_wdir_changes.call_count, 1)

    @mock.patch('datary.Datary.request')
    def test_get_commited_dataset_uuid(self, mock_request):

        # no args path and filename introduced
        mock_request.return_value = MockRequestResponse("", json=self.dataset_uuid)
        result_no_pathname = self.datary.get_commited_dataset_uuid(self.wdir_uuid)
        self.assertEqual(result_no_pathname, {})
        self.assertEqual(mock_request.call_count, 0)

        # good case
        result = self.datary.get_commited_dataset_uuid(self.wdir_uuid, 'path', 'filename')
        self.assertEqual(result, self.dataset_uuid)
        self.assertEqual(mock_request.call_count, 1)

        # datary request return None
        mock_request.reset_mock()
        mock_request.return_value = None

        no_response_result = self.datary.get_commited_dataset_uuid(self.wdir_uuid, 'path', 'filename')
        self.assertEqual(no_response_result, {})
        self.assertEqual(mock_request.call_count, 1)


##########################################################################
#                             Categories Methods
##########################################################################

    @mock.patch('datary.Datary.request')
    def test_get_categories(self, mock_request):
        mock_request.return_value = MockRequestResponse("", json=self.categories,)
        categories = self.datary.get_categories()
        self.assertEqual(mock_request.call_count, 1)
        self.assertEqual(len(categories), len(self.categories))
        self.assertEqual(categories, self.categories)

        mock_request.reset_mock()
        mock_request.return_value = None
        categories = self.datary.get_categories()
        self.assertEqual(mock_request.call_count, 1)
        self.assertEqual(len(categories), len(self.datary.DATARY_CATEGORIES))
        self.assertEqual(sorted(categories), sorted(self.datary.DATARY_CATEGORIES))


##########################################################################
#                            Commits method's
##########################################################################

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
    def test_recollect_last_commit(self, mock_metadata, mock_filetree, mock_get_describerepo):
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

        result = self.datary.compare_commits(self.commit_test1, self.commit_test2)

        self.assertEqual(len(result.get('add')), 1)
        self.assertEqual(len(result.get('update')), 1)
        self.assertEqual(len(result.get('delete')), 1)

        for k, v in expected.items():
            elements_sha1 = [element.get('sha1') for element in result.get(k)]
            for sha1 in v:
                sha1 in elements_sha1

        with patch('datary.Datary.make_index') as mock_makeindex:
            mock_makeindex.side_effect = Exception('Test Exception')
            result2 = self.datary.compare_commits(self.commit_test1, self.commit_test2)

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

    @mock.patch('datary.datetime')
    def test_commit_diff_tostring(self, mock_datetime):

        datetime_value = "12/03/1990-12:04"
        mock_datetime.now().strftime.return_value = datetime_value

        test_diff = {'add': [{'path': 'path1', 'filename': 'filename1'}, {'path': 'path2', 'filename': 'filename2'}]}
        test_diff_result = 'Changes at {}\nADD\n*****************\n+  path1/filename1\n+  path2/filename2\nDELETE\n*****************\nUPDATE\n*****************\n'.format(datetime_value)

        # Empty diff
        result = self.datary.commit_diff_tostring([])
        self.assertEqual(result, "")

        result2 = self.datary.commit_diff_tostring(test_diff)
        self.assertEqual(result2, test_diff_result)

        mock_datetime.now().strftime.side_effect = Exception('test exception in datetime')
        result3 = self.datary.commit_diff_tostring(test_diff)
        self.assertEqual(result3, '')


##########################################################################
#                              Add methods
##########################################################################

    @mock.patch('datary.Datary.request')
    def test_add_dir(self, mock_request):
        # TODO: Unkwnown api method changes?
        mock_request.return_value = MockRequestResponse("")
        self.datary.add_dir(self.json_repo.get('workdir', {}).get('uuid'), 'path', 'dirname')
        mock_request.return_value = None
        self.datary.add_dir(self.json_repo.get('workdir', {}).get('uuid'), 'path', 'dirname')
        self.assertEqual(mock_request.call_count, 2)

    @mock.patch('datary.Datary.request')
    def test_add_file(self, mock_request):
        # TODO: Unkwnown api method changes??
        mock_request.return_value = MockRequestResponse("")
        self.datary.add_file(self.json_repo.get('workdir', {}).get('uuid'), self.element)
        mock_request.return_value = None
        self.datary.add_file(self.json_repo.get('workdir', {}).get('uuid'), self.element)
        self.assertEqual(mock_request.call_count, 2)


##########################################################################
#                              Modify methods
##########################################################################

    @mock.patch('datary.Datary.request')
    def test_modify_request(self, mock_request):
        mock_request.return_value = MockRequestResponse("")
        self.datary.modify_request(self.json_repo.get('workdir', {}).get('uuid'), self.element)
        mock_request.return_value = None
        self.datary.modify_request(self.json_repo.get('workdir', {}).get('uuid'), self.element)
        self.assertEqual(mock_request.call_count, 2)

    @mock.patch('datary.Datary.override_file')
    @mock.patch('datary.Datary.update_append_file')
    def test_modify_file(self, mock_update_append, mock_override_file):

        mock_mod_style = mock.MagicMock()

        # override mode
        self.datary.modify_file(self.json_repo.get('workdir', {}).get('uuid'), self.element)
        self.datary.modify_file(self.json_repo.get('workdir', {}).get('uuid'), self.element, mod_style='override')
        self.assertEqual(mock_override_file.call_count, 2)

        # update-append mode
        self.datary.modify_file(self.json_repo.get('workdir', {}).get('uuid'), self.element, mod_style='update-append')
        self.assertEqual(mock_update_append.call_count, 1)

        # callable mode
        self.datary.modify_file(self.json_repo.get('workdir', {}).get('uuid'), self.element, mod_style=mock_mod_style)
        self.assertEqual(mock_mod_style.call_count, 1)

        # unexisting mode
        self.datary.modify_file(self.json_repo.get('workdir', {}).get('uuid'), self.element, mod_style="magic-mode")
        self.assertEqual(mock_override_file.call_count, 2)
        self.assertEqual(mock_update_append.call_count, 1)
        self.assertEqual(mock_mod_style.call_count, 1)

    @mock.patch('datary.Datary.modify_request')
    def test_override_file(self, mock_modify_requests):

        mock_modify_requests.return_value = MockRequestResponse("")
        self.datary.override_file(self.json_repo.get('workdir', {}).get('uuid'), self.element)
        self.assertEqual(mock_modify_requests.call_count, 1)

    @mock.patch('datary.Datary.modify_request')
    @mock.patch('datary.Datary.update_elements')
    @mock.patch('datary.Datary.get_original')
    @mock.patch('datary.Datary.get_dataset_uuid')
    def test_update_append_file(self, mock_get_dataset_uuid, mock_get_original, mock_update_elements, mock_modify_request):

        # all good.
        mock_get_dataset_uuid.return_value = self.dataset_uuid
        mock_get_original.return_value = self.original

        self.datary.update_append_file(
            wdir_uuid=self.json_repo.get('workdir', {}).get('uuid'),
            element=self.element,
            repo_uuid=self.repo_uuid)

        self.assertEqual(mock_get_dataset_uuid.call_count, 1)
        self.assertEqual(mock_get_original.call_count, 1)
        self.assertEqual(mock_update_elements.call_count, 1)
        self.assertEqual(mock_update_elements.call_count, 1)

        mock_get_dataset_uuid.reset_mock()
        mock_get_original.reset_mock()
        mock_update_elements.reset_mock()
        mock_update_elements.reset_mock()

        # Not retrieve orignal case..
        mock_get_original.return_value = None

        self.datary.update_append_file(
            wdir_uuid=self.json_repo.get('workdir', {}).get('uuid'),
            element=self.element,
            repo_uuid=self.repo_uuid)

        self.assertEqual(mock_get_dataset_uuid.call_count, 1)
        self.assertEqual(mock_get_original.call_count, 1)
        self.assertEqual(mock_update_elements.call_count, 0)
        self.assertEqual(mock_update_elements.call_count, 0)

    @mock.patch('datary.Datary._reload_meta')
    @mock.patch('datary.Datary._update_arrays_elements')
    @mock.patch('datary.Datary._calculate_rowzero_header_confindence')
    def test_update_elements(self, mock_calculate_rowzero_header_confindence, mock_update_arrays_elements, mock_reload_meta):
        # TODO: DO THIS TEST..
        pass

    @mock.patch('datary.utils.get_dimension')
    def test_reload_meta(self, mock_get_dimension):

        # false mock
        mock_get_dimension.side_effect = get_dimension

        # kern test data
        kern_with_header = [['H1', 'H2', 'H3'], [1, 2, 3], [4, 5, 6], [7, 8, 9]]
        kern_without_header = kern_with_header[1:]
        kern_dict_with_header = {'a': kern_with_header, 'b': kern_with_header[:-1]}
        kern_dict_without_header = {'a': kern_with_header[1:], 'b': kern_with_header[1:-1]}
        kern_array = ['a', 'b', 'c']
        meta_array_init = {'axisHeaders': {'': [], '*': []}, 'dimension': {"": [23, 21]}}

        # kern list with header
        meta_with_header = self.datary._reload_meta(kern_with_header, {}, path_key='', is_rowzero_header=True)
        assert(isinstance(meta_with_header, dict))
        self.assertEqual(meta_with_header.get('axisHeaders', {}).get('*'), ['H1', 'H2', 'H3'])
        self.assertEqual(meta_with_header.get('axisHeaders', {}).get(''), ['H1', 1, 4, 7])
        self.assertEqual(meta_with_header.get('dimension', {}).get(''), [4, 3])

        # kern list without header
        meta_without_header = self.datary._reload_meta(kern_without_header, {}, path_key='', is_rowzero_header=False)
        assert(isinstance(meta_without_header, dict))
        self.assertEqual(meta_without_header.get('axisHeaders', {}).get('*'), ['Header{}'.format(x) for x in range(1, len(kern_with_header[0]) + 1)])
        self.assertEqual(meta_without_header.get('axisHeaders', {}).get(''), [1, 4, 7])
        self.assertEqual(meta_without_header.get('dimension', {}).get(''), [3, 3])

        # kern dict with header
        meta_dict_with_header = self.datary._reload_meta(kern_dict_with_header, {}, path_key='a', is_rowzero_header=True)
        assert(isinstance(meta_dict_with_header, dict))
        self.assertEqual(meta_dict_with_header.get('axisHeaders', {}).get('a/*'), ['H1', 'H2', 'H3'])
        self.assertEqual(meta_dict_with_header.get('axisHeaders', {}).get('a'), ['H1', 1, 4, 7])
        self.assertEqual(meta_dict_with_header.get('dimension', {}).get('a'), [4, 3])

        # kern dict update meta with other meta
        meta_dict_with_header = self.datary._reload_meta(kern_dict_with_header, meta_dict_with_header, path_key='b', is_rowzero_header=True)
        assert(isinstance(meta_dict_with_header, dict))
        self.assertEqual(meta_dict_with_header.get('axisHeaders', {}).get('a/*'), ['H1', 'H2', 'H3'])
        self.assertEqual(meta_dict_with_header.get('axisHeaders', {}).get('a'), ['H1', 1, 4, 7])
        self.assertEqual(meta_dict_with_header.get('axisHeaders', {}).get('b/*'), ['H1', 'H2', 'H3'])
        self.assertEqual(meta_dict_with_header.get('axisHeaders', {}).get('b'), ['H1', 1, 4])
        self.assertEqual(meta_dict_with_header.get('dimension', {}).get('a'), [4, 3])
        self.assertEqual(meta_dict_with_header.get('dimension', {}).get('b'), [3, 3])

        # kern dict without header
        meta_dict_without_header = self.datary._reload_meta(kern_dict_without_header, {}, path_key='a', is_rowzero_header=False)
        assert(isinstance(meta_dict_without_header, dict))
        self.assertEqual(meta_dict_without_header.get('axisHeaders', {}).get('a/*'), ['Header{}'.format(x) for x in range(1, len(kern_dict_without_header.get('a')[0]) + 1)])
        self.assertEqual(meta_dict_without_header.get('axisHeaders', {}).get('a'), [1, 4, 7])
        self.assertEqual(meta_dict_without_header.get('dimension', {}).get('a'), [3, 3])

        # kern dict update meta without other meta
        meta_dict_without_header = self.datary._reload_meta(kern_dict_without_header, meta_dict_without_header, path_key='b', is_rowzero_header=False)
        assert(isinstance(meta_dict_without_header, dict))
        self.assertEqual(meta_dict_without_header.get('axisHeaders', {}).get('a/*'), ['Header{}'.format(x) for x in range(1, len(kern_dict_without_header.get('a')[0]) + 1)])
        self.assertEqual(meta_dict_without_header.get('axisHeaders', {}).get('a'), [1, 4, 7])
        self.assertEqual(meta_dict_without_header.get('axisHeaders', {}).get('b/*'), ['Header{}'.format(x) for x in range(1, len(kern_dict_without_header.get('b')[0]) + 1)])
        self.assertEqual(meta_dict_without_header.get('axisHeaders', {}).get('b'), [1, 4])
        self.assertEqual(meta_dict_without_header.get('dimension', {}).get('a'), [3, 3])
        self.assertEqual(meta_dict_without_header.get('dimension', {}).get('b'), [2, 3])

        # case array and override meta
        meta_array = self.datary._reload_meta(kern_array, meta_array_init, path_key='', is_rowzero_header=False)
        assert(isinstance(meta_array, dict))
        self.assertEqual(meta_array.get('axisHeaders', {}).get(''), ['a', 'b', 'c'])
        self.assertEqual(meta_array.get('axisHeaders', {}).get('*'), ['Header1'])
        self.assertEqual(meta_array.get('dimension', {}).get(''), [3, 1])

        # test capture exception
        mock_get_dimension.side_effect = Exception("Test exception")
        meta_array_after_ex = self.datary._reload_meta(kern_array, meta_array_init, path_key='', is_rowzero_header=False)
        self.assertEqual(meta_array_after_ex, meta_array_init)

    def test_calculate_rowzero_header_confindence(self):
        # TODO: DO THIS TEST..
        pass

    def test_merge_headers(self):

        header1 = ['H1', 'H2', 'H3']
        header2 = ['H4', 'H2', 'H1']

        result = self.datary._merge_headers(header1, header2)
        self.assertEqual(result, ['H1', 'H2', 'H3', 'H4'])

        result2 = self.datary._merge_headers(result, ['H5', 'pepe'])
        self.assertEqual(result2, ['H1', 'H2', 'H3', 'H4', 'H5', 'pepe'])

    def test_update_arrays_elements(self):
        # TODO: DO THIS TEST..
        # _update_arrays_elements(self, original_array, update_array, is_rowzero_header)
        pass

##########################################################################
#                              Delete methods
##########################################################################

    @mock.patch('datary.Datary.request')
    def test_delete_dir(self, mock_request):
        # TODO: Unkwnown api method changes??
        mock_request.return_value = MockRequestResponse("")
        self.datary.delete_dir(self.json_repo.get('workdir', {}).get('uuid'), "path", "dirname")
        mock_request.return_value = None
        self.datary.delete_dir(self.json_repo.get('workdir', {}).get('uuid'), "path", "dirname")
        self.assertEqual(mock_request.call_count, 2)

    @mock.patch('datary.Datary.request')
    def test_delete_file(self, mock_request):
        # TODO: Unkwnown api method changes??
        mock_request.return_value = MockRequestResponse("")
        self.datary.delete_file(self.json_repo.get('workdir', {}).get('uuid'), self.element)
        mock_request.return_value = None
        self.datary.delete_file(self.json_repo.get('workdir', {}).get('uuid'), self.element)
        self.assertEqual(mock_request.call_count, 2)

    @mock.patch('datary.Datary.request')
    def test_delete_inode(self, mock_request):
        mock_request.return_value = MockRequestResponse("")
        self.datary.delete_inode(self.json_repo.get('workdir', {}).get('uuid'), self.inode)
        mock_request.return_value = None
        self.datary.delete_inode(self.json_repo.get('workdir', {}).get('uuid'), self.inode)
        self.assertEqual(mock_request.call_count, 2)

        with self.assertRaises(Exception):
            self.datary.delete_inode(self.json_repo.get('workdir', {}).get('uuid'))

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
    def test_clean_repo(self, mock_get_describerepo, mock_clear_index, mock_commit,
                        mock_get_wdir_filetree, mock_add_file, mock_delete_file):

        mock_get_describerepo.return_value = self.json_repo
        mock_get_wdir_filetree.return_value = self.filetree

        self.datary.clean_repo(self.repo_uuid)

        mock_get_describerepo.return_value = None
        self.datary.clean_repo(self.repo_uuid)


##########################################################################
#                              Members methods
##########################################################################

    @mock.patch('datary.Datary.request')
    def test_get_members(self, mock_request):

        mock_request.return_value = MockRequestResponse("aaa", json=self.members)
        member = self.datary.get_members(member_name='username1')
        self.assertEqual(member, self.members[0])

        member2 = self.datary.get_members(member_uuid=self.members[1].get('uuid'))
        self.assertEqual(member2, self.members[1])

        members_fail = self.datary.get_members(member_name='username3')
        self.assertEqual(members_fail, {})

        members_limit = self.datary.get_members()
        assert isinstance(members_limit, list)


class MockRequestsTestCase(unittest.TestCase):

    def test(self):
        test = MockRequestResponse('aaaa', path='test_path')
        self.assertEqual(test.text, 'aaaa')
        self.assertEqual(test.path(), 'test_path')
        self.assertEqual(test.encoding(), 'utf-8')

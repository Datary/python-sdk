# -*- coding: utf-8 -*-
import mock
import requests
import unittest
import collections

from unittest.mock import patch
from collections import OrderedDict
from datary import Datary, Datary_SizeLimitException, nested_dict_to_list, flatten
from .mock_requests import MockRequestResponse


class DataryTestCase(unittest.TestCase):

    # default params to test Datary class
    params = {'username': 'pepe', 'password': 'pass', 'token': '123'}
    datary = Datary(**params)

    url = 'http://datary.io/test'  # not exist, it's false+
    repo_uuid = '1234-1234-21-asd-123'
    wdir_uuid = '4456-2123-55-as2-146'
    commit_sha1 = ""  # TODO: view commit sha1 format
    datary_file_sha1 = ""  # TODO: View datary_file_sha1

    # old_ commit
    commit_test1 = [['a', 'aa', 'data_aa', 'aa_sha1'],
                    ['b', 'bb', 'data_bb', 'bb_sha1'],
                    ['d', 'dd', 'data_dd', 'dd_sha1']]

    # new_ commit
    commit_test2 = [['a', 'aa', 'data_aa', 'aa_sha1'],
                    ['c/a', 'caa', 'data_caa', 'caa_sha1'],
                    ['d', 'dd', 'data_dd', 'dd2_sha1']]

    element = {'path': 'a', 'filename': 'aa', 'data': {'kern': {'data_aa': []}, 'meta': {}}, 'sha1': 'aa_sha1'}

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

    metadata = {"sha1": "sha1_value"}  # TODO: Update sha1 with similar one

    @mock.patch('datary.Datary.request')
    def test_get_user_token(self, mock_request):

        # Assert init class data & token introduced by args
        self.assertEqual(self.datary.username, 'pepe')
        self.assertEqual(self.datary.password, 'pass')
        self.assertEqual(self.datary.token, '123')
        self.assertEqual(mock_request.call_count, 0)

        # Assert get token in __init__
        mock_request.return_value = MockRequestResponse("", headers={'x-set-token': '123'})
        self.datary = Datary(**{'username': 'pepe', 'password': 'pass'})
        self.assertEqual(mock_request.call_count, 1)

        # Assert get token by the method without args.
        mock_request.return_value = MockRequestResponse("", headers={'x-set-token': '123'})
        token1 = self.datary.get_user_token()
        self.assertEqual(token1, '123')

        # Assert get token by method     with args.
        mock_request.return_value = MockRequestResponse("", headers={'x-set-token': '456'})
        token2 = self.datary.get_user_token('maria', 'pass2')
        self.assertEqual(token2, '456')

        mock_request.return_value = MockRequestResponse("", headers={})
        token3 = self.datary.get_user_token('maria', 'pass2')
        self.assertEqual(token3, '')

        self.assertEqual(mock_request.call_count, 4)

    @mock.patch('datary.requests')
    def test_request(self, mock_requests):

        mock_requests.get.return_value = MockRequestResponse("ok", headers={'x-set-token': '123'})
        mock_requests.post.return_value = MockRequestResponse("ok", headers={'x-set-token': '123'})
        mock_requests.delete.return_value = MockRequestResponse("ok", headers={'x-set-token': '123'})

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
        self.assertEqual(repo2.get('name'), None)

        mock_request.return_value = MockRequestResponse("aaa", json=[self.json_repo, self.json_repo2])
        repo3 = self.datary.get_describerepo('0dc6379e-741d-11e6-8b77-86f30ca893d3')
        assert isinstance(repo, dict)
        self.assertEqual(repo3.get('name'), 'test_repo2')

        repo4 = self.datary.get_describerepo(repo_name='test_repo2')
        assert isinstance(repo, dict)
        self.assertEqual(repo4.get('name'), 'test_repo2')

        mock_request.return_value = MockRequestResponse("a", json=[])
        repo5 = self.datary.get_describerepo(repo_name='test_repo2')
        self.assertEqual(repo5, None)

    @mock.patch('datary.Datary.request')
    def test_deleterepo(self, mock_request):

        mock_request.return_value = MockRequestResponse("Repo {} deleted".format('123'))
        result = self.datary.delete_repo(repo_uuid='123')
        self.assertEqual(result, 'Repo 123 deleted')

        with self.assertRaises(Exception):
            self.datary.delete_repo()

    @mock.patch('datary.Datary.request')
    def test_get_commit_filetree(self, mock_request):
        mock_request.return_value = MockRequestResponse("", json=self.wdir_json.get('filetree'))
        filetree = self.datary.get_commit_filetree(self.repo_uuid, self.commit_sha1)
        self.assertEqual(mock_request.call_count, 1)
        assert(isinstance(filetree, dict))

    @mock.patch('datary.Datary.request')
    def test_get_wdir_filetree(self, mock_request):
        mock_request.return_value = MockRequestResponse("", json=self.wdir_json.get('filetree'))
        filetree = self.datary.get_wdir_filetree(self.repo_uuid)
        self.assertEqual(mock_request.call_count, 1)
        assert(isinstance(filetree, dict))

    @mock.patch('datary.Datary.request')
    def test_get_metadata(self, mock_request):
        mock_request.return_value = MockRequestResponse("", json=self.metadata)
        metadata = self.datary.get_metadata(self.repo_uuid, self.datary_file_sha1)
        self.assertEqual(mock_request.call_count, 1)
        assert(isinstance(metadata, dict))
        self.assertEqual(metadata, self.metadata)

        mock_request.return_value = None
        metadata2 = self.datary.get_metadata(self.repo_uuid, self.datary_file_sha1)
        assert(isinstance(metadata2, dict))
        self.assertEqual(metadata2, {})

    @mock.patch('datary.Datary.request')
    def test_get_original(self, mock_request):

        mock_request.return_value = MockRequestResponse("", json=self.element.get('data', {}))
        original = self.datary.get_original(self.repo_uuid, self.datary_file_sha1)
        self.assertEqual(mock_request.call_count, 1)
        assert(isinstance(original, dict))
        self.assertEqual(original, self.element.get('data', {}))

        mock_request.return_value = None
        original2 = self.datary.get_original(self.repo_uuid, self.datary_file_sha1)
        assert(isinstance(original2, dict))
        self.assertEqual(original2, {})

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

    @mock.patch('datary.Datary.request')
    def test_modify_file(self, mock_request):
        # TODO: Unkwnown api method changes??
        mock_request.return_value = MockRequestResponse("")
        self.datary.modify_file(self.json_repo.get('workdir', {}).get('uuid'), self.element)
        mock_request.return_value = None
        self.datary.modify_file(self.json_repo.get('workdir', {}).get('uuid'), self.element)
        self.assertEqual(mock_request.call_count, 2)

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

    def test_Datary_SizeLimitException(self):
        a = Datary_SizeLimitException('test_msg', 'test_src_path', size=4)

        self.assertEqual(a.msg, 'test_msg')
        self.assertEqual(a.src_path, 'test_src_path')
        self.assertEqual(a.size, 4)
        self.assertEqual(str(a), 'test_msg;test_src_path;4')

    def test_nested_dict_to_list(self):
        expected = [['', 'b', 'bv2'], ['', 'a', 'av1'], ['c', 'cc', 'ccv1'],
                    ['c', 'ca', 'cav1'], ['c', 'cb', 'cbv1'], ['ccca', 'ccaa', 'ccaav1']]

        test = OrderedDict([
            ('b', 'bv2'),
            ('a', 'av1'),
            ('c', OrderedDict([
                ('cc', 'ccv1'),
                ('ca', 'cav1'),
                ('cb', 'cbv1'),
                ('cca', OrderedDict([
                    ('ccaa', 'ccaav1')])),
            ]))])

        result = nested_dict_to_list("", test)
        for r in result:
            assert r in expected

    def test_flatten(self):
        test = OrderedDict(
            {'a': 2, 'b': 2, 'c': {'ca': 3, 'cb': MockRequestResponse(''), 'cd': [1, 3, 4], 'cc': {'cca': 1}}})
        test_result_1 = collections.OrderedDict([
           ('a', 2), ('b', 2), ('c/ca', 3), ('c/cb', test.get('c', {}).get('cb')), ('c/cc/cca', 1), ('c/cd/1', 3),
           ('c/cd/0', 1), ('c/cd/2', 4)])

        test_result_2 = collections.OrderedDict([
            ('test_a', 2), ('test_c_ca', 3), ('test_c_cd_1', 3), ('test_c_cd_2', 4), ('test_c_cd_0', 1),
            ('test_c_cb', test.get('c', {}).get('cb')), ('test_c_cc_cca', 1), ('test_b', 2)])

        result = flatten(test, '', sep='/')
        result2 = flatten(test, 'test')

        for retrieved_result, test_result in [(result, test_result_1), (result2, test_result_2)]:
            for k, v in test_result.items():
                assert k in retrieved_result
                self.assertEqual(retrieved_result[k], v)


class MockRequestsTestCase(unittest.TestCase):

    def test(self):
        test = MockRequestResponse('aaaa', path='test_path')
        self.assertEqual(test.text, 'aaaa')
        self.assertEqual(test.path(), 'test_path')
        self.assertEqual(test.encoding(), 'utf-8')

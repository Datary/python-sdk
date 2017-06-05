# -*- coding: utf-8 -*-
import mock

from datary.test.test_datary import DataryTestCase
from datary.test.mock_requests import MockRequestResponse


class DataryReposTestCase(DataryTestCase):

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

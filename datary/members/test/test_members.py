# -*- coding: utf-8 -*-
import mock

from datary.test.test_datary import DataryTestCase
from datary.test.mock_requests import MockRequestResponse


class DataryMembersTestCase(DataryTestCase):

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
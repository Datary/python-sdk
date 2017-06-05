
# -*- coding: utf-8 -*-
import structlog

from urllib.parse import urljoin
from datary.requests import DataryRequests

logger = structlog.getLogger(__name__)


class DataryMembers(DataryRequests):

    def get_members(self, member_uuid='', member_name='', **kwargs):
        """
        ==============  =============   ====================================
        Parameter       Type            Description
        ==============  =============   ====================================
        member_uuid     str             member_uuid uuid
        member_name     str             member_name
        limit           int             number of results limit (default=20)
        ==============  =============   ====================================

        Returns:
            (list or dict) repository with the given member_uuid or member_name.
        """

        logger.info("Getting Datary members")

        url = urljoin(
            DataryRequests.URL_BASE,
            "search/members")

        response = self.request(url, 'GET', **{'headers': self.headers, 'params': {'limit': kwargs.get('limit', 20)}})

        members_data = response.json() if response else {}
        member = {}

        if member_name or member_uuid:
            for member_data in members_data:
                if member_uuid and member_data.get('uuid') == member_uuid:
                    member = member_data
                    break

                elif member_name and member_data.get('username') == member_name:
                    member = member_data
                    logger.info(member)
                    break
        else:
            member = members_data

        return member

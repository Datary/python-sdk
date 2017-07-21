# -*- coding: utf-8 -*-
"""
Datary sdk Datasets File
"""
import os

from urllib.parse import urljoin
from datary.auth import DataryAuth
from datary.filetrees import DataryFiletrees
from datary.utils import exclude_empty_values, get_element

import structlog

logger = structlog.getLogger(__name__)


class DataryDatasets(DataryAuth):
    """
    Datary Datasets module
    """

    headers = {}

    @classmethod
    def get_kern(cls, dataset_uuid, repo_uuid='', wdir_uuid='', scope=''):
        """
        ================  =============   ====================================
        Parameter         Type            Description
        ================  =============   ====================================
        repo_uuid         int             repository id
        dataset_uuid      str
        ================  =============   ====================================

        Returns:
            (dict) dataset kern

        """
        return cls.get_original(
            dataset_uuid, repo_uuid, wdir_uuid, 'kern', scope)

    @classmethod
    def get_metadata(cls, dataset_uuid, repo_uuid='', wdir_uuid='', scope=''):
        """
        ================  =============   ====================================
        Parameter         Type            Description
        ================  =============   ====================================
        repo_uuid         int             repository id
        dataset_uuid      str
        ================  =============   ====================================

        Returns:
            (dict) dataset metadata

        """
        return cls.get_original(
            dataset_uuid, repo_uuid, wdir_uuid, 'meta', scope)

    @classmethod
    def get_original(cls, dataset_uuid, repo_uuid='', wdir_uuid='',
                     section_edge='', scope=''):
        """
        ================  =============   ====================================
        Parameter         Type            Description
        ================  =============   ====================================
        dataset_uuid      str             dataset uuid
        repo_uuid         str             repository uuid
        wdir_uuid         str             workingdir uuid
        ================  =============   ====================================

        Returns:
            (dict) dataset original data
        """
        response = None

        if (repo_uuid or wdir_uuid) and dataset_uuid:
            url = urljoin(
                cls.URL_BASE,
                "datasets/{}/{}".format(dataset_uuid, section_edge))

            # look in changes or namespace only if not wdir_uuid
            if scope != 'repo':
                params = exclude_empty_values(
                    {'namespace': repo_uuid, 'scope': wdir_uuid})
                response = cls.request(
                    url, 'GET', **{'headers': cls.headers, 'params': params})

            if not response or not response.json():
                logger.error(
                    "Not original retrieved from wdir scope",
                    namespace=repo_uuid,
                    scope=wdir_uuid,
                    dataset_uuid=dataset_uuid)

                params = exclude_empty_values(
                    {'namespace': repo_uuid, 'scope': repo_uuid})
                response = cls.request(
                    url, 'GET', **{'headers': cls.headers, 'params': params})
                if not response:
                    logger.error(
                        "Not original retrieved from repo scope",
                        namespace=repo_uuid,
                        scope=repo_uuid,
                        dataset_uuid=dataset_uuid)

        return response.json() if response else {}

    @classmethod
    def get_dataset_uuid(cls, wdir_uuid, path='', filename=''):
        """
        ================  =============   ====================================
        Parameter         Type            Description
        ================  =============   ====================================
        wdir_uuid         str             workdir uuid
        path              str             path of dataset
        filename          str             filename of dataset
        ================  =============   ====================================

        Returns:
            (str) uuid of dataset in path introduced in args.
        """
        dataset_uuid = None
        filepath = os.path.join(path, filename)

        if filepath:

            # retrieve wdir filetree
            wdir_filetree = DataryFiletrees.get_wdir_filetree(wdir_uuid)

            # retrieve last commit filetree
            wdir_changes_filetree = DataryFiletrees.format_wdir_changes(
                DataryFiletrees.get_wdir_changes(wdir_uuid).values())

            # retrieve dataset uuid
            dataset_uuid = (get_element(wdir_changes_filetree, filepath)) or (
                get_element(wdir_filetree, filepath)) or None

        return dataset_uuid

    def get_commited_dataset_uuid(self, wdir_uuid, path='', filename=''):
        """
        ================  =============   ====================================
        Parameter         Type            Description
        ================  =============   ====================================
        wdir_uuid         str             wdir uuid.
        path              str             path of the file in Datary.
        filename          str             filename of the file in Datary.
        ================  =============   ====================================

        Returns:
            (string) uuid dataset/s of pathname introduced.
        """
        response = {}
        pathname = os.path.join(path, filename)

        if pathname:
            url = urljoin(self.URL_BASE,
                          "/workdirs/{}/filetree".format(wdir_uuid))
            params = exclude_empty_values({'pathname': pathname})
            response = self.request(
                url, 'GET', **{'headers': self.headers, 'params': params})
            if not response:
                logger.error(
                    "Not response retrieved.")

        return response.json() if response else {}

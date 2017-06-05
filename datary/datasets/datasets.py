# -*- coding: utf-8 -*-
import os
import structlog

from urllib.parse import urljoin
from datary.requests import DataryRequests
from datary.utils import exclude_empty_values, get_element
logger = structlog.getLogger(__name__)


class DataryDatasets(DataryRequests):
    def get_metadata(self, repo_uuid, dataset_uuid):
        """
        ================  =============   ====================================
        Parameter         Type            Description
        ================  =============   ====================================
        repo_uuid         int             repository id
        dataset_uuid  str
        ================  =============   ====================================

        Returns:
            (dict) dataset metadata

        """

        url = urljoin(
            DataryRequests.URL_BASE,
            "datasets/{}/metadata".format(dataset_uuid))

        params = {'namespace': repo_uuid}

        response = self.request(
            url, 'GET', **{'headers': self.headers, 'params': params})
        if not response:
            logger.error(
                "Not metadata retrieved.",
                repo_uuid=repo_uuid,
                dataset_uuid=dataset_uuid)

        return response.json() if response else {}

    def get_original(self, dataset_uuid, repo_uuid='', wdir_uuid=''):
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

            # look in changes or namespace only if not wdir_uuid
            url = urljoin(DataryRequests.URL_BASE, "datasets/{}/original".format(dataset_uuid))
            params = exclude_empty_values({'namespace': repo_uuid, 'scope': wdir_uuid})
            response = self.request(url, 'GET', **{'headers': self.headers, 'params': params})
            if not response or not response.json():
                logger.error(
                    "Not original retrieved from wdir scope",
                    namespace=repo_uuid,
                    scope=wdir_uuid,
                    dataset_uuid=dataset_uuid)

                params = exclude_empty_values({'namespace': repo_uuid, 'scope': repo_uuid})
                response = self.request(url, 'GET', **{'headers': self.headers, 'params': params})
                if not response:
                    logger.error(
                        "Not original retrieved from repo scope",
                        namespace=repo_uuid,
                        scope=repo_uuid,
                        dataset_uuid=dataset_uuid)

        return response.json() if response else {}

    def get_dataset_uuid(self, wdir_uuid, path='', filename=''):
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
            wdir_filetree = self.get_wdir_filetree(wdir_uuid)

            # retrieve last commit filetree
            wdir_changes_filetree = self.format_wdir_changes_to_filetreeformat(self.get_wdir_changes(wdir_uuid).values())

            # retrieve dataset uuid
            dataset_uuid = get_element(wdir_changes_filetree, filepath) or get_element(wdir_filetree, filepath) or None

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
            url = urljoin(DataryRequests.URL_BASE, "/workdirs/{}/filetree".format(wdir_uuid))
            params = exclude_empty_values({'pathname': pathname})
            response = self.request(url, 'GET', **{'headers': self.headers, 'params': params})
            if not response:
                logger.error(
                    "Not response retrieved.")

        return response.json() if response else {}
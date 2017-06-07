# -*- coding: utf-8 -*-
"""
Datary sdk Remove Operations File
"""
import os

from urllib.parse import urljoin
from datary.requests import DataryRequests
from datary.utils import flatten

import structlog

logger = structlog.getLogger(__name__)


class DataryRemoveOperation(DataryRequests):
    """
    Datary RemoveOperation module class
    """

    def delete_dir(self, wdir_uuid, path, dirname):
        """
        Delete directory.
        -- NOT IN USE --

        ================  =============   ====================================
        Parameter         Type            Description
        ================  =============   ====================================
        wdir_uuid         str             working directory uuid
        path              str             path to directory
        dirname           str             directory name
        ================  =============   ====================================

        """
        logger.info(
            "Delete directory in workdir.",
            wdir_uuid=wdir_uuid,
            dirname=dirname,
            path=os.path.join(path, dirname))

        url = urljoin(DataryRequests.URL_BASE,
                      "workdirs/{}/changes".format(wdir_uuid))

        payload = {"action": "delete",
                   "filemode": 40000,
                   "dirname": path,
                   "basename": dirname}

        response = self.request(
            url, 'GET', **{'data': payload, 'headers': self.headers})

        if response:
            logger.info(
                "Directory has been deleted in workdir",
                wdir_uuid=wdir_uuid,
                url=url,
                payload=payload)

    def delete_file(self, wdir_uuid, element):
        """
        Delete file.

        ================  =============   ====================================
        Parameter         Type            Description
        ================  =============   ====================================
        wdir_uuid         str             working directory uuid
        element           Dic             element with path & filename
        ================  =============   ====================================

        """
        logger.info(
            "Delete file in workdir.",
            element=element,
            wdir_uuid=wdir_uuid)

        url = urljoin(DataryRequests.URL_BASE,
                      "workdirs/{}/changes".format(wdir_uuid))

        payload = {
            "action": "remove",
            "filemode": 100644,
            "dirname": element.get('path'),
            "basename": element.get('filename')
        }

        response = self.request(
            url, 'POST', **{'data': payload, 'headers': self.headers})
        if response:
            logger.info("File has been deleted.")

    def delete_inode(self, wdir_uuid, inode):
        """
        Delete using inode.

        ================  =============   ====================================
        Parameter         Type            Description
        ================  =============   ====================================
        wdir_uuid         str             working directory uuid
        inode             str             directory or file inode.
        ================  =============   ====================================
        """
        logger.info("Delete by inode.", wdir_uuid=wdir_uuid, inode=inode)

        url = urljoin(DataryRequests.URL_BASE,
                      "workdirs/{}/changes".format(wdir_uuid))
        payload = {"action": "remove", "inode": inode}

        response = self.request(
            url, 'POST', **{'data': payload, 'headers': self.headers})

        if response:
            logger.info("Element has been deleted using inode.")

    def clear_index(self, wdir_uuid):
        """
        Clear changes in repo.

        ================  =============   ====================================
        Parameter         Type            Description
        ================  =============   ====================================
        wdir_uuid         str             working directory uuid
        ================  =============   ====================================
        """

        url = urljoin(DataryRequests.URL_BASE,
                      "workdirs/{}/changes".format(wdir_uuid))

        response = self.request(url, 'DELETE', **{'headers': self.headers})
        if response:
            logger.info("Repo index has been cleared.")
            return True

        return False

    def clean_repo(self, repo_uuid, **kwargs):
        """
        Clean repo data from datary & algolia.

        ================  =============   ====================================
        Parameter         Type            Description
        ================  =============   ====================================
        repo_uuid         str             repository uuid
        ================  =============   ====================================
        """
        repo = self.get_describerepo(repo_uuid=repo_uuid, **kwargs)

        if repo:
            wdir_uuid = repo.get('workdir', {}).get('uuid')

            # clear changes
            self.clear_index(wdir_uuid)

            # get filetree
            filetree = self.get_wdir_filetree(wdir_uuid)

            # flatten filetree to list
            flatten_filetree = flatten(filetree, sep='/')

            filetree_keys = [
                x for x in flatten_filetree.keys() if '__self' not in x]

            # Delete files
            for path in filetree_keys:
                element_data = {
                    'path': "/".join(path.split('/')[:-1]),
                    'filename': path.split('/')[-1]
                }

                self.delete_file(wdir_uuid, element_data)

            # commit clean repo
            self.commit(repo_uuid, 'Commit delete all files to clean repo')

        else:
            logger.error('Fail to clean_repo, repo not found in datary.')

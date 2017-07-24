# -*- coding: utf-8 -*-
"""
Datary sdk Remove Operations File
"""
import os

from urllib.parse import urljoin
from datary.auth import DataryAuth

import structlog

logger = structlog.getLogger(__name__)


class DataryRemoveOperation(DataryAuth):
    """
    Datary RemoveOperation module class
    """

    @classmethod
    def delete_dir(cls, wdir_uuid, path, dirname):
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

        url = urljoin(cls.URL_BASE,
                      "workdirs/{}/changes".format(wdir_uuid))

        payload = {"action": "delete",
                   "filemode": 40000,
                   "dirname": path,
                   "basename": dirname}

        response = cls.request(
            url, 'GET', **{'data': payload, 'headers': cls.headers})

        if response:
            logger.info(
                "Directory has been deleted in workdir",
                wdir_uuid=wdir_uuid,
                url=url,
                payload=payload)

    @classmethod
    def delete_file(cls, wdir_uuid, element):
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

        url = urljoin(cls.URL_BASE,
                      "workdirs/{}/changes".format(wdir_uuid))

        payload = {
            "action": "remove",
            "filemode": 100644,
            "dirname": element.get('path'),
            "basename": element.get('filename')
        }

        response = cls.request(
            url, 'POST', **{'data': payload, 'headers': cls.headers})
        if response:
            logger.info("File has been deleted.")

    @classmethod
    def delete_inode(cls, wdir_uuid, inode):
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

        url = urljoin(cls.URL_BASE,
                      "workdirs/{}/changes".format(wdir_uuid))

        payload = {"action": "remove", "inode": inode}

        response = cls.request(
            url, 'POST', **{'data': payload, 'headers': cls.headers})

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

        url = urljoin(self.URL_BASE,
                      "workdirs/{}/changes".format(wdir_uuid))

        response = self.request(url, 'DELETE', **{'headers': self.headers})
        if response:
            logger.info("Repo index has been cleared.")
            return True

        return False

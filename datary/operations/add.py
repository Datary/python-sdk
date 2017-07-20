# -*- coding: utf-8 -*-
"""
Datary sdk Add Operations File
"""
import os
import json
from urllib.parse import urljoin
from datary.requests import DataryRequests
import structlog

logger = structlog.getLogger(__name__)


class DataryAddOperation(DataryRequests):
    """
    Datary AddOperation module class
    """

    def add_dir(self, wdir_uuid, path, dirname):
        """
        (DEPRECATED)
        Creates a new directory.

        ================  =============   ====================================
        Parameter         Type            Description
        ================  =============   ====================================
        wdir_uuid         str             working directory uuid
        path              str             path to the new directory
        dirname           str             name of the new directory
        ================  =============   ====================================

        """
        logger.info(
            "Add new directory to Datary.",
            path=os.path.join(path, dirname))

        url = urljoin(DataryRequests.URL_BASE,
                      "workdirs/{}/changes".format(wdir_uuid))

        payload = {"action": "add",
                   "filemode": 40000,
                   "dirname": path,
                   "basename": dirname}

        response = self.request(
            url, 'POST', **{'data': payload, 'headers': self.headers})
        if response:
            logger.info(
                "Directory has been created in workdir.",
                url=url,
                wdir_uuid=wdir_uuid,
                dirname=dirname)

    def add_file(self, wdir_uuid, element):
        """
        Adds a new file.
        If the file is to be created within a new path
        it also creates all necesary directories.

        ================  =============   ====================================
        Parameter         Type            Description
        ================  =============   ====================================
        wdir_uuid         str             working directory uuid
        element           list            [path, filename, data, sha1]
        dirname           str             directory name
        ================  =============   ====================================

         """
        logger.info("Add new file to Datary.")

        url = urljoin(DataryRequests.URL_BASE,
                      "workdirs/{}/changes".format(wdir_uuid))

        payload = {
            "action": "add",
            "filemode": 100644,
            "dirname": element.get('path'),
            "basename": element.get('filename'),
            "kern": json.dumps(element.get('data', {}).get('kern')),
            "meta": json.dumps(element.get('data', {}).get('meta'))}

        response = self.request(
            url, 'POST', **{'data': payload, 'headers': self.headers})
        if response:
            logger.info(
                "File has been Added to workdir.",
                wdir_uuid=wdir_uuid,
                element=element)

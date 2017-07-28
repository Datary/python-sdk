
# -*- coding: utf-8 -*-
"""
Datary sdk clean Operations File
"""

from datary.auth import DataryAuth
from datary.repos import DataryRepos
from datary.filetrees import DataryFiletrees
from datary.operations.remove import DataryRemoveOperation
from datary.utils import flatten

import structlog

logger = structlog.getLogger(__name__)


class DataryCleanOperation(DataryAuth):
    """
    Datary clean operation class
    """
    @classmethod
    def clean_repo(cls, repo_uuid, **kwargs):
        """
        Clean repo data from datary & algolia.

        ================  =============   ====================================
        Parameter         Type            Description
        ================  =============   ====================================
        repo_uuid         str             repository uuid
        ================  =============   ====================================
        """
        repo = DataryRepos.get_describerepo(repo_uuid=repo_uuid, **kwargs)

        if repo:
            wdir_uuid = repo.get('workdir', {}).get('uuid')

            # clear changes
            DataryRemoveOperation().clear_index(wdir_uuid)

            # get filetree
            filetree = DataryFiletrees.get_wdir_filetree(wdir_uuid)

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

                DataryRemoveOperation.delete_file(wdir_uuid, element_data)

        else:
            logger.error('Fail to clean_repo, repo not found in datary.')

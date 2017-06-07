# -*- coding: utf-8 -*-
"""
Main datary sdk module
"""
import structlog

from .auth import DataryAuth
from .categories import DataryCategories
from .commits import DataryCommits
from .datasets import DataryDatasets
from .filetrees import DataryFiletrees
from .members import DataryMembers
from .repos import DataryRepos
from .operations import (
    DataryAddOperation,
    DataryModifyOperation,
    DataryRemoveOperation)

from . import version

logger = structlog.getLogger(__name__)
URL_BASE = "http://api.datary.io/"


class Datary(DataryAuth, DataryCategories, DataryCommits, DataryDatasets,
             DataryFiletrees, DataryMembers, DataryAddOperation, DataryRepos,
             DataryModifyOperation, DataryRemoveOperation):
    """
    Datary main api class.
    Inherits from the rest of Datary modules its api functionality :
        - DataryAuth
        - DataryCategories
        - DataryCommits
        - DataryDatasets
        - DataryFiletrees
        - DataryMembers
        - DataryAddOperation
        - DataryRepos
        - DataryModifyOperation
        - DataryRemoveOperation
    """

    __version__ = version.__version__

    # Datary Entity Meta Field Allowed
    ALLOWED_DATARY_META_FIELDS = [
        "axisHeaders",
        "caption",
        "citation",
        "description",
        "dimension",
        "downloadUrl",
        "includesAxisHeaders",
        "lastUpdateAt",
        "period",
        "propOrder",
        "rootAleas",
        "size",
        "sha1",
        "sourceUrl",
        "summary",
        "title",
        "traverseOnly",
        "bigdata",
        "dimension"]

    def __init__(self, **kwargs):
        """
        Init Datary class
        """
        super(Datary, self).__init__(**kwargs)

        # self.username = kwargs.get('username')
        # self.password = kwargs.get('password')
        # self.token = kwargs.get('token')
        # self.commit_limit = int(kwargs.get('commit_limit', 30))

        # If a token is not in the params, we retrieve it with the username and
        # password
        if not self.token and self.username and self.password:
            self.token = self.get_user_token(self.username, self.password)

        self.headers = kwargs.get('headers', {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "Bearer {}".format(self.token)
        })


class DatarySizeLimitException(Exception):
    """
    Datary exception for size limit exceed
    """

    def __init__(self, msg='', src_path='', size=-1):
        super(DatarySizeLimitException, self).__init__(self, msg)
        self.msg = msg
        self.src_path = src_path
        self.size = size

    def __str__(self):
        return "{};{};{}".format(self.msg, self.src_path, self.size)

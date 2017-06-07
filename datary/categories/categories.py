# -*- coding: utf-8 -*-
"""
Datary sdk Categories File
"""
from urllib.parse import urljoin
from datary.requests import DataryRequests

import structlog


logger = structlog.getLogger(__name__)


class DataryCategories(DataryRequests):
    """
    Datary Categories class.
    """

    DATARY_CATEGORIES = [
        "business",
        "climate",
        "consumer",
        "education",
        "energy",
        "finance",
        "government",
        "health",
        "legal",
        "media",
        "nature",
        "science",
        "sports",
        "socioeconomics",
        "telecommunications",
        "transportation",
        "other"
    ]

    headers = {}

    def __init__(self, **kwargs):
        """
        DataryCategories Init method
        """
        super(DataryCategories, self).__init__()
        self.headers = kwargs.get('headers', {})

    def get_categories(self):
        """
        Returns:
            List with the predefined categories in the system.
        """
        url = urljoin(DataryRequests.URL_BASE, "search/categories")

        response = self.request(url, 'GET', **{'headers': self.headers})
        return response.json() if response else self.DATARY_CATEGORIES

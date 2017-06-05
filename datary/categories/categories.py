# -*- coding: utf-8 -*-
import structlog

from urllib.parse import urljoin
from datary.requests import DataryRequests

logger = structlog.getLogger(__name__)


class DataryCategories(DataryRequests):

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

    def get_categories(self):
        """
        Returns:
            List with the predefined categories in the system.
        """
        url = urljoin(DataryRequests.URL_BASE, "search/categories")

        response = self.request(url, 'GET', **{'headers': self.headers})
        return response.json() if response else self.DATARY_CATEGORIES

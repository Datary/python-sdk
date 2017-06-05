# -*- coding: utf-8 -*-
import mock

from datary.test.test_datary import DataryTestCase
from datary.test.mock_requests import MockRequestResponse


class DataryCategoriesTestCase(DataryTestCase):
    @mock.patch('datary.Datary.request')
    def test_get_categories(self, mock_request):
        mock_request.return_value = MockRequestResponse("", json=self.categories,)
        categories = self.datary.get_categories()
        self.assertEqual(mock_request.call_count, 1)
        self.assertEqual(len(categories), len(self.categories))
        self.assertEqual(categories, self.categories)

        mock_request.reset_mock()
        mock_request.return_value = None
        categories = self.datary.get_categories()
        self.assertEqual(mock_request.call_count, 1)
        self.assertEqual(len(categories), len(self.datary.DATARY_CATEGORIES))
        self.assertEqual(sorted(categories), sorted(self.datary.DATARY_CATEGORIES))
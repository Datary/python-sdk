# -*- coding: utf-8 -*-


class MockRequestResponse:
    """
    Class to mock request responses, httpretty doesn't work with proxy..
    """

    def __init__(self, body, json={}, params={}, headers={}, path="",
                 status_code=200, encoding='utf-8'):

        self.status_code = status_code
        self.headers = headers

        self.text = body
        self.params = params

        self._path = path
        self._encoding = encoding

        self._json = json

    def encoding(self):
        return self._encoding

    def path(self):
        return self._path

    def json(self):
        return self._json

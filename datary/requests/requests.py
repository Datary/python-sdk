# -*- coding: utf-8 -*-
"""
Datary sdk Requests File
"""
import time
import requests
import structlog
from requests import RequestException


logger = structlog.getLogger(__name__)


class DataryRequests(object):
    """
    Datary Requests module class
    """

    URL_BASE = "http://api.datary.io/"
    tries_limit = 3
    headers = {}

    def __init__(self, **kwargs):
        """
        DataryRequests Init method
        """
        super(DataryRequests, self).__init__()
        self.headers = {"Content-Type": "application/x-www-form-urlencoded"}
        self.headers.update(kwargs.get('headers', {}))
        self.tries_limit = kwargs.get('tries_limit', 3)

    def request(self, url, http_method, tries=0, **kwargs):
        """
        Sends request to Datary passing config through arguments.

        ===========   =============   =======================================
        Parameter     Type            Description
        ===========   =============   =======================================
        url           str             destination url
        http_method   str             http methods of request
                                        [GET, POST, POST, DELETE]
        ===========   =============   =======================================

        Returns:
            content(): if HTTP response between the 200 range

        Raises:
            - Unknown HTTP method
            - Fail request to datary

        """
        try:
            #  HTTP GET Method
            if http_method == 'GET':
                content = requests.get(url, **kwargs)

            # HTTP POST Method
            elif http_method == 'POST':
                content = requests.post(url, **kwargs)

            # HTTP PUT Method
            elif http_method == 'PUT':
                content = requests.put(url, **kwargs)

            # HTTP DELETE Method
            elif http_method == 'DELETE':
                content = requests.delete(url, **kwargs)

            # Unkwown HTTP Method
            else:
                logger.error(
                    'Do not know {} as HTTP method'.format(http_method))
                raise Exception(
                    'Do not know {} as HTTP method'.format(http_method))

            # Check for correct request status code.
            if 199 < content.status_code < 300:
                tries = 0
                return content

            # Check if must wait x seconds returning 429 http code.
            elif content.status_code == 429:

                # TODO: RETRIEVE TIMESLEEP FROM RETURNED ERR MSG
                time_sleep = 2

                msg = "Fail Request to datary ({}) - Need to wait {} seconds"
                logger.warning(
                    msg.format(content.status_code, time_sleep),
                    url=url, http_method=http_method,
                    code=content.status_code,
                    text=content.text,
                    # kwargs=kwargs,
                )
                time.sleep(time_sleep)
                tries += 1

                if tries >= self.tries_limit:
                    logger.error(
                        "Request Tries Limit Exceeded!!",
                        url=url,
                        http_method=http_method,
                        # requests_args=kwargs,
                    )

                else:
                    return self.request(url, http_method, tries, **kwargs)

            else:
                msg = "Fail Request to datary done with code {}"
                tries = 0
                logger.error(
                    msg.format(content.status_code),
                    url=url, http_method=http_method,
                    code=content.status_code,
                    text=content.text,
                    # kwargs=kwargs,
                )

        # Request Exception
        except RequestException as ex:
            tries = 0
            logger.error(
                "Fail request to Datary - {}".format(ex),
                url=url,
                http_method=http_method,
                # requests_args=kwargs,
            )

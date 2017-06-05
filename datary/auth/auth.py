# -*- coding: utf-8 -*-
import structlog

from urllib.parse import urljoin
from datary.requests import DataryRequests

logger = structlog.getLogger(__name__)


class DataryAuth(DataryRequests):

    def get_user_token(self, user=None, password=None):
        """
        ===========   =============   ================================
        Parameter     Type            Description
        ===========   =============   ================================
        user          str             Datary username
        password      str             Datary password
        ===========   =============   ================================

        Returns:
            (str) User's token given a username and password.
        """

        payload = {
            "username": user or self.username,
            "password": password or self.password,
        }

        url = urljoin(DataryRequests.URL_BASE, "/connection/signIn")
        self.headers = {"Content-Type": "application/x-www-form-urlencoded"}

        response = self.request(
            url, 'POST', **{'headers': self.headers, 'data': payload})

        # Devuelve el token del usuario.
        user_token = str(response.headers.get("x-set-token", ''))

        if user_token:
            self.headers['Authorization'] = 'Bearer {}'.format(user_token)

        return user_token

    def sign_out(self):
        """
        ===========   =============   ================================
        Parameter     Type            Description
        ===========   =============   ================================
        ...           ...             ...
        ===========   =============   ================================

        Sign-out and invalidate the actual token.

        """

        url = urljoin(DataryRequests.URL_BASE, "connection/signOut")

        # Make sign_out request.
        response = self.request(url, 'GET')

        if response:
            self.token = None
            logger.info('Sign Out Succesfull!')

        else:
            logger.error(
                "Fail to make Sign Out succesfully :(",
                response=response)

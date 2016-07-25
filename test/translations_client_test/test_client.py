# -*- coding: utf-8 -*-
from threading import Thread
from unittest.case import TestCase

from zmq import Context, REP, LINGER, Poller, POLLIN

from translations_client import TranslationsClient, TranslationsServerError


_KEY1 = "k1"

_PLURAL1 = 1

_TRANSLATION1 = "t1"

_KEY2 = "k2"

_PLURAL2 = None

_TRANSLATION2 = "t2"

_LANGUAGE = "en"

_COUNTRY = "Shangri-La"

_HOST = "127.0.0.1"

_PORT = 5513

_ENCODING = "utf-8"

_TIMEOUT = 500  # milliseconds


class TestClient(TestCase):

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self._client_request = None

    def _server(self, response):
        """ Wait for a client request, record it and send the response. """
        context = Context()
        try:
            socket = context.socket(REP)
            try:
                socket.set(LINGER, 0)
                socket.bind("tcp://*:{}".format(_PORT))
                poller = Poller()
                poller.register(socket, POLLIN)
                sockets = dict(poller.poll(_TIMEOUT))
                if socket in sockets:
                    self._client_request = socket.recv_multipart()
                    if response:
                        socket.send_multipart(response)
            finally:
                socket.close()
        finally:
            context.destroy(linger=0)

    def _request(self, response, *request, client=None):
        """ Create a simulated server and let a client make one request.

        The client request received on the server side will be saved to
        `self._client_request`.

        :param request: The request to make. List of arguments to give to the
            clients get function.
        :type request: []
        :param response: The response that the server should send.
        :type response: [bytes]
        :return: The response from the client.
        :rtype: [str]
        """
        close_client = client is None  # close only if not provided
        self._client_request = None
        server = Thread(target=self._server, args=(response, ), name="server")
        server.start()
        try:
            if client is None:
                client = TranslationsClient(_HOST, _PORT)
            try:
                return client.get(*request)
            finally:
                if close_client:
                    client.close()
        finally:
            server.join()

    def test_communication(self):
        """ Make a request with the client and verify the resulting request.
        """
        response = [_TRANSLATION1.encode(_ENCODING)]
        translation = self._request(
            response, _LANGUAGE, _COUNTRY, (_KEY1, _PLURAL1))
        self.assertEqual(translation, _TRANSLATION1)
        self.assertEqual(
            [r.decode(_ENCODING) for r in self._client_request],
            [_LANGUAGE, _COUNTRY, _KEY1, str(_PLURAL1)])

    def test_timeout(self):
        """ Tell the server to not send any response and check the resulting
        "translation".
        """
        client = TranslationsClient(_HOST, _PORT, timeout=0)
        try:
            translation = self._request(
                None, _LANGUAGE, _COUNTRY, (_KEY1, _PLURAL1), client=client)
        finally:
            client.close()
        self.assertEqual(translation, _KEY1)

    def test_server_error(self):
        """ Tell the server to return an error response and check the raised
        exception.
        """
        with self.assertRaises(TranslationsServerError):
            self._request([b""], _LANGUAGE, _COUNTRY, (_KEY1, _PLURAL1))

    def test_multiple_keys(self):
        """ Test requesting two translation, check the result and the client
        request on the server side.
        """
        response = [
            _TRANSLATION1.encode(_ENCODING), _TRANSLATION2.encode(_ENCODING)]
        translation = self._request(
            response, _LANGUAGE, _COUNTRY, (_KEY1, _PLURAL1),
            (_KEY2, _PLURAL2))
        self.assertEqual(translation, [_TRANSLATION1, _TRANSLATION2])
        self.assertEqual(
            [r.decode(_ENCODING) for r in self._client_request],
            [_LANGUAGE, _COUNTRY, _KEY1, str(_PLURAL1), _KEY2, ""])

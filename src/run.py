#!/usr/bin/env python
# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from sys import path

from translations_client import TranslationsClient


def _connect_to_debug_server(server):
    path.append("../.pydevsrc/")  # @IgnorePep8
    import pydevd  # @UnresolvedImport pylint: disable=import-error
    pydevd.settrace(
        server, stdoutToServer=True, stderrToServer=True, suspend=False)

if __name__ == "__main__":
    parser = ArgumentParser(
        "Get a translation for a key in a specific language from a "
        "translation service server. Ment to be used for testing/checking.")
    parser.add_argument(
        "host", help="The translation service server IP address")
    parser.add_argument("port", help="The translation service server port")
    parser.add_argument("language", help="The language for the translation")
    parser.add_argument("key", help="The key/text to translate")
    parser.add_argument("--country", help="The country for the translation")
    parser.add_argument("--plural", help="The plural from for the translation")
    parser.add_argument(
        "-d", "--remote-debug",
        help="Remote debug server, for example 192.168.33.1")
    args, _unknown = parser.parse_known_args()
    if args.remote_debug:
        _connect_to_debug_server(args.remote_debug)
    client = TranslationsClient(args.host, args.port)
    try:
        translation = client.get(
            args.language, args.country, (args.key, args.plural))
    finally:
        client.close()
    print("Translation:\n" + translation)

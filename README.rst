TranslationsClient
==================

.. image:: https://api.travis-ci.org/GreenelyAB/TranslationsClient.svg?branch=master
    :target: https://travis-ci.org/GreenelyAB/TranslationsClient?branch=master

A translation service client.


Usage example
-------------

::

    >>> from translations_client import TranslationsClient
    >>> client = TranslationsClient("127.0.0.1", 5512)
    >>> print(client.get("se", None, "I have many"))
    "Jag har många"
    >>> print(client.get("se", None, "I have many", "translations"))
    ["Jag har många", "översättningar"]
    >>> print(client.get("se", None, ("I have many", 1), ("translations", 1)))
    ["Jag har en", "översättning"]
    >>> print(client.get("se", None, ("I have many", 0), ("translations", 0)))
    ["Jag har inga", "översättningar"]

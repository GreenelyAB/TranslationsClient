# -*- coding: utf-8 -*-
import time


class TranslationCache:

    def clear(self):
        raise NotImplementedError("Implement to clear cache.")

    def get_multiple(self, language, country, keys):
        """ Get multiple keys from the cache - the once not found will remain
            None
        :param language: The language code
        :param country: The country code
        :param key: The key - either str or tuple
        :return: A list of translations, None entries for not found entries
        """
        raise NotImplementedError("Implement to use cache.")

    def get_cache_key(self, language, country, key):
        """ Build a unique identifier for a given key, lang and country
        :param language: The language code
        :param country: The country code
        :param key: The key - either str or tuple
        :return: The cache key that should be used
        """
        if isinstance(key, str):
            _plural_int = None
        else:
            _plural_int = key[1]
            key = key[0]

        return '{}/{}/{}/{}'.format(language, country, key, _plural_int)

    def set_multiple(self, language, country, keys, translations):
        """ Set multiple keys on the cache - the number of keys and
            translations should be the same size.

        :param language: The language code
        :param country: The country code
        :param keys: A list of the keys (elements can be str or tuple)
        :param translations: A list of the translations
        """
        raise NotImplementedError("Implement to use cache.")


class DictTimeoutTranslationCache(TranslationCache):

    def __init__(self, timeout=10):
        self._timeout = timeout
        self._storage = {}

    def clear(self):
        self._storage = {}

    def get_multiple(self, language, country, keys):
        _translated = []

        for key in keys:
            cache_key = self.get_cache_key(language, country, key)
            value = self._retrieve(cache_key)
            _translated.append(value)

        return _translated

    def _retrieve(self, key):
        result = self._storage.get(key, None)

        if result:
            translation, stored_time = result

            if time.time() - stored_time > \
                    self._timeout:
                result = None
            else:
                result = translation

        return result

    def set_multiple(self, language, country, keys, translations):
        for key, translation in zip(keys, translations):
            cache_key = self.get_cache_key(language, country, key)
            self._storage[cache_key] = (translation, time.time())

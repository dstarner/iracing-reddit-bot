from abc import ABC, abstractmethod

from diskcache import Cache as DiskCache


class Cache(ABC):

    @abstractmethod
    def cache_comment_id(self, comment_id):
        pass

    @abstractmethod
    def comment_response_exists(self, comment_id):
        pass


class FilesystemCache(Cache):
    """
    Maintains a cache on the local filestem
    This is not suitable for deployed applications as resources may turn and clear cache
    """

    def __init__(self, cache_directory):
        self.cache = DiskCache(cache_directory)

    def cache_comment_id(self, comment_id):
        with self.cache as cache:
            cache.add(comment_id, True)

    def comment_response_exists(self, comment_id):
        with self.cache as cache:
            return cache.get(comment_id, default=False)

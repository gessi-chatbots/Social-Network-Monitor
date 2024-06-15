
from abc import ABC, abstractmethod

class ServiceInterface(ABC):
    @abstractmethod
    def search_posts(self, query, limit, token, from_date=None, to_date=None):
        pass

    @abstractmethod
    def filter_posts(self, posts, from_date=None, to_date=None):
        pass

    @abstractmethod
    def save_posts(self, posts):
        pass
    
    @abstractmethod
    def save_posts_json_mastodon(self, data, platform):
        pass

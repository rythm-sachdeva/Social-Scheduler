from abc import ABC, abstractmethod
from .models import SchedulePost

class PosterABS(ABC):
    @abstractmethod
    def post(self,post:SchedulePost):
        """Posting Post to Social Media app"""



class Poster:
    def __init__(self,adapter:PosterABS):
        self.poster  = adapter

    def post_to_social_media(self,post:SchedulePost):
        self.poster.post(post)
        
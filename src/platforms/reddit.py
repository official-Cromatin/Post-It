import praw
import praw.models
import logging
from utils.event_counter import Event_Counter
from utils.datetime_tools import get_elapsed_time_milliseconds
from typing import Union
from datetime import datetime

class Reddit_Adapter(praw.Reddit):
    """A class that extends and abstracts the functionality of the `praw.Reddit` class by adding 
    logging and request tracking capabilities."""
    VERSION = "1.0"
    number_of_instances = 0

    def __init__(self, client_id:str, client_secret:str):
        self.__instance_number = self.__class__.number_of_instances
        self.__class__.number_of_instances += 1
        
        super().__init__(
            client_id = client_id,
            client_secret = client_secret,
            user_agent="Small discord bot to embed posts (given by url) into an standardized format"
        )
        self.__events = Event_Counter(1000)
        self.__logger = logging.getLogger(f"pltfm.reddit.{self.__instance_number}")

    def fetch(self, post_url:str) -> praw.models.Submission:
        """Fetches specified submission (post) and returns it"""
        start_time = datetime.now().timestamp()
        self.__events.increment()
        subm: praw.models.Submission = self.submission(url = post_url)
        self.__logger.debug(f"Submission for post (URL: {post_url}), successfully fetched after {get_elapsed_time_milliseconds(datetime.now().timestamp() - start_time)}")
        return subm

    
    def get_total_requests(self) -> int:
        """Returns the total number of events"""
        return self.__events.get_total_events()
    
    def get_events_last_5m(self) -> int:
        return self.__events.get_count("5m")
    
    def get_events_last_5m_10m_15m(self) -> tuple[int]:
        return (self.__events.get_count("5m"), self.__events.get_count("10m"), self.__events.get_count("15m"))
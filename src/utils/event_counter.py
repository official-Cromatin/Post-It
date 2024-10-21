from datetime import datetime
import re

class Event_Counter:
    """A class to track and count events, storing the event timestamps and allowing queries 
    
    for the number of events in specific time windows (e.g., last 5 minutes, 10 minutes)."""
    REGEX_PATTERN = r'(\d+)\s*(sec|second|seconds|s|min|minute|minutes|m|h|hour|hours|d|day|days)'
    TIME_MULTIPLIERS = {
        'sec': 1, 'second': 1, 'seconds': 1, 's': 1,
        'min': 60, 'minute': 60, 'minutes': 60, 'm': 60,
        'h': 3600, 'hour': 3600, 'hours': 3600,
        'd': 86400, 'day': 86400, 'days': 86400
    }

    def __init__(self, retention_duration:int = 900) -> None:
        """
        Initializes the Event_Counter object with a specified retention duration.

        Args:
            retention_duration (int, optional): 
                The time period (in seconds) for which event data should be retained. Defaults to 900 (15 minutes).
        
        uwu
        """
        self.__events:list[float] = []
        self.__total_events = 0
        self.__retention_duration = retention_duration

    def cleanup(self):
        """Cleans up events that are older than the retention duration.
        
        Removes all events that occurred outside the defined retention window."""
        offset_time = datetime.now().timestamp() - self.__retention_duration
        while len(self.__events) > 0:
            event_time = self.__events[0]
            if event_time < offset_time:
                self.__events.pop(0)
            else:
                break

    @classmethod
    def duration_to_seconds(cls, duration_str:str) -> int:
        """Converts a human-readable duration string (e.g., '5min 2sec') into its equivalent in seconds.

        Args:
            duration_str (str): The string representing the duration (e.g., "5min 2sec").

        Returns:
            int: The total duration in seconds derived from the input string."""
        matches = re.findall(cls.REGEX_PATTERN, duration_str, flags=re.IGNORECASE)
        
        total_seconds = 0
        for value, unit in matches:
            unit = unit.lower()
            total_seconds += int(value) * cls.TIME_MULTIPLIERS[unit]
        
        return total_seconds

    def increment(self, count:int = 1, skip_cleanup:bool = False):
        """Increments the event count by a specified number of events.

        Args:
            count (int, optional): The number of events to add. Defaults to 1.
            skip_cleanup (bool, optional): If True, skips the cleanup process. Defaults to False."""
        timestamp = datetime.now().timestamp()
        self.__total_events += count
        self.__events.extend([timestamp] * count)
        
        if skip_cleanup:
            return
        self.cleanup()

    def get_count(self, time_window:str = "5M") -> int:
        """Returns the number of events that occurred within a specified time window.

        Args:
            time_window (str, optional): 
                The time window to query, e.g., "5M" for 5 minutes. Defaults to "5M".

        Returns:
            int: The count of events that occurred within the specified time window."""
        self.cleanup()
        
        offset_time = datetime.now().timestamp() - self.duration_to_seconds(time_window)
        counter = 0
        for event_time in self.__events:
            if event_time > offset_time:
                counter += 1
            else:
                break

        return counter

    def get_total_events(self) -> int:
        """Returns the total number of events tracked by the Event_Counter.

        Returns:
            int: The total number of events that have been recorded."""
        return self.__total_events

if __name__ == "__main__":
    from time import sleep
    counter = Event_Counter(1)
    counter.increment()
    sleep(1)
    counter.increment()
    print(counter.get_count("5sEc"))
    sleep(0)
    print(counter.get_count("5sEc"))
from utils.singleton import Singleton
from utils.adv_configparser import Advanced_ConfigParser
from platforms.reddit import Reddit_Adapter

@Singleton
class Portal:
    bot_config:Advanced_ConfigParser = None
    platforms_config:Advanced_ConfigParser = None
    STARTUP_TIMESTAMP:float = None
    no_executed_commands:int = 0
    no_succeeded_commands:int = 0
    no_failed_commands:int = 0
    reddit_adapter: Reddit_Adapter = None
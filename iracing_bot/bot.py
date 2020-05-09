class IRacingBot:
    """Contains all of the functionality for the iRacing subreddit bot
    """

    def __init__(self, subreddit, sporting_code, reddit, response_generator, response_cache):
        self.subreddit = subreddit
        self.sporting_code = sporting_code
        self.reddit = reddit
        self.response_generator = response_generator
        self.response_cache = response_cache

    def begin_blocking_loop(self):
        """Core loop of the bot which will keep it going and going
        """
        pass

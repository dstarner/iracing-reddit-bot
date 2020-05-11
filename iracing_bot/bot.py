from praw.exceptions import PRAWException


DEFAULT_REPLY_FOOTER = """

*This response was made by an automated bot. Please see
 [the project for information and usage](https://github.com/dstarner/iracing-reddit-bot). If you
 feel as though there was an error,
 [please file an issue](https://github.com/dstarner/iracing-reddit-bot/issues).*
"""


class IRacingBot:
    """Contains all of the functionality for the iRacing subreddit bot
    """
    BOT_PREFIXES = ['!irbot']
    REPLY_FOOTER = DEFAULT_REPLY_FOOTER

    def __init__(self, subreddit, sporting_code, reddit, response_generator,
                 response_cache, verbose=True):
        self.subreddit = subreddit
        self.sporting_code = sporting_code
        self.reddit = reddit
        self.response_generator = response_generator
        self.response_cache = response_cache
        if not self.sporting_code.parsed:
            self.sporting_code.parse_pdf()

    def begin_blocking_loop(self):
        """Core loop of the bot which will keep it going and going
        """
        print(f'Starting to listen on r/{self.subreddit}')
        subreddit = self.reddit.subreddit(self.subreddit)
        # Constantly stream in new comments from the selected SubReddit
        for comment in subreddit.stream.comments():
            text = str(comment.body).strip()
            # Skip if empty message or if its been replied to already
            if not text or comment.author.name == self.reddit.config.username:
                continue

            if self.response_cache.comment_response_exists(comment.id):
                print(f'comment {comment.id} by {comment.author.name} already is cached, skipping')
                continue

            # ignore comments if they aren't asking for the bot and strip it from the text
            cur_prefix = ''
            for prefix in self.BOT_PREFIXES:
                if text.startswith(prefix):
                    cur_prefix = prefix
                    text = text.replace(cur_prefix, '', 1).strip()
            if not cur_prefix:
                continue

            print(f'found comment {comment.id} by {comment.author.name}')
            # we can now generate our message from the text
            response = self.response_generator.respond_to_request(text)

            try:
                comment.reply(self.amend_legalese(response))
                self.response_cache.cache_comment_id(comment.id)
            except PRAWException as e:
                print(str(e))
            print(f'replied to comment {comment.id} by {comment.author.name}')

    def amend_legalese(self, msg):
        """
        Slaps the legalese content onto whatever message is generated,
        so we stay in good graces with the reddit community
        """
        return msg + self.REPLY_FOOTER

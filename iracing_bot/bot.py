import logging
import sys

from praw.exceptions import PRAWException


logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

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
        if verbose:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)
        if not self.sporting_code.parsed:
            self.sporting_code.parse_pdf()

    def begin_blocking_loop(self):
        """Core loop of the bot which will keep it going and going
        """
        subreddit = self.reddit.subreddit(self.subreddit)
        # Constantly stream in new comments from the selected SubReddit
        for comment in subreddit.stream.comments():
            text = str(comment.body).strip()
            # Skip if empty message or if its been replied to already
            if not text:
                continue

            if self.response_cache.comment_response_exists(comment.id):
                logger.debug(
                    'comment %d by %s already is cached, skipping', comment.id, comment.author.name
                )
                continue

            # ignore comments if they aren't asking for the bot and strip it from the text
            cur_prefix = ''
            for prefix in self.BOT_PREFIXES:
                if text.startswith(prefix):
                    cur_prefix = prefix
                    text = text.replace(cur_prefix, '', 1).strip()
            if not cur_prefix:
                continue

            logging.debug('found comment by %s: %s', comment.author.name, text)
            # we can now generate our message from the text
            # TODO: uncomment me--response = self.response_generator.respond_to_request(text)

            try:
                # TODO: uncomment me--comment.reply(self.amend_legalese(response))
                self.response_cache.cache_comment_id(comment.id)
            except PRAWException as e:
                logger.exception(e)
            logging.info('replied to comment %d by %s')

    def amend_legalese(self, msg):
        """
        Slaps the legalese content onto whatever message is generated,
        so we stay in good graces with the reddit community
        """
        return msg + self.REPLY_FOOTER

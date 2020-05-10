import configargparse

import praw

from iracing_bot.bot import IRacingBot
from iracing_bot.cache import FilesystemCache
from iracing_bot.responder import ResponseGenerator
from iracing_bot.sporting_code import SportingCode, BulletFormatter, ImageFormatter


CONFIG_FILE = ".bot.yaml"
URL = 'https://d3bxz2vegbjddt.cloudfront.net/members/pdfs/FIRST_Sporting_Code_18_09_printable.pdf'


def parse_arguments():
    """
    Creates a nice command line, config file, environment variable interface to
    interact with the program through.
    """
    p = configargparse.ArgParser(
        description=(
            'Starts a Reddit bot that replies to certain iRacing posts. '
            'It attempts to perform text classification against comment/body content and '
            'creates an inteligent reply that the original poster may be looking for.'
        ),
        default_config_files=[CONFIG_FILE]
    )

    # Program Control Flags
    # ---------------------
    p.add('-c', '--config', is_config_file=True, help='override the config file path')
    p.add('-v', '--verbose', help='enable verbose logging', action='store_true')
    p.add(
        '-s', '--subreddit', help='Subreddit to listen to',
        env_var='REDDIT_SUB', default='iracingbottest'
    )
    p.add('--sporting-code', help='URL to the PDF of the sporting code', default=URL)
    p.add(
        '-d', '--training', type=str, default='training.yaml',
        env_var='TRAINING_PATH', help='Training YAML file to load from'
    )
    p.add(
        '--cache', type=str, choices=['redis', 'disk'], default='disk',
        env_var='BOT_CACHE_TYPE', help='Type of cache to use for responses'
    )

    # Authentication Flags
    # --------------------
    p.add(
        '-u', '--username', required=True, env_var='REDDIT_USERNAME', type=str,
        help='reddit username of the associated account for auth'
    )
    p.add(
        '-p', '--password', required=True, env_var='REDDIT_PASSWORD', type=str,
        help='reddit password of the associated account for auth'
    )
    p.add(
        '--client-id', required=True, env_var='REDDIT_CLIENT_ID', type=str,
        help='reddit client ID of the associated app for auth'
    )
    p.add(
        '--client-secret', required=True, env_var='REDDIT_CLIENT_PASSWORD',
        help='reddit client secret of the associated app for auth', type=str
    )
    return p.parse_args()


def main():
    """Entrypoint for the entire application"""
    options = parse_arguments()

    # 1. Sporting code is used to link to specific sections in the sporting code
    sporting_code = SportingCode(
        options.sporting_code,
        # Format overrides are used to control how the final sporting code sections
        # are rendered. These are used if the PDF parser cannot correctly / easily
        # pick up the formatting in the PDF file.
        format_overrides={
            '3.2.2.1.': BulletFormatter(),
            '3.2.2.2.': BulletFormatter(),
            '3.5.1.1.': ImageFormatter('https://imgur.com/a/M21QoWv', cut_at='Incident Type'),
            '3.5.1.2.': ImageFormatter('https://imgur.com/a/yFJQSV2', cut_at='Incident Type'),
            '3.6.1.1.': ImageFormatter('https://imgur.com/a/1ayfC8y', cut_at='Session Type'),
            '5.5.4.5.': ImageFormatter('https://imgur.com/a/vdShzku', cut_at='Tier Name')
        }
    )
    print(f"⌚️Attempting to parse Sporting Code PDF...")
    sporting_code.parse_pdf()
    print("🎉Parsed Successfully!")

    # 2. Reddit authentication instance
    print(f"⌚️Attempting connection to Reddit as {options.username}...")
    reddit = praw.Reddit(user_agent=f"iRacing Bot (by {options.username})",
                        client_id=options.client_id, client_secret=options.client_secret,
                        username=options.username, password=options.password)
    print("🎉Connected Successfully!")

    # 3. Response Generator
    print(f"⌚️Training Response Generator from file {options.training}...")
    response_generator = ResponseGenerator(training_file=options.training)
    print(f"🎉Training Successfully!")

    # 4. Response cache to prevent us from answering the same comment twice
    if options.cache == 'disk':
        cache = FilesystemCache('.iracing_bot_cache')  # TODO: make this arg an option

    # Core iRacing bot that orchestrates everything
    bot = IRacingBot(
        subreddit=options.subreddit,
        sporting_code=sporting_code,
        reddit=reddit,
        response_generator=response_generator,
        response_cache=cache,
    )
    bot.begin_blocking_loop()


if __name__ == '__main__':
    main()

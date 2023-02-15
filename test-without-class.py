import logging
import sys
import os
import asyncio
from twitchio.ext import commands

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('[%(asctime)s] [%(levelname)s] %(name)s: %(message)s'))
logger.addHandler(handler)

logger.debug(f"token:{os.environ.get('TWITCH_TOKEN')}")
logger.debug(f"client:{os.environ['TWITCH_CLIENT_ID']}")

bot = commands.Bot(
        token=os.environ['TWITCH_TOKEN'],
        irc_token=os.environ['TWITCH_TOKEN'], # can we use api oauth token to irc?
        client_id=os.environ['TWITCH_CLIENT_ID'],
        nick=os.environ['TWITCH_BOT_NICK'],
        prefix=os.environ['TWITCH_BOT_PREFIX'],
        initial_channels=[os.environ['TWITCH_CHANNEL']])

@bot.event
async def event_ready():
    """Called once when the bot goes online"""
    logger.debug(f'bot is ready nick:{bot.nick}')
    ws = bot._ws
    await ws.send_privmsg(os.environ.get('TWITCH_CHANNEL'), f"yo!")


@bot.command(name='hello')
async def hello(ctx):
    logger.debug(f'hello user:{ctx.author.name}')
    # ctx is based from caller user
    await ctx.channel.send(f'{ctx.author.name} aww aww')
    #bot.irc_connect()
    #bot.join_channel(os.environ['TWITCH_CHANNEL'])
    #bot.irc_disconnect()

bot.run()


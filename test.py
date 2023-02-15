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

class Bot(commands.Bot):

    def __init__(self):
        super().__init__(
                token=os.environ['TWITCH_TOKEN'],
                nick='justabot', #nick assignment is useless here
                prefix=os.environ['TWITCH_BOT_PREFIX'],
                initial_channels=[os.environ['TWITCH_CHANNEL']])
    
    async def event_ready(self):
        logger.debug(f'bot is ready nick: {self.nick}')
        logger.debug(f'user id is: {self.user_id}')
        logger.debug(f"{self.get_channel(os.environ.get('TWITCH_CHANNEL'))}")
        ch = self.get_channel(os.environ.get('TWITCH_CHANNEL'))
        if ch is not None:
            loop = asyncio.get_event_loop()
            loop.create_task(ch.send('chat bot is ready, use !hello|!chat for testing'))

    @commands.command(name='hello')
    async def hello(self, ctx: commands.Context):
        logger.debug(f'hello user: {ctx.author.name}')
        await ctx.channel.send(f'[BOT]{ctx.author.name} aww~~ hello world!')

    @commands.command(name='chat')
    async def chat(self, ctx: commands.Context):
        logger.debug(f'chat user: {ctx.author.name}')
        await ctx.channel.send(f"[BOT]{ctx.author.name} I\'m not ready to do this~")

bot = Bot()
bot.run()



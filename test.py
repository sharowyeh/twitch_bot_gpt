import logging
import sys
import os
import asyncio
from twitchio.ext import commands

logging.basicConfig(stream=sys.stdout,
                    level=logging.DEBUG,
                    format='[%(asctime)s] [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger(__name__)

if os.environ.get('OPENAI_API_KEY') is None:
    print('openai api key can not be empty')
    exit()

logger.debug(f"token:{os.environ.get('TWITCH_TOKEN')}")
logger.debug(f"client:{os.environ['TWITCH_CLIENT_ID']}")

from chat import GPTChat
gptchat = GPTChat()

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
            loop.create_task(ch.send('chat bot is ready, use !chat or !hello for testing'))

    @commands.command(name='hello')
    async def hello(self, ctx: commands.Context):
        logger.debug(f'cmd:{ctx.command.name} user:{ctx.author.name}')
        await ctx.reply(f'[BOT] aww~~ hello world! {ctx.author.name}')

    @commands.command(name='assistant')
    async def assistant(self, ctx: commands.Context):
        """given additional assistant behavor to gpt 3.5"""
        logger.debug(f'cmd:{ctx.command.name} user:{ctx.author.name} msg:{ctx.message.content}')
        text = ctx.message.content[6:]
        if not text:
            return
        gptchat.setInitAssistant(text)
        await ctx.send(f"{ctx.author.mention} [BOT] The assistant has been set")

    async def mention_reply(self, ctx: commands.Context, text: str):
        """helper function avoid reply message exceed 500 ccharacters"""
        REPLY_LENGTH = 150 # keep single sentence for twtich chat room
        logger.debug(f'')
        reply = ""
        delimiter = "\n"
        sp = text.split(delimiter)
        if len(sp[0]) > REPLY_LENGTH:
            delimiter = "."
            sp = text.split(delimiter)
        while (len(sp) > 0):
            # ref:array.deque(), popleft()
            reply += sp.pop(0) + "."

            if len(reply) > REPLY_LENGTH:
                logger.debug(f"reply: {reply}")
                await ctx.send(f"{ctx.author.mention} [BOT] {reply}")
                reply = ""
        
        if reply and reply != "." and len(reply.strip()) > 0:
            await ctx.send(f"{ctx.author.mention} [BOT] {reply}")
            logger.debug(f'reply: {reply}')

    @commands.command(name='chat')
    async def chat(self, ctx: commands.Context):
        logger.debug(f'cmd:{ctx.command.name} user:{ctx.author.name} msg:{ctx.message.content}')
        # remove command !chat
        text = ctx.message.content[6:]
        if not text:
            await ctx.send(f"{ctx.author.mention} [BOT] how's today?")
            return
        # increase temperature...
        gptchat.setTemp(0.7)
        try:
            reply_text = gptchat.chatCompletion(text, 50)
        except Exception as err:
            logger.exception(f"Unexpected {err}, {type(err)}")
            reply_text = "I got error"
 
        # send whole text at once from response
        await self.mention_reply(ctx, reply_text)
        #await ctx.send(f"{ctx.author.mention} [BOT] {reply_text}")

    @commands.command(name='text')
    async def text(self, ctx: commands.Context):
        """previous version for text completion using davinci 003 engine"""
        logger.debug(f'cmd:{ctx.command.name} user:{ctx.author.name} msg:{ctx.message.content}')
        # remove command !chat
        text = ctx.message.content[6:]
        if not text:
            await ctx.send(f"{ctx.author.mention} [BOT] how's today?")
            return
        # increase temperature...
        gptchat.setTemp(0.7)
        try:
            reply_text = gptchat.completion(text)
        except Exception as err:
            logger.exception(f"Unexpected {err}, {type(err)}")
            reply_text = "I got error"
 
        # send whole text at once from response
        await ctx.send(f"{ctx.author.mention} [BOT] {reply_text}")
        # still need a end mark, it is annoy in twitch chat dialog?
        #await ctx.send(f"{ctx.author.mention} [BOT] 😘")

bot = Bot()
bot.run()



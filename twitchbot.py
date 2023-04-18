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

from gptchat import GPTChat
gptchat = GPTChat()

from datastore import DataStore
gptdata = DataStore()

# pre-defined stuff
TWITCH_CHAT_REPLY_LENGTH = 150 # keep single sentence for twtich chat room
GPT_DEFAULT_SYSTEM_CONTENT = "always brief reply in a sentence"

# TODO: free trial is 20 RPM and 40k TPM, refer to [rate limit](https://platform.openai.com/docs/guides/rate-limits)
#   based on the !chat usage frequences to design chunks for sending requests
# TODO: behaviors should design in the gptchat.py
GPT_RATE_LIMIT = 40000
GPT_TOKENS_PER_REQUEST = 4096 # GPT3.5 tokens per request

class TwtichBot(commands.Bot):

    def __init__(self):
        super().__init__(
                token=os.environ['TWITCH_TOKEN'],
                nick='justabot', #nick assignment is useless here
                prefix=os.environ['TWITCH_BOT_PREFIX'],
                initial_channels=[os.environ['TWITCH_CHANNEL']])
        self.topic_id = None
    
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
        await ctx.reply(f'[BOT] aww~~ {ctx.channel.name} force me reply twice🙄')

    @commands.command(name='setgpt')
    async def setgpt(self, ctx: commands.Context):
        """given a name for topic used for bot characteristic"""
        logger.debug(f'cmd:{ctx.command.name} user:{ctx.author.name} msg:{ctx.message.content}')
        text = ctx.message.content.replace(f"!{ctx.command.name} ", "")
        if not text:
            return
        #TODO: so far data store is mandatory
        #TODO: always create new or getTopic from exists?
        self.topic_id = gptdata.createTopic(text)
        if not self.topic_id:
            await ctx.reply(f'[BOT] my datastore goes wrong!')
            return
        # simply create default system message for the new topic,
        #   keep reply briefly for the twitch chat room 
        gptchat.setInitSystem(GPT_DEFAULT_SYSTEM_CONTENT)
        msg_id = gptdata.createMessage(self.topic_id, GPT_DEFAULT_SYSTEM_CONTENT, "system", 0, "", "", "", 0, 0, 0)
        logger.debug(f'msg:{msg_id} system message created for topic:{self.topic_id}')
        await ctx.reply(f'[BOT] topic created, use !assistant for given features or !chat directly🙄')

    @commands.command(name='assistant')
    async def assistant(self, ctx: commands.Context):
        """given additional assistant behavor to gpt 3.5"""
        logger.debug(f'cmd:{ctx.command.name} user:{ctx.author.name} msg:{ctx.message.content}')
        text = ctx.message.content.replace(f"!{ctx.command.name} ", "")
        if not text:
            return
        #TODO: so far data store is mandatory
        if not self.topic_id:
            await ctx.reply(f'[BOT] my datastore goes wrong!')
            return
        msg_id = gptdata.createMessage(self.topic_id, text, "assistant", 0, "", "", "", 0, 0, 0)
        logger.debug(f'msg:{msg_id} assistant message create for topic:{self.topic_id}')
        gptchat.setInitAssistant(text)
        await ctx.reply(f"[BOT] assistant set, use !chat to see what you get😊")

    @commands.command(name='chat')
    async def chat(self, ctx: commands.Context):
        logger.debug(f'cmd:{ctx.command.name} user:{ctx.author.name} msg:{ctx.message.content} param:{ctx.command.params}')
        # remove command !chat
        text = ctx.message.content.replace(f"!{ctx.command.name} ", "")
        if not text:
            await ctx.send(f"{ctx.author.mention} [BOT] how's today?")
            return
        #TODO: so far data store is mandatory
        if not self.topic_id:
            await ctx.reply(f'[BOT] my datastore goes wrong!')
            return
        msg_id = gptdata.createMessage(self.topic_id, text, "user", 0, "", "", "", 0, 0, 0)
        logger.debug(f'msg:{msg_id} user message create for topic:{self.topic_id}')
        # increase temperature...
        gptchat.setTemp(0.7)
        gptchat.setTokenLength(50)
        total_tokens = 0
        try:
            (reply_text, reply_objs) = gptchat.chatCompletion(text, 50)
            for resp in reply_objs:
                msg_id = gptdata.createMessage(
                    self.topic_id, 
                    resp.choices[0].message.content, 
                    resp.choices[0].message.role, 
                    resp.created, 
                    resp.id, 
                    resp.model, 
                    resp['object'], 
                    resp.usage.completion_tokens, 
                    resp.usage.prompt_tokens, 
                    resp.usage.total_tokens)
                logger.debug(f'msg:{msg_id} assistant reply message create for topic:{self.topic_id}')
                logger.debug(f'token usage:{resp.usage}')
                total_tokens = resp.usage.total_tokens
            # update for token usage
            gptdata.updateTopicTokens(self.topic_id)
        except Exception as err:
            logger.exception(f"Unexpected {err}, {type(err)}")
            reply_text = "I got error"
 
        # chunk text prevent exceeded twitch chat length
        for chunk_text in gptchat.splitText(reply_text):
            await ctx.send(f"{ctx.author.mention} [BOT] {chunk_text}")

        # remind chat gpt rate limit
        if total_tokens > (GPT_TOKENS_PER_REQUEST * 0.85):
            await ctx.send(f'[BOT] I\'m going to get error! stop chatting and help me!😫')
        elif total_tokens > (GPT_TOKENS_PER_REQUEST * 0.7):
            await ctx.send(f'[BOT] Soft remind, chat token usage is over 70%, make chunks or squash history!🙄')  

    @commands.command(name='text')
    async def text(self, ctx: commands.Context):
        """previous version for text completion using davinci 003 engine"""
        logger.debug(f'cmd:{ctx.command.name} user:{ctx.author.name} msg:{ctx.message.content}')
        # remove command
        text = ctx.message.content.replace(f"!{ctx.command.name} ", "")
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
 
        # chunk text prevent exceeded twitch chat length
        for chunk_text in gptchat.splitText(reply_text):
            await ctx.send(f"{ctx.author.mention} [BOT] {chunk_text}")

bot = TwtichBot()
bot.run()

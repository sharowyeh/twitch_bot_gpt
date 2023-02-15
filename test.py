import logging
import sys
import os
import asyncio
from twitchio.ext import commands
import openai

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('[%(asctime)s] [%(levelname)s] %(name)s: %(message)s'))
logger.addHandler(handler)

if os.environ.get('OPENAI_API_KEY') is None:
    print('openai api key can not be empty')
    exit()

openai.api_key = os.environ.get('OPENAI_API_KEY')

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
        logger.debug(f'cmd:{ctx.command.name} user:{ctx.author.name}')
        await ctx.reply(f'[BOT] aww~~ hello world! {ctx.author.name}')

    @commands.command(name='chat')
    async def chat(self, ctx: commands.Context):
        logger.debug(f'cmd:{ctx.command.name} user:{ctx.author.name} msg:{ctx.message.content}')
        # remove command !chat
        text = ctx.message.content[6:]
        if not text:
            await ctx.send(f"{ctx.author.mention} [BOT] how's today?")
            return
        # twitch chat is not fit for long text, restrict reponse in 1 or 2 sentences
        text = text + ",reply in 1 or 2 sentences" #TODO: should language specific?
        temp = 0.7
        # let openai API call by async? but completion does not have acreate method
        # or use from asgiref.sync import sync_to_async? [link](https://github.com/openai/openai-python/issues/98)
        token_length = 100
        #TODO: try catch here, you may need get exception from API rate limit!
        resp = openai.Completion.create(
            engine="text-davinci-003",
            prompt=text,
            temperature=temp,
            max_tokens=token_length,
    #        frequency_penalty=0,
    #        presence_penalty=0
    #        stream=False,
    #        stop="\n",
        )

        reply_text = ""
        # we still need looping for wide-char language(took more tokens for response)
        while True:
            logger.debug(resp)
            if not hasattr(resp, 'choices') or len(resp.choices) == 0:
                await ctx.send("I got no response")
                break
            if not resp.choices[0].text:
                await ctx.send("I got empty response")
                break
            logger.debug(f"choices: {resp.choices[0].text}")

            if not reply_text:
                reply_text = resp.choices[0].text.strip()
            else:
                # add whitespace for ascii languages
                if reply_text[-1:].isalpha():
                    reply_text += " " + resp.choices[0].text.strip()
                else:
                    reply_text += resp.choices[0].text.strip()
            #await ctx.send(f"{ctx.author.mention} [BOT] {reply_text}")
            
            if not resp.choices[0].finish_reason or resp.choices[0].finish_reason != "length":
                logger.debug(f"Response may end")
                break

            # append text for rest of responses(is necessary?)
            text += resp.choices[0].text
            # increase token length
            token_length += 100
            resp = openai.Completion.create(
                engine="text-davinci-003",
                prompt=text,
                temperature=temp,
                max_tokens=token_length,
    #            stream=False,
    #            stop="\n",
            )
        # send whole text at once from response
        await ctx.send(f"{ctx.author.mention} [BOT] {reply_text}")
        # still need a end mark, it is annoy in twitch chat dialog?
        #await ctx.send(f"{ctx.author.mention} [BOT] 😘")

bot = Bot()
bot.run()



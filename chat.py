import os
import logging
import openai

logger = logging.getLogger(__name__)

openai.api_key = os.environ.get('OPENAI_API_KEY')

class GPTChat(object):
    
    def __init__(self):
        self.temperature = 0.5
        self.token_length = 100
        self.max_length = 200
    
    def setTemp(self, temperature):
        logger.debug(f"temp assign {temperature}")
        if 0.0 <= temperature <= 1.0:
            self.temperature = temperature
        else:
            self.temperature = 0.5 

    def completion(self, text):
        # twitch chat is not fit for long text, restrict reponse in 1 or 2 sentences
        text = text + ",reply in 1 or 2 sentences" #TODO: should language specific?
        
        resp_length = self.token_length
        # let openai API call by async? but completion does not have acreate method
        # or use from asgiref.sync import sync_to_async? [link](https://github.com/openai/openai-python/issues/98)
        resp = openai.Completion.create(
            engine = "text-davinci-003",
            prompt = text,
            temperature = self.temperature,
            max_tokens = resp_length,
#        frequency_penalty=0,
#        presence_penalty=0
#        stream=False,
#        stop="\n",
        )

        reply_text = ""
        # looping for total max length (wide-char language may take more tokens for response)
        while resp_length <= self.max_length:
            logger.debug(resp)
            if not hasattr(resp, 'choices') or len(resp.choices) == 0 or not resp.choices[0].text:
                reply_text = "I got no response"
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

            if not resp.choices[0].finish_reason or resp.choices[0].finish_reason != "length":
                logger.debug(f"Response may end")
                break

            # append text for rest of responses(is necessary?)
            text += resp.choices[0].text
            # increase token length
            resp_length += self.token_length
            resp = openai.Completion.create(
                engine = "text-davinci-003",
                prompt = text,
                temperature = self.temperature,
                max_tokens = resp_length,
#            stream=False,
#            stop="\n",
            )
        # while -end
        return reply_text

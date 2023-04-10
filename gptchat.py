import os
import logging
import openai

logger = logging.getLogger(__name__)

openai.api_key = os.environ.get('OPENAI_API_KEY')

class GPTChat(object):
    """ Open AI chat with limited content length for community service usage """
    def __init__(self):
        self.temperature = 0.5
        self.token_length = 100
        self.max_length = 200
        # we need to let sentence as simple as passible during the twitch chatting
        self.pre_msgs = [
            {"role": "system", "content": "always brief reply in 2 sentences"}
        ]
        # full chatting backlogs for gpt engine 3.5
        self.all_msgs = self.pre_msgs
    
    def setTemp(self, temperature):
        logger.debug(f"temper={temperature}")
        if 0.0 <= temperature <= 1.0:
            self.temperature = temperature
        else:
            self.temperature = 0.5 

    def setTokenLength(self, length):
        self.token_length = length
        self.max_length = length * 2

    def setInitSystem(self, text):
        """For GPT engine 3.5, set the default system content"""
        logger.debug(f"system={text}")
        if not text:
            return
        # be always at the first of pre_msgs
        if len(self.pre_msgs) == 0:
            self.pre_msgs.append({"role": "system", "content": text})
        else:
            self.pre_msgs[0]["content"] = text
        #TODO: replace prev completion whole backlogs or just first 2?
        self.all_msgs = self.pre_msgs

    def setInitAssistant(self, text):
        """For gpt engine 3.5, set a default assistant content"""
        logger.debug(f"assistant={text}")
        if not text:
            return
        # be always at the second of pre_msgs
        if len(self.pre_msgs) == 1:
            self.pre_msgs.append({"role": "assistant", "content": text})
        else:
            self.all_msgs[1]["content"] = text
        #TODO: should we just make a completion see what we got first?
        # re-assign to chatting backlogs
        self.all_msgs = self.pre_msgs

    def chatCompletion(self, text, resp_length):
        """return reply string and continous boolean"""
        # twitch has maximum characters 500
        #resp_length = self.token_length
        # given history backlogs including pre-messages for roles of system and assistant
        msgs = self.all_msgs
        # build a message structure for chat completion API
        if text:
            msg = {"role": "user", "content": text}
            msgs.append(msg)
        #logger.debug(msgs) # will be very long during chatting
        resp = openai.ChatCompletion.create(
            model = "gpt-3.5-turbo",
            messages = msgs,
            temperature = self.temperature,
            max_tokens = resp_length,
            #stop = ["\r", "\n", "\r\n"]
        )

        # check out the response format [link](https://platform.openai.com/docs/api-reference/chat/create)
        reply_text = ""
        logger.debug(f"res: {resp}")
        if not hasattr(resp, 'choices') or len(resp.choices) == 0 or not resp.choices[0].message:
            reply_text = "I got no response"
            return reply_text
        if not resp.choices[0].message.role or not resp.choices[0].message.content or resp.choices[0].message.role != "assistant":
            reply_text = "I got err response"
            return reply_text
        if not resp.choices[0].finish_reason:
            reply_text = "I got err response"
            return reply_text
        
        logger.debug(f"choices: {resp.choices[0].message.content}")

        #TODO: need squash messages avoid huge backlogs?
        #TODO: remove previous non-finished message or just keep it
        self.all_msgs.append(resp.choices[0].message)

        reply_text = resp.choices[0].message.content
        #logger.debug(f"reply: {reply_text}")
        #TODO: merge dict? [{**resp, **resp.choices[0].message}] for py3.5 or later
        reply_objs = [resp]
        
        # recursive call while finish_reason is length
        if resp.choices[0].finish_reason == "length":
            logger.debug("Response not finished, retrieve again")
            (add_text, add_objs) = self.chatCompletion(None, self.max_length)
            # append or replace
            if reply_text.split(" ")[0] == add_text.split(" ")[0]:
                reply_text = add_text
                # return single response for data store
                reply_objs[0] = add_objs[-1]
            else:
                reply_text += add_text
                # return multiple responses for data store
                reply_objs.append(add_objs[-1])
        
        return (reply_text, reply_objs)

    def completion(self, text):
        """text completion using gpt 3 engine"""
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

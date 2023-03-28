
# openai api #

get openai api key from account page, export to env `OPENAI_API_KEY`

following open ai [quickstart](https://beta.openai.com/docs/quickstart)
or just ask the chatgpt...

openai completion will increase token length if got `length` from choices[0].finish_reason until max_tokens, which keeps conversation as simple as passible for community chatbot feature usage.

NOTE: completion response is a object contains choices listing results
- engine davich-003: response text from resp.choices[0].text
- model gpt-3.5-turbo: response text from resp.choices[0].message.content

separate individual method call for different models

model gpt-3.5-turbo given messages and roles from `system`, `assistant` and `user`, to keep context for references

## TODO ##
do gpt 3.5 given messages or backlogs need squash? or store in other forms?


# twtich bot #

visit and register for https://dev.twitch.tw/console

add application with chat bot, set unique id for user auth page display, client id and secret for oauth usage

for authentication, refer https://dev.twitch.tv/docs/irc/authenticate-bot/

since I just test own chat bot, simply use implict flow from example

https://id.twitch.tv/oauth2/authorize?response_type=token&client_id=<client_id>&redirect_uri=http://localhost&scope=channel%3Amoderate+chat%3Aedit+chat%3Aread&state=c3ab8aa609ea11e793ae92361f002671

for scopes, refer to https://dev.twitch.tv/docs/authentication/scopes/


## TODO ## 
further steps, blah blah blah

due to twitch chat room is not suitable for long text, likes chat gpt usually responding detailed reply, function separates context as multiple sentences to send

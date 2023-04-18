# why i do this? #

due to twitch chat room is not suitable for long text, likes chat gpt usually responding detailed reply, function separates context as multiple sentences sending to openai api

been separated chat gpt function in a class, and note that referenced from my another [discord chatbot project](https://github.com/sharowyeh/discord-bot-gpt), but currently have no idea how to do for project depencency

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

- try to manage gpt chat msgs which token exceeded 4096 in a request
- other in source code with TODO: comments

# data storage #

only for running environment in my raspberry in debian and mariadb, asked chatgpt design the docker and yaml files for me.

env => debian:buster + mariadb:10.3.38

refer to `docker-compose.mariadb.yml` for container

refer to `data` folder for mariadb initialization for the container

mariadb connector/c for python requires system packages, [see also](https://mariadb.com/docs/skysql/connect/programming-languages/c/install/#Install_on_Debian,_Ubuntu)

```
> sudo apt-get install libmariadb3 libmariadb-dev
```

## NOTE for raspbian ##

env => raspbian:buster + mariadb:10.3.29

Before install mariadb connector and python pacakge on debian buster,
pkg manager default installed gnueabihf compiled 3.1.20
(or just because I dont want to update index files), 
which not fit for mariadb python package minimal requires 3.3.1

try to get connector/c source code from https://github.com/mariadb-corporation/mariadb-connector-c

find socket the database running at
```
mysqld --verbose --help | grep ^socket
```

```
> git clone https://github.com/MariaDB/mariadb-connector-c.git
> cd mariadb-connector-c
> git checkout v3.3.1
> mkdir build & cd build
> cmake ../ -LH -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr/local -DWITH_SSL=OPENSSL -DDM_DIR=/usr/lib/arm-linux-gnueabihf -DCMAKE_C_FLAGS_RELEASE:STRING="-w" -DMARIADB_UNIX_ADDR=/run/mysqld/mysqld.sock
> cmake --build . --config Release
> make install
```

NOTE: commands above will install compiled libmariadb at /usr/local/mariadb, can simply use following command listing props
```
> mariadb_config --help
```

NOTE: for python load module in runtime, these libs need to add to ld library path manually
```
> sudo vim /etc/ld.so.conf.d/my-mariadb-connector-arm.conf
> # add /lib/local/mariadb in the text file
> sudo ldconfig
```

# twtich bot #

visit and register for https://dev.twitch.tw/console

add application with chat bot, set unique id for user auth page display, client id and secret for oauth usage

for authentication, refer https://dev.twitch.tv/docs/irc/authenticate-bot/

since I just test own chat bot, simply use implict flow from example, paste to browser url

```
https://id.twitch.tv/oauth2/authorize?response_type=token&client_id=<client_id>&redirect_uri=http://localhost&scope=channel%3Amoderate+chat%3Aedit+chat%3Aread&state=c3ab8aa609ea11e793ae92361f002671
```

for scopes, refer to https://dev.twitch.tv/docs/authentication/scopes/


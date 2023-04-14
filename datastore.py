import os
import logging
import mariadb

logger = logging.getLogger(__name__)

DB_CONN_STRING = "localhost:3306"
DB_USER_NAME = "dev"
DB_USER_PASSWORD = "dev"

conn_string = os.environ.get("DB_CONN_STRING", DB_CONN_STRING)
user_name = os.environ.get("DB_USER_NAME", DB_USER_NAME)
user_password = os.environ.get("DB_USER_PASSWORD", DB_USER_PASSWORD)

# For mariadb refer to:
#   https://mariadb-corporation.github.io/mariadb-connector-python/cursor.html
# NOTE: following partial codes were generated from Chat GPT 

class DataStore(object):
    def __init__(self):
        """DAO for chatgpt instance in my mariadb"""
        self.type = "MARIADB"
        # TODO: try to use connection pool
        self.host = conn_string.split(':')[0]
        self.port = int(conn_string.split(':')[1])
        self.user = user_name
        self.password = user_password
        self.database = "chatgpt"

    def connect(self):
        try:
            self.conn = mariadb.connect(
                host = self.host,
                port = self.port,
                user = self.user,
                password = self.password,
                database = self.database
            )
            self.cursor = self.conn.cursor()
        except mariadb.Error as err:
            logger.exception(f"Unexpected {err}, {type(err)}")
            self.cursor = None

    def disconnect(self):
        try:
            self.conn.close()
        except mariadb.Error as err:
            logger.exception(f"Unexpected {err}, {type(err)}")

    def createTopic(self, name: str):
        try:
            self.connect()
            self.cursor.execute(
                "INSERT INTO topics (name, updatetime) VALUES (?, NOW())",
                (name,))
            self.conn.commit()
            # TODO: check if return auto increased id
            id = self.cursor.lastrowid
            logger.debug(f'create topic lastrowid:{self.cursor.lastrowid}')
            self.disconnect()
            return id
        except mariadb.Error as err:
            logger.exception(f"Unexpected {err}, {type(err)}")
        except Exception as e:
            logger.debug(f"Unexpected {e}, {type(e)}")

    def getTopic(self, name: str):
        try:
            self.connect()
            self.cursor.execute(
                "SELECT id, messages, total_tokens, updatetime FROM topics WHERE name = ?",
                (name,))
            result = None
            # also can use cursor.fetchone()
            for (id, messages, total_tokens, updatetime) in self.cursor:
                logger.debug(f'get topic {name}=>{id}, {messages}, {total_tokens}')
                result = (id, messages, total_tokens)
            self.disconnect()
            return result
        except mariadb.Error as err:
            logger.exception(f"Unexpected {err}, {type(err)}")
        except Exception as e:
            logger.debug(f"Unexpected {e}, {type(e)}")

    def updateTopic(self, topic_id, name: str, messages: int, total_tokens: int):
        try:
            self.connect()
            self.cursor.execute(
                "UPDATE topics SET name = ?, messages = ?, total_tokens = ?, updatetime = NOW() WHERE id = ?",
                (name, messages, total_tokens, topic_id,))
            self.conn.commit()
            # TODO: check if return auto increased id
            id = self.cursor.lastrowid
            logger.debug(f'create topic lastrowid:{self.cursor.lastrowid}')
            self.disconnect()
            return id
        except mariadb.Error as err:
            logger.exception(f"Unexpected {err}, {type(err)}")
        except Exception as e:
            logger.debug(f"Unexpected {e}, {type(e)}")

    def deleteTopic(self, topic_id):
        try:
            self.connect()
            self.cursor.execute("DELETE FROM topics WHERE id = ?", (topic_id,))
            self.conn.commit()
            self.disconnect()
        except mariadb.Error as err:
            logger.exception(f"Unexpected {err}, {type(err)}")
        except Exception as e:
            logger.debug(f"Unexpected {e}, {type(e)}")


    def createMessage(self, topic_id, content, role, created, chat_id, model, obj, completion_tokens, prompt_tokens, total_tokens):
        try:
            self.connect()
            self.cursor.execute(
                "INSERT INTO messages (topics_id, content, role, created, chat_id, model, obj, completion_tokens, prompt_tokens, total_tokens) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                (topic_id, content, role, created, chat_id, model, obj, completion_tokens, prompt_tokens, total_tokens,))
            self.conn.commit()
            id = self.cursor.lastrowid
            self.disconnect()
            return id
        except mariadb.Error as err:
            logger.exception(f"Unexpected {err}, {type(err)}")
        except Exception as e:
            logger.debug(f"Unexpected {e}, {type(e)}")
        
    def getMessage(self, message_id):
        try:
            self.connect()
            self.cursor.execute("SELECT * FROM messages WHERE id = ?", (message_id,))
            result = self.cursor.fetchone()
            self.disconnect()
            return result
        
        except mariadb.Error as err:
            logger.exception(f"Unexpected {err}, {type(err)}")
        except Exception as e:
            logger.debug(f"Unexpected {e}, {type(e)}")
        
    def updateMessage(self, message_id, content, role, created, chat_id, model, obj, completion_tokens, prompt_tokens, total_tokens):
        try:
            self.connect()
            self.cursor.execute(
                "UPDATE messages SET content = ?, role = ?, created = ?, chat_id = ?, model = ?, obj = ?, completion_tokens = ?, prompt_tokens = ?, total_tokens = ? WHERE id = ?", 
                (content, role, created, chat_id, model, obj, completion_tokens, prompt_tokens, total_tokens, message_id,))
            self.conn.commit()
            self.disconnect()
        except mariadb.Error as err:
            logger.exception(f"Unexpected {err}, {type(err)}")
        except Exception as e:
            logger.debug(f"Unexpected {e}, {type(e)}")
        
    def deleteMessage(self, message_id):
        try:
            self.connect()
            self.cursor.execute("DELETE FROM messages WHERE id = ?", (message_id,))
            self.conn.commit()
            self.disconnect()
        except mariadb.Error as err:
            logger.exception(f"Unexpected {err}, {type(err)}")
        except Exception as e:
            logger.debug(f"Unexpected {e}, {type(e)}")

    def getMessageCount(self, topic_id):
        """Get message count from given topic TODO: should I miss ORM framework?"""
        try:
            self.connect()
            self.cursor.execute(
                "SELECT COUNT(id) FROM messages WHERE topics_id = ?",
                (topic_id,))
            result = self.cursor.fetchone()
            self.disconnect()
            return result
        except mariadb.Error as err:
            logger.exception(f"Unexpected {err}, {type(err)}")
        except Exception as e:
            logger.debug(f"Unexpected {e}, {type(e)}")

    def updateTopicTokens(self, topic_id):
        """Update topic tokens and messages without really pull out data TODO: or make triggers in DB?"""
        try:
            self.connect()
            # can ask chat gpt for trigger or other efficient version
            self.cursor.execute(
                "UPDATE topics t INNER JOIN ( \
                    SELECT topics_id, COUNT(*) AS msg_count, MAX(total_tokens) as max_tokens \
                    FROM messages m \
                    WHERE topics_id = ? \
                ) m ON m.topics_id = t.id \
                SET t.messages = m.msg_count, t.total_tokens = m.max_tokens",
                (topic_id,))
            self.conn.commit()
            self.disconnect()
        except mariadb.Error as err:
            logger.exception(f"Unexpected {err}, {type(err)}")
        except Exception as e:
            logger.debug(f"Unexpected {e}, {type(e)}")

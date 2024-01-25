import os
import logging
import mariadb

logger = logging.getLogger(__name__)

conn_string = "localhost:3306"
user_name = "dev"
user_password = "dev"

# NOTE: for the maria db in docker env, must run docker compose startup the container
#       use docker-database.sh instead

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

if __name__ == '__main__':
    data = DataStore()
    data.connect()
    if data.conn:
        print(data.conn)

    data.disconnect()

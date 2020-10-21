import sqlite3
import zlib
import time

class SQLiteDB:

    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name, check_same_thread = False)
        self.cursor = self.conn.cursor()

    def new_chat_add(self, chat_id, start = False):
        self.cursor.execute(f"""SELECT checkout FROM chats WHERE chat_id = '{chat_id}'""")
        result = self.cursor.fetchall()
        if result:
            if result[0][0] == 1:
                return
            elif result[0][0] == 0 and start == True:
                self.enable_bot(chat_id)
        else:
            self.cursor.execute(f"""INSERT INTO chats
                    VALUES ('{chat_id}', 1)""")
            self.conn.commit()
                
    def new_url_add(self, chat_id, url):
        self.cursor.execute(f"""SELECT * FROM urls WHERE chat_id = '{chat_id}' and url = '{url}'""")
        result = self.cursor.fetchall()
        if result:
            return 1
        else:
            hash_id = hex(zlib.crc32(str.encode(str(chat_id)+url)) & 0xffffffff)
            print(hash_id)
            self.cursor.execute(f"""INSERT INTO urls
                    VALUES ('{chat_id}', '{url}', 1, '{hash_id}')""")
            self.conn.commit()

    def delete_url(self, id):
        self.cursor.execute(f"""DELETE FROM urls WHERE id = '{id}' """)
        self.conn.commit()


    def disable_bot(self, chat_id):
        print(chat_id)
        self.cursor.execute(f"""UPDATE chats
            set checkout = 0 WHERE chat_id = '{chat_id}'""")
        self.conn.commit()

    def enable_bot(self, chat_id):
        self.cursor.execute(f"""UPDATE chats 
                   set checkout = 1 WHERE chat_id = '{chat_id}'""")
        self.conn.commit()
    
    def check_bot(self, chat_id):
        self.cursor.execute(f"""SELECT checkout FROM chats WHERE chat_id = '{chat_id}'""")
        result = self.cursor.fetchall()
        if result:
            if result[0][0] == 1:
                return True
            elif result[0][0] == 0:
                return False    


    def get_urls(self, chat_id):
        self.cursor.execute(f"""SELECT url FROM urls WHERE chat_id = '{chat_id}' and checkout = 1""")
        result = self.cursor.fetchall()
        urls = []
        for url in result:
            urls.append(url[0])
        return urls

    def get_url_hash(self, chat_id, url):
        self.cursor.execute(f"""SELECT id FROM urls WHERE chat_id = '{chat_id}' and url = '{url}' """)
        result = self.cursor.fetchall()
        if result[0][0]:
            return result[0][0]
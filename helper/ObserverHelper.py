import json
from helper.KakaoDecrypt import KakaoDecrypt
import requests

class ObserverHelper:
    def __init__(self,config):
        self.last_log_id = 0
        self.config = get_config()
        self.BOT_ID = self.config["bot_id"]
        self.BOT_NAME = self.config["bot_name"]

    def is_command(self, msg):
        commands = get_config()["commands"]
        if msg.split(' ')[0] in commands:
            return True
        else:
            return False

    def make_post_data(self, dec_msg, room, sender, js):
        data = {"msg" : dec_msg,
                "room" : room,
                "sender" : sender,
                "json" : js
                }
        return json.dumps(data)
    
    def check_change(self, db):
        if self.last_log_id == 0:
            limit = 1
        else:
            limit = 5
        db.cur.execute(f'select * from chat_logs order by id desc limit ?',[limit])
        description = [desc[0] for desc in db.cur.description]
        res = db.cur.fetchall()
        res.reverse()
        for row in res:
            if row[0] > self.last_log_id:
                self.last_log_id = row[0]
                v = json.loads(row[13])
                enc = v["enc"]
                origin = v["origin"]
                enc_msg = row[5]
                user_id = row[4]
                dec_msg = KakaoDecrypt.decrypt(enc,enc_msg,user_id)
                if self.is_command(dec_msg):
                    chat_id = row[3]
                    user_info = db.get_user_info(chat_id,user_id)
                    room = user_info[0]
                    sender = user_info[1]
                    if room == self.BOT_NAME:
                        room = sender
                    post_data = self.make_post_data(dec_msg, room, sender, {description[i]:row[i] for i in range(len(row))})
                    requests.post("http://127.0.0.1:5000/db",data={"data":post_data})
                    print('sent')

def get_config():
    with open('config.json','r') as fo:
        config = json.loads(fo.read())
    return config
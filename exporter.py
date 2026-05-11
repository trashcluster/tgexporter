import os
import logging
from telegram.client import Telegram
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from models import Base, User, Chat, Message, SyncState, chat_members
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TGExporter:
    def __init__(self, api_id, api_hash, phone, db_url):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        
        self.tg = Telegram(
            api_id=api_id,
            api_hash=api_hash,
            phone=phone,
            database_encryption_key='changeme123',
            files_directory='/app/session/',
            tdlib_verbosity=0
        )

    def auth(self):
        # This will prompt for code/2FA in the terminal on first run
        self.tg.login()
        logger.info("Successfully authenticated.")

    def sync_chats(self):
        db = self.Session()
        r = self.tg.get_chats()
        r.wait()
        
        for chat_id in r.update['chat_ids']:
            chat_data = self.tg.get_chat(chat_id)
            chat_data.wait()
            c = chat_data.update
            
            chat_type = c['type']['@type']
            db_chat = db.query(Chat).filter(Chat.id == chat_id).first()
            if not db_chat:
                db_chat = Chat(id=chat_id, title=c.get('title', 'Private'), type=chat_type)
                db.add(db_chat)
            
            self.sync_messages(db, chat_id)
        
        db.commit()
        db.close()

    def sync_messages(self, db, chat_id):
        # Delta Logic: Get last stored message ID
        state = db.query(SyncState).filter(SyncState.chat_id == chat_id).first()
        last_id = state.last_message_id if state else 0
        
        logger.info(f"Syncing chat {chat_id} from message {last_id}")
        
        from_msg_id = 0 # 0 means from the latest
        finished = False
        new_last_id = None

        while not finished:
            history = self.tg.get_chat_history(chat_id=chat_id, from_message_id=from_msg_id, limit=100)
            history.wait()
            messages = history.update.get('messages', [])
            
            if not messages:
                break
                
            for msg in messages:
                if msg['id'] <= last_id:
                    finished = True
                    break
                
                if new_last_id is None:
                    new_last_id = msg['id']

                self._process_message(db, chat_id, msg)
            
            if len(messages) < 100:
                finished = True
            else:
                from_msg_id = messages[-1]['id']

        if new_last_id:
            if not state:
                state = SyncState(chat_id=chat_id, last_message_id=new_last_id)
                db.add(state)
            else:
                state.last_message_id = new_last_id

    def _process_message(self, db, chat_id, msg):
        sender_id = msg.get('sender_id', {}).get('user_id', 0)
        if sender_id == 0: return # Skip channel posts or anonymous

        # Handle User
        user = db.query(User).filter(User.id == sender_id).first()
        if not user:
            user_info = self.tg.get_user(sender_id)
            user_info.wait()
            u = user_info.update
            user = User(
                id=sender_id, 
                first_name=u.get('first_name'), 
                last_name=u.get('last_name'),
                username=u.get('username')
            )
            db.add(user)
            db.flush()

        # Handle Membership mapping
        membership_exists = db.query(chat_members).filter_by(user_id=sender_id, chat_id=chat_id).first()
        if not membership_exists:
            db.execute(chat_members.insert().values(user_id=sender_id, chat_id=chat_id))

        # Handle Message
        content = msg.get('content', {})
        content_type = content.get('@type', 'unknown')
        text = ""
        file_id = None

        if content_type == 'messageText':
            text = content['text']['text']
        elif content_type == 'messagePhoto':
            file_id = content['photo']['sizes'][-1]['photo']['id']
            text = content.get('caption', {}).get('text', '')
        # ... handle other types similarly ...

        db_msg = Message(
            id=msg['id'],
            chat_id=chat_id,
            sender_id=sender_id,
            date=datetime.fromtimestamp(msg['date']),
            content_type=content_type,
            text=text,
            file_id=file_id
        )
        db.add(db_msg)

    def download_pending_media(self):
        # Implementation would query Message where file_id is not null and is_downloaded is False
        # Then call self.tg.download_file(file_id)
        pass

    def run(self):
        self.auth()
        self.sync_chats()
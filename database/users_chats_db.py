import motor.motor_asyncio
import logging
from info import (
    DATABASE_NAME, DATABASE_URL, IMDB, IMDB_TEMPLATE, MELCOW_NEW_USERS,
    P_TTI_SHOW_OFF, SINGLE_BUTTON, SPELL_CHECK_REPLY, PROTECT_CONTENT,
    MAX_RIST_BTNS, IMDB_DELET_TIME
)

logger = logging.getLogger(name)
logger.setLevel(logging.INFO)

class Database:
    def init(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.users_collection = self.db.users
        self.groups_collection = self.db.groups

    @staticmethod
    def new_user(user_id, name):
        return {
            'id': user_id,
            'name': name,
            'ban_status': {
                'is_banned': False,
                'ban_reason': "",
            },
        }

    @staticmethod
    def new_group(group_id, title, username):
        return {
            'id': group_id,
            'title': title,
            'username': username,
            'chat_status': {
                'is_disabled': False,
                'reason': "",
            },
        }

    async def add_user(self, user_id, name):
        user = self.new_user(user_id, name)
        try:
            await self.users_collection.insert_one(user)
        except Exception as e:
            logger.exception(f"Failed to add user {user_id}: {e}")

    async def is_user_exist(self, user_id):
        return await self.users_collection.find_one({'id': int(user_id)}) is not None

    async def total_users_count(self):
        return await self.users_collection.count_documents({})

    async def remove_ban(self, user_id):
        ban_status = {'is_banned': False, 'ban_reason': ''}
        await self.users_collection.update_one({'id': user_id}, {'$set': {'ban_status': ban_status}})

    async def ban_user(self, user_id, ban_reason="No Reason"):
        ban_status = {'is_banned': True, 'ban_reason': ban_reason}
        await self.users_collection.update_one({'id': user_id}, {'$set': {'ban_status': ban_status}})

    async def get_ban_status(self, user_id):
        default = {'is_banned': False, 'ban_reason': ''}
        user = await self.users_collection.find_one({'id': int(user_id)})
        return user.get('ban_status', default) if user else default

    async def get_all_users(self):
        return self.users_collection.find({})

    async def delete_user(self, user_id):
        await self.users_collection.delete_many({'id': int(user_id)})

    async def delete_chat(self, chat_id):
        await self.groups_collection.delete_many({'id': int(chat_id)})

    async def get_banned(self):
        banned_users = self.users_collection.find({'ban_status.is_banned': True})
        disabled_chats = self.groups_collection.find({'chat_status.is_disabled': True})

        b_chats = [chat['id'] async for chat in disabled_chats]
        b_users = [user['id'] async for user in banned_users]

        return b_users, b_chats

    async def add_chat(self, chat_id, title, username):
        group = self.new_group(chat_id, title, username)
        try:
            await self.groups_collection.insert_one(group)
        except Exception as e:
            logger.exception(f"Failed to add chat {chat_id}: {e}")

    async def get_chat(self, chat_id):
        chat = await self.groups_collection.find_one({'id': int(chat_id)})
        return chat.get('chat_status') if chat else False

    async def re_enable_chat(self, chat_id):
        chat_status = {'is_disabled': False, 'reason': ""}
        await self.groups_collection.update_one({'id': int(chat_id)}, {'$set': {'chat_status': chat_status}})

    async def update_settings(self, chat_id, settings):
        await self.groups_collection.update_one({'id': int(chat_id)}, {'$set': {'settings': settings}})
        async def get_settings(self, chat_id):
        default_settings = {
            'button': SINGLE_BUTTON,
            'botpm': P_TTI_SHOW_OFF,
            'file_secure': PROTECT_CONTENT,
            'imdb': IMDB,
            'spell_check': SPELL_CHECK_REPLY,
            'welcome': MELCOW_NEW_USERS,
            'template': IMDB_TEMPLATE            
        }
        chat = await self.groups_collection.find_one({'id': int(chat_id)})
        return chat.get('settings', default_settings) if chat else default_settings

    async def disable_chat(self, chat_id, reason="No Reason"):
        chat_status = {'is_disabled': True, 'reason': reason}
        await self.groups_collection.update_one({'id': int(chat_id)}, {'$set': {'chat_status': chat_status}})

    async def total_chat_count(self):
        return await self.groups_collection.count_documents({})

    async def get_all_chats(self):
        return self.groups_collection.find({})

    async def get_db_size(self):
        stats = await self.db.command("dbstats")
        return stats['dataSize']

# Initialize the database instance
db = Database(DATABASE_URL, DATABASE_NAME)

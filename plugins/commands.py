import os, re, json, base64, logging, random, asyncio

from Script import script
from database.users_chats_db import db
from pyrogram import Client, filters, enums
from pyrogram.errors import ChatAdminRequired, FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.ia_filterdb import Media, get_file_details, unpack_new_file_id
from info import CHANNELS, ADMINS, AUTH_CHANNEL, LOG_CHANNEL, PICS, BATCH_FILE_CAPTION, CUSTOM_FILE_CAPTION, PROTECT_CONTENT, START_MESSAGE, FORCE_SUB_TEXT, SUPPORT_CHAT
from utils import get_settings, get_size, is_subscribed, save_group_settings, temp
from database.connections_mdb import active_connection

logger = logging.getLogger(name)
BATCH_FILES = {}

@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    bot_name = "SPYDER BOT"  # Updated bot name
    start_message = START_MESSAGE.format(user=message.from_user.mention if message.from_user else message.chat.title, bot=bot_name)
    
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        buttons = [[           
            InlineKeyboardButton('📢 Uᴩᴅᴀᴛᴇꜱ 📢', url=f'https://t.me/{SUPPORT_CHAT}')
            ],[
            InlineKeyboardButton('ℹ️ Hᴇʟᴩ ℹ️', url=f"https://t.me/{temp.U_NAME}?start=help")
        ]]
        await message.reply(start_message, reply_markup=InlineKeyboardMarkup(buttons), disable_web_page_preview=True)                    
        await asyncio.sleep(2) 
        if not await db.get_chat(message.chat.id):
            total = await client.get_chat_members_count(message.chat.id)
            await client.send_message(LOG_CHANNEL, script.LOG_TEXT_G.format(a=message.chat.title, b=message.chat.id, c=message.chat.username, d=total, f=bot_name, e="Unknown"))       
            await db.add_chat(message.chat.id, message.chat.title, message.chat.username)
        return 
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(message.from_user.id, message.from_user.mention, message.from_user.username, temp.U_NAME))
    if len(message.command) != 2:
        buttons = [[
            InlineKeyboardButton("➕ Aᴅᴅ Mᴇ Tᴏ Yᴏᴜʀ Cʜᴀᴛ ➕", url=f"http://t.me/{temp.U_NAME}?startgroup=true")
            ],[
            InlineKeyboardButton("Sᴇᴀʀᴄʜ 🔎", switch_inline_query_current_chat=''), 
            InlineKeyboardButton("Cʜᴀɴɴᴇʟ 🔈", url="https://t.me/mkn_bots_updates")
            ],[      
            InlineKeyboardButton("Hᴇʟᴩ 🕸", callback_data="help"),
            InlineKeyboardButton("Aʙᴏᴜᴛ ✨", callback_data="about")
        ]]
        m = await message.reply_sticker("CAACAgUAAxkBAAEBvlVk7YKnYxIHVnKW2PUwoibIR2ygGAACBAADwSQxMYnlHW4Ls8gQHgQ") 
        await asyncio.sleep(2)
        await message.reply_photo(photo=random.choice(PICS), caption=start_message, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)
        return await m.delete()
        
    if AUTH_CHANNEL and not await is_subscribed(client, message):
        try:
            invite_link = await client.create_chat_invite_link(int(AUTH_CHANNEL))
        except ChatAdminRequired:
            logger.error("MAKE SURE BOT IS ADMIN IN FORCESUB CHANNEL")
            return
        btn = [[InlineKeyboardButton("Jᴏɪɴ Mʏ Cʜᴀɴɴᴇʟ ✨", url=invite_link.invite_link)]]
        if message.command[1] != "subscribe":
            try:
                kk, file_id = message.command[1].split("_", 1)
                pre = 'checksubp' if kk == 'filep' else 'checksub' 
                btn.append([InlineKeyboardButton("⟳ Tʀʏ Aɢᴀɪɴ", callback_data=f"{pre}#{file_id}")])
            except (IndexError, ValueError):

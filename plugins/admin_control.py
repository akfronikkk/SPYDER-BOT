from pyrogram import Client, filters, enums
from pyrogram.errors import ChatAdminRequired
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong, PeerIdInvalid, UserNotParticipant, MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty

from info import ADMINS, LOG_CHANNEL, SUPPORT_CHAT, WELCOM_PIC, WELCOM_TEXT, IMDB_TEMPLATE
from utils import get_size, temp, extract_user, get_file_id, get_poster, humanbytes
from database.users_chats_db import db
from database.ia_filterdb import Media
from datetime import datetime
from Script import script
import logging, re, asyncio, time, shutil, psutil, os, sys

logger = logging.getLogger(name)
logger.setLevel(logging.ERROR)

@Client.on_message(filters.new_chat_members & filters.group)
async def savegroup_and_welcome(bot, message):
    r_j_check = [u.id for u in message.new_chat_members]
    if bot.id in r_j_check:
        if not await db.get_chat(message.chat.id):
            total = await bot.get_chat_members_count(message.chat.id)
            r_j = message.from_user.mention if message.from_user else "Anonymous"
            await bot.send_message(LOG_CHANNEL, script.LOG_TEXT_G.format(a=message.chat.title, b=message.chat.id, c=message.chat.username, d=total, e=r_j, f=bot.mention))       
            await db.add_chat(message.chat.id, message.chat.title, message.chat.username)
        if message.chat.id in temp.BANNED_CHATS:
            buttons = [[InlineKeyboardButton('Support', url=f'https://t.me/{SUPPORT_CHAT}')]]
            k = await message.reply("CHAT NOT ALLOWED 🐞\n\nMy admins have restricted me from working here! If you want to know more about it, contact support.", reply_markup=InlineKeyboardMarkup(buttons))
            try:
                await k.pin()
            except:
                pass
            return await bot.leave_chat(message.chat.id)
           
        buttons = [[InlineKeyboardButton('Help', url=f"https://t.me/{temp.U_NAME}?start=help")]]
        await message.reply(text="❤️ Thanks for adding me to your group.\n» Don't forget to make me an admin.\n» If you have any doubts about using me, click the button below...✨", reply_markup=InlineKeyboardMarkup(buttons))
    else:
        for u in message.new_chat_members:
            if (temp.MELCOW).get('welcome') is not None:
                try:
                    await (temp.MELCOW['welcome']).delete()
                except:
                    pass
            if WELCOM_PIC:
                temp.MELCOW['welcome'] = await message.reply_photo(photo=WELCOM_PIC, caption=WELCOM_TEXT.format(user=u.mention, chat=message.chat.title))
            else:
                temp.MELCOW['welcome'] = await message.reply_text(text=WELCOM_TEXT.format(user=u.mention, chat=message.chat.title))

@Client.on_message(filters.command('leave') & filters.user(ADMINS))
async def leave_a_chat(bot, message):
    if len(message.command) == 1:
        return await message.reply('Please provide a chat ID.')
    chat = message.command[1]
    try:
        chat = int(chat)
    except:
        chat = chat
    try:
        buttons = [[InlineKeyboardButton('Support', url=f'https://t.me/{SUPPORT_CHAT}')]]
        await bot.send_message(chat_id=chat, text='<b>Hello Friends, \nMy admin has told me to leave from this group so I go! If you want to add me again, contact my support group.</b>', reply_markup=InlineKeyboardMarkup(buttons))
        await bot.leave_chat(chat)
    except Exception as e:
        await message.reply(f'Error: {e}')

@Client.on_message(filters.command('disable') & filters.user(ADMINS))
async def disable_chat(bot, message):
    if len(message.command) == 1:
        return await message.reply('Please provide a chat ID.')
        r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = "No Reason Provided"
    try:
        chat_ = int(chat)
    except:
        return await message.reply('Please provide a valid chat ID.')
    cha_t = await db.get_chat(int(chat_))
    if not cha_t:
        return await message.reply("Chat not found in DB.")
    if cha_t['is_disabled']:
        return await message.reply(f"This chat is already disabled:\nReason: <code>{cha_t['reason']}</code>")
    await db.disable_chat(int(chat_), reason)
    temp.BANNED_CHATS.append(int(chat_))
    await message.reply('Chat successfully disabled.')
    try:
        buttons = [[InlineKeyboardButton('Support', url=f'https://t.me/{SUPPORT_CHAT}')]]
        await bot.send_message(chat_id=chat_, text=f'<b>Hello Friends, \nMy admin has told me to leave from this group so I go! If you want to add me again, contact my support group.</b>\nReason: <code>{reason}</code>', reply_markup=InlineKeyboardMarkup(buttons))
        await bot.leave_chat(chat_)
    except Exception as e:
        await message.reply(f'Error: {e}')

@Client.on_message(filters.command('enable') & filters.user(ADMINS))
async def re_enable_chat(bot, message):
    if len(message.command) == 1:
        return await message.reply('Please provide a chat ID.')
    chat = message.command[1]
    try:
        chat_ = int(chat)
    except:
        return await message.reply('Please provide a valid chat ID.')
    sts = await db.get_chat(int(chat))
    if not sts:
        return await message.reply("Chat not found in DB.")
    if not sts.get('is_disabled'):
        return await message.reply('This chat is not yet disabled.')
    await db.re_enable_chat(int(chat_))
    temp.BANNED_CHATS.remove(int(chat_))
    await message.reply("Chat successfully re-enabled.")

@Client.on_message(filters.command('stats') & filters.incoming)
async def get_ststs(bot, message):
    rju = await message.reply('<b>Please wait...</b>')
    total_users = await db.total_users_count()
    totl_chats = await db.total_chat_count()
    files = await Media.count_documents()
    size = await db.get_db_size()
    free = 536870912 - size
    size = get_size(size)
    free = get_size(free)
    await rju.edit(script.STATUS_TXT.format(files, total_users, totl_chats, size, free))

@Client.on_message(filters.command('invite') & filters.user(ADMINS))
async def gen_invite(bot, message):
    if len(message.command) == 1:
        return await message.reply('Please provide a chat ID.')
    chat = message.command[1]
    try:
        chat = int(chat)
    except:
        return await message.reply('Please provide a valid chat ID.')
    try:
        link = await bot.create_chat_invite_link(chat)
    except ChatAdminRequired:
        return await message.reply("Invite link generation failed, I do not have sufficient rights.")
    except Exception as e:
        return await message.reply(f'Error: {e}')
    await message.reply(f'Here is your invite link: {link.invite_link}')

@Client.on_message(filters.command('ban_user') & filters.user(ADMINS))
async def ban_a_user(bot, message):
    if len(message.command) == 1:
        return await message.reply('Please provide a user ID / username.')
    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = "No reason Provided"
    try:
        chat = int(chat)
    except:
        pass
    try:
        k = await bot.get_users(chat)
    except PeerIdInvalid:
        return await message.reply("This is an invalid user, make sure I have met them before.")
    except IndexError:
        return await message.reply("This might be a channel, make sure it's a user.")
    except Exception as e:
        return await message.reply(f'Error: {e}')
    else:
        jar = await db.get_ban_status(k.id)
        if jar['is_banned']:
            return await message.reply(f"{k.mention} is already banned.\nReason: {jar['ban_reason']}")
        await db.ban_user(k.id, reason)
        temp.BANNED_USERS.append(k.id)
        await message.reply(f"Successfully banned {k.mention}")

@Client.on_message(filters.command('unban_user') & filters.user(ADMINS))
async def unban_a_user(bot, message):
    if len(message.command) == 1:
        return await message.reply('Please provide a user ID / username.')
    r

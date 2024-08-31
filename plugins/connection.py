from pyrogram import filters, Client, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.connections_mdb import add_connection, all_connections, if_active, delete_connection
from info import ADMINS
import logging

logger = logging.getLogger(name)
logger.setLevel(logging.WARNING)  # Adjust the logging level as needed

@Client.on_message((filters.private | filters.group) & filters.command('connect'))
async def addconnection(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply("You are an anonymous admin. Use /connect {message.chat.id} in PM")

    chat_type = message.chat.type
    if chat_type == enums.ChatType.PRIVATE:
        try:
            cmd, group_id = message.text.split(" ", 1)
        except ValueError:
            await message.reply_text(
                "<b>Enter in correct format!</b>\n\n"
                "<code>/connect groupid</code>\n\n"
                "<i>Get your Group id by adding this bot to your group and use <code>/id</code></i>",
                quote=True
            )
            return
    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        group_id = message.chat.id

    try:
        st = await client.get_chat_member(group_id, userid)
        if (
                st.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]
                and userid not in ADMINS
        ):
            return await message.reply_text("You should be an admin in the given group!", quote=True)
    except Exception as e:
        logger.exception("Failed to get chat member status: %s", e)
        return await message.reply_text("Invalid Group ID!\n\nIf correct, make sure I'm present in your group!", quote=True)

    try:
        st = await client.get_chat_member(group_id, "me")
        if st.status == enums.ChatMemberStatus.ADMINISTRATOR:
            ttl = await client.get_chat(group_id)
            title = ttl.title

            if await add_connection(str(group_id), str(userid)):
                await message.reply_text(
                    f"Successfully connected to {title}\nNow manage your group from my PM!",
                    quote=True,
                    parse_mode=enums.ParseMode.MARKDOWN
                )
                if chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
                    await client.send_message(
                        userid,
                        f"Connected to {title}!",
                        parse_mode=enums.ParseMode.MARKDOWN
                    )
            else:
                await message.reply_text("You're already connected to this chat!", quote=True)
        else:
            await message.reply_text("Add me as an admin in the group", quote=True)
    except Exception as e:
        logger.exception("Failed to connect group: %s", e)
        await message.reply_text('Some error occurred! Try again later.', quote=True)


@Client.on_message((filters.private | filters.group) & filters.command('disconnect'))
async def deleteconnection(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply("You are an anonymous admin. Use /connect {message.chat.id} in PM")

    chat_type = message.chat.type
    if chat_type == enums.ChatType.PRIVATE:
        await message.reply_text("Run /connections to view or disconnect from groups!", quote=True)
    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        group_id = message.chat.id

        try:
            st = await client.get_chat_member(group_id, userid)
            if (
                    st.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]
                    and str(userid) not in ADMINS
            ):
                return
        except Exception as e:
            logger.exception("Failed to get chat member status: %s", e)
            return
            if await delete_connection(str(userid), str(group_id)):
            await message.reply_text("Successfully disconnected from this chat", quote=True)
        else:
            await message.reply_text("This chat isn't connected to me!\nDo /connect to connect.", quote=True)


@Client.on_message(filters.private & filters.command(["connections"]))
async def connections(client, message):
    userid = message.from_user.id
    groupids = await all_connections(str(userid))
    if groupids is None:
        return await message.reply_text("There are no active connections!! Connect to some groups first.", quote=True)

    buttons = []
    for groupid in groupids:
        try:
            ttl = await client.get_chat(int(groupid))
            title = ttl.title
            active = await if_active(str(userid), str(groupid))
            act = " - ACTIVE" if active else ""
            buttons.append([InlineKeyboardButton(f"{title}{act}", callback_data=f"groupcb:{groupid}:{act}")])
        except Exception as e:
            logger.exception("Failed to get chat details: %s", e)
            continue

    if buttons:
        await message.reply_text("Your connected group details:\n\n", reply_markup=InlineKeyboardMarkup(buttons), quote=True)
    else:
        await message.reply_text("There are no active connections!! Connect to some groups first.", quote=True)
        

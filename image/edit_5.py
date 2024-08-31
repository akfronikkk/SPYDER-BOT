from pyrogram.enums import ChatAction
import asyncio
import shutil
import os


async def process_image(client, message, glitch_type):
    try:
        userid = str(message.chat.id)
        user_dir = f"./DOWNLOADS/{userid}"
        if not os.path.isdir(user_dir):
            os.makedirs(user_dir)
        
        download_location = os.path.join(user_dir, f"{userid}.jpg")
        edit_img_loc = os.path.join(user_dir, f"{glitch_type}.jpg")
        
        if not message.reply_to_message.empty:
            msg = await message.reply_to_message.reply_text(
                "<b>𝙳𝙾𝚆𝙽𝙻𝙾𝙰𝙳𝙸𝙽𝙶 𝙸𝙼𝙰𝙶𝙴....</b>", quote=True
            )
            await client.download_media(
                message=message.reply_to_message, file_name=download_location
            )
            await msg.edit("<b>𝚄𝙿𝙻𝙾𝙰𝙳𝙸𝙽𝙶 𝙸𝙼𝙰𝙶𝙴....</b>")
            
            cd = ["glitch_this", "-c", "-o", edit_img_loc, download_location, glitch_type]
            process = await asyncio.create_subprocess_exec(
                *cd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
            
            await message.reply_chat_action(ChatAction.UPLOAD_PHOTO)
            await message.reply_to_message.reply_photo(edit_img_loc, quote=True)
            await msg.delete()
        else:
            await message.reply_text("Why did you delete that??")
        
        try:
            shutil.rmtree(user_dir)
        except Exception:
            pass

    except Exception as e:
        print(f"{glitch_type}-error - " + str(e))
        if "USER_IS_BLOCKED" in str(e):
            return
        try:
            await message.reply_to_message.reply_text(
                "Something went wrong!", quote=True
            )
        except Exception:
            return


async def normalglitch_1(client, message):
    await process_image(client, message, "normalglitch_1")


async def normalglitch_2(client, message):
    await process_image(client, message, "normalglitch_2")


async def normalglitch_3(client, message):
    await process_image(client, message, "normalglitch_3")


async def normalglitch_4(client, message):
    await process_image(client, message, "normalglitch_4")


async def normalglitch_5(client, message):
    await process_image(client, message, "normalglitch_5")


async def scanlineglitch_1(client, message):
    await process_image(client, message, "scanlineglitch_1")


async def scanlineglitch_2(client, message):
    await process_image(client, message, "scanlineglitch_2")


async def scanlineglitch_3(client, message):
    await process_image(client, message, "scanlineglitch_3")


async def scanlineglitch_4(client, message):
    await process_image(client, message, "scanlineglitch_4")


async def scanlineglitch_5(client, message):
    await process_image(client, message, "scanlineglitch_5")

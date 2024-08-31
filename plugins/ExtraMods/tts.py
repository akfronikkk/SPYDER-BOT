import traceback
from asyncio import get_running_loop
from io import BytesIO
from googletrans import Translator
from gtts import gTTS
from pyrogram import Client, filters
from pyrogram.types import Message

def convert(text):
    audio = BytesIO()
    translator = Translator()
    translated = translator.translate(text, dest="en")
    lang = translated.src
    tts = gTTS(translated.text, lang=lang)
    tts.write_to_fp(audio)
    audio.seek(0)  # Reset the buffer to the beginning
    return audio

@Client.on_message(filters.command("tts"))
async def text_to_speech(client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to some text, please.")
    if not message.reply_to_message.text:
        return await message.reply_text("Reply to a text message, please.")
    m = await message.reply_text("Processing...")
    text = message.reply_to_message.text
    try:
        loop = get_running_loop()
        audio = await loop.run_in_executor(None, convert, text)
        await message.reply_audio(audio)
        await m.delete()
        audio.close()
    except Exception as e:
        await m.edit(f"Error: {e}")
        traceback.print_exc()

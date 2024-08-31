from pyrogram import Client, filters
from pyrogram.types import Message
from PIL import Image
import pytesseract
import io

async def extract_text_command(client: Client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.photo:
        return await message.reply_text("Please reply to a photo to extract text from it.")

    photo = message.reply_to_message.photo
    file = await client.download_media(photo.file_id)
    
    # Load the image and extract text
    with Image.open(file) as img:
        text = pytesseract.image_to_string(img)

    # Clean up the downloaded file
    os.remove(file)
    
    if text:
        await message.reply_text(f"Extracted text:\n{text}")
    else:
        await message.reply_text("No text could be extracted from the image.")

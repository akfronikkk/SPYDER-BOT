import motor.motor_asyncio
from pyrogram import enums
from info import DATABASE_URL, DATABASE_NAME
import logging

# Set up logging
logger = logging.getLogger(name)
logger.setLevel(logging.ERROR)

# Initialize Motor client and database
client = motor.motor_asyncio.AsyncIOMotorClient(DATABASE_URL)
db = client[DATABASE_NAME]

async def add_gfilter(gfilters, text, reply_text, btn, file, alert):
    mycol = db[str(gfilters)]
    data = {
        'text': str(text),
        'reply': str(reply_text),
        'btn': str(btn),
        'file': str(file),
        'alert': str(alert)
    }
    try:
        await mycol.update_one({'text': str(text)}, {"$set": data}, upsert=True)
    except Exception as e:
        logger.exception('Error adding or updating global filter', exc_info=True)

async def find_gfilter(gfilters, name):
    mycol = db[str(gfilters)]

    try:
        query = mycol.find({'text': name})
        results = []
        async for file in query:
            reply_text = file.get('reply')
            btn = file.get('btn')
            fileid = file.get('file')
            alert = file.get('alert', None)
            results.append((reply_text, btn, alert, fileid))
        if results:
            return results
        return None, None, None, None
    except Exception as e:
        logger.exception('Error finding global filter', exc_info=True)
        return None, None, None, None

async def get_gfilters(gfilters):
    mycol = db[str(gfilters)]

    texts = []
    try:
        async for file in mycol.find():
            text = file.get('text')
            texts.append(text)
    except Exception as e:
        logger.exception('Error retrieving global filters', exc_info=True)
    return texts

async def delete_gfilter(message, text, gfilters):
    mycol = db[str(gfilters)]

    try:
        result = await mycol.delete_many({'text': text})
        if result.deleted_count > 0:
            await message.reply_text(
                f"'{text}' deleted. I'll not respond to that global filter anymore.",
                quote=True,
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await message.reply_text("Couldn't find that global filter!", quote=True)
    except Exception as e:
        logger.exception('Error deleting global filter', exc_info=True)
        await message.reply_text("An error occurred while deleting the global filter.", quote=True)

async def del_allg(message, gfilters):
    if str(gfilters) not in await db.list_collection_names():
        await message.edit_text("Nothing to remove!")
        return

    mycol = db[str(gfilters)]
    try:
        await mycol.drop()
        await message.edit_text(f"All global filters have been removed")
    except Exception as e:
        logger.exception('Error removing all global filters', exc_info=True)
        await message.edit_text("Couldn't remove all global filters!")

async def count_gfilters(gfilters):
    mycol = db[str(gfilters)]

    try:
        count = await mycol.count_documents({})
        return count if count > 0 else False
    except Exception as e:
        logger.exception('Error counting global filters', exc_info=True)
        return False

async def gfilter_stats():
    collections = await db.list_collection_names()

    if "CONNECTION" in collections:
        collections.remove("CONNECTION")

    totalcount = 0
    for collection in collections:
        mycol = db[collection]
        try:
            count = await mycol.count_documents({})
            totalcount += count
        except Exception as e:
            logger.exception(f'Error counting documents in collection {collection}', exc_info=True)

    totalcollections = len(collections)

    return totalcollections, totalcount

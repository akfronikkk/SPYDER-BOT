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

async def add_filter(grp_id, text, reply_text, btn, file, alert):
    mycol = db[str(grp_id)]

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
        logger.exception('Error adding or updating filter', exc_info=True)

async def find_filter(group_id, name):
    mycol = db[str(group_id)]

    try:
        query = mycol.find({'text': name})
        results = []
        async for file in query:
            reply_text = file.get('reply')
            btn = file.get('btn')
            fileid = file.get('file')
            alert = file.get('alert')
            results.append((reply_text, btn, alert, fileid))
        if results:
            return results
        return None, None, None, None
    except Exception as e:
        logger.exception('Error finding filters', exc_info=True)
        return None, None, None, None

async def get_filters(group_id):
    mycol = db[str(group_id)]

    texts = []
    try:
        async for file in mycol.find():
            text = file.get('text')
            texts.append(text)
    except Exception as e:
        logger.exception('Error retrieving filters', exc_info=True)
    return texts

async def delete_filter(message, text, group_id):
    mycol = db[str(group_id)]

    try:
        result = await mycol.delete_many({'text': text})
        if result.deleted_count > 0:
            await message.reply_text(
                f"'{text}' deleted. I'll not respond to that filter anymore.",
                quote=True,
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await message.reply_text("Couldn't find that filter!", quote=True)
    except Exception as e:
        logger.exception('Error deleting filter', exc_info=True)
        await message.reply_text("An error occurred while deleting the filter.", quote=True)

async def del_all(message, group_id, title):
    if str(group_id) not in await db.list_collection_names():
        await message.edit_text(f"Nothing to remove in {title}!")
        return

    mycol = db[str(group_id)]
    try:
        await mycol.drop()
        await message.edit_text(f"All filters from {title} have been removed")
    except Exception as e:
        logger.exception('Error removing all filters', exc_info=True)
        await message.edit_text("Couldn't remove all filters from group!")

async def count_filters(group_id):
    mycol = db[str(group_id)]

    try:
        count = await mycol.count_documents({})
        return count > 0
    except Exception as e:
        logger.exception('Error counting filters', exc_info=True)
        return False

async def filter_stats():
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

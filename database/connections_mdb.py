import motor.motor_asyncio
from info import DATABASE_URL, DATABASE_NAME
import logging

# Set up logging
logger = logging.getLogger(name)
logger.setLevel(logging.ERROR)

# Initialize Motor client and database
client = motor.motor_asyncio.AsyncIOMotorClient(DATABASE_URL)
db = client[DATABASE_NAME]
collection = db['CONNECTION']

async def add_connection(group_id, user_id):
    try:
        result = await collection.update_one(
            {'_id': user_id, 'group_details.group_id': {'$ne': group_id}},  # Ensure group_id doesn't already exist
            {
                '$push': {'group_details': {'group_id': group_id}},
                '$set': {'active_group': group_id}
            },
            upsert=True  # Insert if not exists
        )
        return result.modified_count > 0 or result.upserted_id is not None
    except Exception:
        logger.exception('Error adding connection', exc_info=True)
        return False

async def active_connection(user_id):
    query = await collection.find_one(
        {'_id': user_id},
        {'_id': 0, 'active_group': 1}
    )
    if query and query.get('active_group'):
        return int(query['active_group'])
    return None

async def all_connections(user_id):
    query = await collection.find_one(
        {'_id': user_id},
        {'_id': 0, 'group_details.group_id': 1}
    )
    if query and query.get('group_details'):
        return [x['group_id'] for x in query['group_details']]
    return []

async def if_active(user_id, group_id):
    count = await collection.count_documents(
        {'_id': user_id, 'active_group': group_id},
        limit=1  # Optimization: Stop searching after 1 match
    )
    return count > 0

async def make_active(user_id, group_id):
    result = await collection.update_one(
        {'_id': user_id},
        {'$set': {'active_group': group_id}}
    )
    return result.modified_count > 0

async def make_inactive(user_id):
    result = await collection.update_one(
        {'_id': user_id},
        {'$set': {'active_group': None}}
    )
    return result.modified_count > 0

async def delete_connection(user_id, group_id):
    try:
        # Remove the group_id from group_details
        result = await collection.update_one(
            {'_id': user_id},
            {'$pull': {'group_details': {'group_id': group_id}}}
        )
        if result.modified_count == 0:
            return False

        # Check if we need to update active_group
        query = await collection.find_one({'_id': user_id})
        if query and query.get('group_details'):
            if query['active_group'] == group_id:
                # Set the last group's ID as the new active_group
                new_active_group = query['group_details'][-1]['group_id']
                await collection.update_one(
                    {'_id': user_id},
                    {'$set': {'active_group': new_active_group}}
                )
        else:
            # No group_details left, set active_group to None
            await collection.update_one(
                {'_id': user_id},
                {'$set': {'active_group': None}}
            )
        return True
    except Exception:
        logger.exception('Error deleting connection', exc_info=True)
        return False

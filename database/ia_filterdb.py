import logging
from struct import pack
import re
import base64
from pyrogram.file_id import FileId
from pymongo.errors import DuplicateKeyError
from umongo import Instance, Document, fields
from motor.motor_asyncio import AsyncIOMotorClient
from marshmallow.exceptions import ValidationError
from info import FILE_DB_URL, FILE_DB_NAME, COLLECTION_NAME, MAX_RIST_BTNS

# Set up logging
logger = logging.getLogger(name)
logger.setLevel(logging.INFO)

# Initialize Motor client and database
client = AsyncIOMotorClient(FILE_DB_URL)
db = client[FILE_DB_NAME]
instance = Instance.from_db(db)

@instance.register
class Media(Document):
    file_id = fields.StrField(attribute='_id')
    file_ref = fields.StrField(allow_none=True)
    file_name = fields.StrField(required=True)
    file_size = fields.IntField(required=True)
    file_type = fields.StrField(allow_none=True)
    mime_type = fields.StrField(allow_none=True)
    caption = fields.StrField(allow_none=True)

    class Meta:
        collection_name = COLLECTION_NAME

async def save_file(media):
    file_id, file_ref = unpack_new_file_id(media.file_id)
    file_name = re.sub(r"@\w+|(_|\-|\.|\+)", " ", str(media.file_name))
    try:
        file = Media(
            file_id=file_id,
            file_ref=file_ref,
            file_name=file_name,
            file_size=media.file_size,
            file_type=media.file_type,
            mime_type=media.mime_type
        )
    except ValidationError as e:
        logger.exception('Validation Error occurred while saving file in database', exc_info=True)
        return False, 2
    try:
        await file.commit()
    except DuplicateKeyError:
        logger.warning(f"{file_name} is already saved in the database")
        return False, 0
    else:
        logger.info(f"{file_name} has been saved in the database")
        return True, 1

async def get_search_results(query, file_type=None, max_results=MAX_RIST_BTNS, offset=0, filter=False):
    query = query.strip()
    if not query:
        raw_pattern = '.'
    elif ' ' not in query:
        raw_pattern = r'(\b|[\.\+\-_])' + query + r'(\b|[\.\+\-_])'
    else:
        raw_pattern = query.replace(' ', r'.*[\s\.\+\-_]')
    
    try:
        regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    except re.error as e:
        logger.exception('Regex compilation error', exc_info=True)
        return [], '', 0

    search_filter = {'file_name': regex}
    if file_type:
        search_filter['file_type'] = file_type

    total_results = await Media.count_documents(search_filter)
    next_offset = offset + max_results
    if next_offset > total_results:
        next_offset = ''

    cursor = Media.find(search_filter)
    cursor.sort('$natural', -1)
    cursor.skip(offset).limit(max_results)
    files = await cursor.to_list(length=max_results)
    
    return files, next_offset, total_results

async def get_file_details(query):
    filter = {'file_id': query}
    filedetails = await Media.find_one(filter)
    return filedetails

def encode_file_id(s: bytes) -> str:
    r = b""
    n = 0
    for i in s + bytes([22]) + bytes([4]):
        if i == 0:
            n += 1
        else:
            if n:
                r += b"\x00" + bytes([n])
                n = 0
            r += bytes([i])
    return base64.urlsafe_b64encode(r).decode().rstrip("=")

def encode_file_ref(file_ref: bytes) -> str:
    return base64.urlsafe_b64encode(file_ref).decode().rstrip("=")

def unpack_new_file_id(new_file_id):
    """Return file_id, file_ref"""
    decoded = FileId.decode(new_file_id)
    file_id = encode_file_id(
        pack(
            "<iiqq",
            int(decoded.file_type),
            decoded.dc_id,
            decoded.media_id,
            decoded.access_hash
        )
    )
    file_ref = encode_file_ref(decoded.file_reference)
    return file_id, file_ref

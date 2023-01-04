import pymongo

def connect_collection(str):
  db_client = pymongo.MongoClient("mongodb+srv://andrey:28122011@cluster0.i2aesum.mongodb.net/?retryWrites=true&w=majority")
  current_db = db_client['TeleBot']

  return current_db[str]

async def check_id(collection, id):
  obj = await collection.find_one({'id': id})
  if obj:
    return True
  return False


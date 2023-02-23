import pymongo

def connect_collection(str):
  db_client = pymongo.MongoClient("mongodb+srv://andrey:28122011@cluster0.i2aesum.mongodb.net/?retryWrites=true&w=majority")
  current_db = db_client['TeleBot']

  return current_db[str]

def check_key(collection_db, key, value):
  obj = collection_db.find_one({key: value})
  if obj:
    return True
  return False

def available_time():
  available_time = []

  book = connect_collection('book')
  asd = book.find()
  for obj in asd:
    time = obj['time']
    for key in time:
      if not key in available_time:
          if time[key] == True:
            available_time.append(key)

  return available_time

async def auth_err(collection_name, key, message, answer):
  collection = connect_collection(collection_name)
  if not check_key(collection, key, message.text):
    await message.answer(answer)
    return True
  return False

def give_user(collection, id):
  return collection.find_one({'id': id})

def change_key(collection, filter, key, value):
  collection.update_one(filter, { "$set": { key: value } })
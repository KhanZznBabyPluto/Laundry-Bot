from pandas import DataFrame
from mongo import *

def available_time():
  available_time = list()

  book = connect_collection('book')
  decode = DataFrame(book.find())

  for times in decode.columns[2:]:
    if True in decode[times].values:
      available_time.append(times)
  return available_time
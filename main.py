from pandas import DataFrame
from mongo import *

book = connect_collection('book')

decode = DataFrame(book.find())

print(decode)
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
connection = MongoClient(os.getenv('MONGO_URI'))
db = connection.squawk


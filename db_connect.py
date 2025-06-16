from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
client = MongoClient(os.getenv("MONGODB_URI"))
db = client["ticketing_platform"]
customers_collection = db["customers"]
tickets_collection = db["tickets"]

# Test query
print(customers_collection.find_one({"username": "john_doe"}))
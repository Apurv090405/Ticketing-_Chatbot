from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

class Database:
    def __init__(self):
        try:
            self.client = MongoClient("localhost", 27017)
            self.db = self.client["Ticketing_Platform"]
            self.customers_collection = self.db["Customers"]
            self.tickets_collection = self.db["tickets"]
        except Exception as e:
            raise Exception(f"Failed to connect to MongoDB: {e}")

    def get_customer_by_username(self, username):
        try:
            return self.customers_collection.find_one({"username": username})
        except Exception as e:
            print(f"Error fetching customer: {e}")
            return None

    def add_customer(self, customer):
        try:
            result = self.customers_collection.insert_one(customer)
            return result.inserted_id
        except Exception as e:
            print(f"Error adding customer: {e}")
            return None

    def get_tickets(self):
        try:
            tickets = list(self.tickets_collection.find())
            if not tickets:
                print("No tickets found in the database.")
                return []
            for ticket in tickets:
                if "ticket_id" not in ticket:
                    ticket["ticket_id"] = str(ticket["_id"])
            return tickets
        except Exception as e:
            print(f"Error fetching tickets: {e}")
            return []

    def get_ticket_by_query(self, query):
        try:
            ticket = self.tickets_collection.find_one({"query": query})
            if ticket and "ticket_id" not in ticket:
                ticket["ticket_id"] = str(ticket["_id"])
            return ticket
        except Exception as e:
            print(f"Error fetching ticket by query: {e}")
            return None

    def add_ticket(self, ticket):
        try:
            result = self.tickets_collection.insert_one(ticket)
            return result.inserted_id
        except Exception as e:
            print(f"Error adding ticket: {e}")
            return None

db = Database()
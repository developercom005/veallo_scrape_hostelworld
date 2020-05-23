import pymongo
from pymongo import MongoClient
import os
from bson import ObjectId
from bson.son import SON
from datetime import datetime

class MongoDBService:
    client = None
    url = None

    def __init__(self, url):
        self.url = url
        self.get_mongo_client()

    def get_mongo_client(self):
        """Connect to the mongodb database server """
        self.client = None

        print('Connecting to the MongoDB database...')
        if self.client is None:
            try:
                self.client = MongoClient(self.url)
                return self.client

            except (Exception, pymongo.errors.ConnectionFailure) as error:
                print(error)
            except (Exception, pymongo.errors.ServerSelectionTimeoutError) as error:
                print(error)
            finally:
                print("In Finally")
                if self.client is not None:
                    self.client.close()
                    print("MongoDB Connection closed")


    def insert_cities(self, data):
        db_veallo = self.client["veallo"]
        collection_cities = db_veallo["hostelworld_cities"]
        try:
            collection_cities.insert_many(data)
            print("City Data inserted in db")
            return True
        except pymongo.errors.DuplicateKeyError as de:
            print(de.details)
            print("Duplicate found while inserting city data in db.")
            pass
            return True
        except pymongo.errors.OperationFailure as be:
            print(be.details)
            print("OperationFailure while inserting city data  in db.")
            pass
            return False


    def insert_city(self, data):
        db_veallo = self.client["veallo"]
        collection_cities = db_veallo["hostelworld_cities"]
        try:
            collection_cities.insert_one(data)
            print("City Data inserted in db")
            return True
        except pymongo.errors.DuplicateKeyError as de:
            print("Duplicate found while inserting city data in db.")
            pass
            return True
        except pymongo.errors.OperationFailure as be:
            print("OperationFailure while inserting city data  in db.")
            pass
            return False

    def insert_accommodation(self, data):
        db_veallo = self.client["veallo"]
        collection_accommodations = db_veallo["accommodation"]
        status = False
        try:
            collection_accommodations.insert_one(data)
            status = True
        except pymongo.errors.DuplicateKeyError as de:
            print(de.details)
            print("Duplicate found while inserting accommodation data in db.")
            status = False
            pass
        except pymongo.errors.OperationFailure as be:
            print(be.details)
            print("OperationFailure while inserting accommodation data  in db.")
            status = False
            pass
        return status

    def update_scrapped_city_accommodations(self):
        db_veallo = self.client["veallo"]
        collection_accommodations = db_veallo["accommodation"]
        collection_cities = db_veallo["hostelworld_cities"]
        cities = []
        try:
            for a in collection_accommodations.aggregate([
                {"$match": {"website": "https://www.hostelworld.com/"}},
                {"$group": {
                    "_id": None,
                    "city": {"$addToSet": '$city'}
                }}
            ]):
                cities = a["city"]
            for city in cities:
                for c in collection_cities.find({"city": city}):
                    _id = c["_id"]
                    collection_cities.update_one({"_id": _id}, {"$set": {"scrapped": True, "modified_date": datetime.utcnow()}})
                    print(city, " updated")
        except pymongo.errors.DuplicateKeyError as de:
            print(de.details)
            print("Duplicate found while inserting city data in db.")
            pass
            return True
        except pymongo.errors.OperationFailure as be:
            print(be.details)
            print("OperationFailure while inserting city data  in db.")
            pass
            return False


    def get_city_left_to_scrape(self):
        db_veallo = self.client["veallo"]
        collection_cities = db_veallo["hostelworld_cities"]
        cities = []
        try:
            for c in collection_cities.find({"scrapped": False}):
                cities.append(c)
        except pymongo.errors.DuplicateKeyError as de:
            print(de.details)
            print("Duplicate found while getting cities data in db.")
            pass
        except pymongo.errors.OperationFailure as be:
            print(be.details)
            print("OperationFailure while getting cities data  in db.")
            pass
        return cities

    def get_country_by_distinct_fields(self):
        db_veallo = self.client["veallo"]
        collection_cities = db_veallo["hostelworld_cities"]
        countries = []
        try:
            for c in collection_cities.distinct("country"):
                countries.append(c)
        except pymongo.errors.DuplicateKeyError as de:
            print(de.details)
            print("Duplicate found while getting cities data in db.")
            pass
        except pymongo.errors.OperationFailure as be:
            print(be.details)
            print("OperationFailure while getting cities data  in db.")
            pass
        return countries


    def update_cities(self, city, country, scrapped_value,count):
        db_veallo = self.client["veallo"]
        collection_cities = db_veallo["hostelworld_cities"]
        update_id =  None
        try:
            for c in collection_cities.find({"$and": [{"city": city, "country": country}]}):
                print("--------------------")
                print(c)
                print("--------------------")
                update_id = c["_id"]
            collection_cities.update_one({"_id": update_id}, {"$set": {"scrapped": scrapped_value, "count": count, "modified_date": datetime.utcnow()}})
            print("Updated city count with true for ", city)
            return True
        except pymongo.errors.DuplicateKeyError as de:
            print(de.details)
            print("Duplicate found while inserting city data in db.")
            pass
            return True
        except pymongo.errors.OperationFailure as be:
            print(be.details)
            print("OperationFailure while inserting city data  in db.")
            pass
            return False

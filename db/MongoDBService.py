import pymongo
from pymongo import MongoClient
import os
from bson import ObjectId
from bson.son import SON

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
            collection_cities.insert_one(data)
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

    def get_accommodation_by_distinct_fields(self):
        db_veallo = self.client["veallo"]
        collection_cities = db_veallo["accommodation"]
        cities = []
        try:
            for c in collection_cities.aggregate([
                {"$match": {"website": "https://www.hostelworld.com/"}},
                {"$group": {
                "_id": None,
                "city": {"$addToSet": '$city'}
                }}
            ]):
                cities = c["city"]
        except pymongo.errors.DuplicateKeyError as de:
            print(de.details)
            print("Duplicate found while getting cities data in db.")
            pass
        except pymongo.errors.OperationFailure as be:
            print(be.details)
            print("OperationFailure while getting cities data  in db.")
            pass
        return cities


    def get_cities(self,query,limit,skip):
        db_veallo = self.client["veallo"]
        collection_cities = db_veallo["cities"]
        cities = []
        try:
            for c in collection_cities.find(query).skip(skip).limit(limit):
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
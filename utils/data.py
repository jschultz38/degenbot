from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.collection import ReturnDocument
import credentials

class RemoteStorageConnection():
    def __init__(self):
        #TODO: will move database names around later instead of 'test'
        uri = f"mongodb+srv://degen-bot:{credentials.mongo_password}@cluster0.e2siu.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        # Create a new client and connect to the server
        self.client = MongoClient(uri, server_api=ServerApi('1'))

        # Send a ping to confirm a successful connection
        try:
            self.client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
            self.connected = True
        except Exception as e:
            print(e)
            self.connected = False

    '''Calls mongodb to update the pat missed count and return an int'''
    def miss_pat(self):
        collection = self.client['test']['commands']
        query = {"name" : "Pat"}
        updated_document = collection.find_one_and_update(
            query,
            {"$inc": {"count":1}},
            return_document = ReturnDocument.AFTER
        )
        return updated_document["count"]

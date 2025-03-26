from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.collection import ReturnDocument
from datetime import datetime
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

    def write_command(self, command):
        collection = self.client['degendb']['commands']
        collection.update_one(
            {command: command},
            {
                "$inc": {'count': 1},
                "$setOnInsert": {"createdAt": datetime.now()},
                "$set": {"updatedAt": datetime.now()}
            },
            upsert= True
        )
    #keep in here for future utility
    def update_team_data(self, team_data):
        collection = self.client['degendb']['teams']
        for team in team_data["teams"]:
            team_filter = {"id": team["id"]}  # Filter based on the team 'id'
        team_update = {
            "$set": team
        }
        collection.update_one(team_filter, team_update, upsert=True)

    #Getting this to match the existing JSON doc
    def get_team_data(self):
        # Default seasons data if not found
        seasons_data = {'khl': {'current_seasons': []}}  # Use empty list as fallback

        # Retrieve teams data
        collection = self.client['degendb']['teams']
        teams_data = [{k: v for k, v in doc.items() if k != "_id"} for doc in collection.find({})]

        try:
            # Retrieve season data
            season_coll = self.client['degendb']['seasons']
            result = season_coll.find_one({}, {"seasons.khl.current_seasons": 1})
            if result and 'seasons' in result:
                seasons_data = result['seasons']
        except Exception as e:
            print(f"Error retrieving seasons data: {e}")

        # Prepare final data combining seasons and teams
        data = {
            "seasons": seasons_data,
            "teams": teams_data
        }
        return data

    # def import_team_data(self):
    #     return
    #
    # def update_team_data(self):
    #     #add team
    #     #remove team
    #     #add or remove player from a team

    def update_seasons(self, league, new_season):
        collection = self.client['degendb']['seasons']
        collection.update_one(
            {"seasons.{}".format(league): {"$exists": True}},  # Check if league exists
            {"$addToSet": {f"seasons.{league}.current_seasons": {"$each": [new_season]}}},  # Add seasons if not present
            upsert=True  # Insert if document doesn't exist
        )


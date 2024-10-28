from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.collection import ReturnDocument
from datetime import datetime
import credentials
import threading

class RemoteStorageConnection():
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(RemoteStorageConnection, cls).__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        uri = f"mongodb+srv://degen-bot:{credentials.mongo_password}@cluster0.e2siu.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        self.client = MongoClient(uri, server_api=ServerApi('1'))
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

    def write_player_game_stats(self, data):
        # Data should include: 'Player', 'Team', 'season_id', 'id', 'Goals', 'Assists', 'Secondary Assists'
        collection = self.client['degendb']['players']
        player = collection.find_one({"name": data['Player']})

        # Convert the season_id to string
        season_id_str = str(data['season_id'])
        game_id_str = str(data['id'])  # Convert game ID to string

        if player:
            # Check if the season already exists
            season = player.get("seasons", {}).get(season_id_str, None)
            if data['Team'] not in player['teams']:
                print(f"Adding new team '{data['Team']}' to player {data['Player']}")
                collection.update_one(
                    {"name": data['Player']},
                    {"$addToSet": {"teams": data['Team']}}
                )

            if season:
                # Check if the game already exists within the season
                game = season.get("games", {}).get(game_id_str, None)

                if game:
                    # Update the existing game's stats
                    collection.update_one(
                        {"name": data['Player'], f"seasons.{season_id_str}.games.{game_id_str}": {"$exists": True}},
                        {
                            "$set": {
                                f"seasons.{season_id_str}.games.{game_id_str}.goals": int(data['Goals']),
                                f"seasons.{season_id_str}.games.{game_id_str}.assists": int(data['Assists']),
                                f"seasons.{season_id_str}.games.{game_id_str}.secondaries": int(
                                    data['Secondary Assists']),
                                f"seasons.{season_id_str}.games.{game_id_str}.team": data['Team']
                                # Update the team if necessary
                            }
                        }
                    )
                else:
                    # Add a new game entry to the existing season
                    collection.update_one(
                        {"name": data['Player'], f"seasons.{season_id_str}": {"$exists": True}},
                        {
                            "$set": {
                                f"seasons.{season_id_str}.games.{game_id_str}": {
                                    "team": data['Team'],  # Include team for the new game
                                    "goals": int(data['Goals']),
                                    "assists": int(data['Assists']),
                                    "secondaries": int(data['Secondary Assists']),
                                }
                            }
                        }
                    )
            else:
                # Add a new season with the game entry
                collection.update_one(
                    {"name": data['Player']},
                    {
                        "$set": {
                            f"seasons.{season_id_str}": {
                                "games": {
                                    game_id_str: {
                                        "team": data['Team'],  # Include team for the new game
                                        "goals": int(data['Goals']),
                                        "assists": int(data['Assists']),
                                        "secondaries": int(data['Secondary Assists']),
                                    }
                                }
                            }
                        }
                    }
                )
        else:
            # Insert a new player with the season and game data
            collection.insert_one({
                "name": data['Player'],
                "teams": [data['Team']],
                "seasons": {
                    season_id_str: {  # Ensure season_id is a string
                        "games": {
                            game_id_str: {  # Each game is keyed by its unique ID
                                "team": data['Team'],  # Include team for the new game
                                "goals": int(data['Goals']),
                                "assists": int(data['Assists']),
                                "secondaries": int(data['Secondary Assists']),
                            }
                        }
                    }
                }
            })



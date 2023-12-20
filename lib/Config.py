# Create an empty config.json file if one doesn't already exist
import json

class Config():
    @staticmethod
    def generate_config():
        """create a new empty config file"""
        # not sure if this method is totally necessary but I will keep for now
        dictionary = {
            "minBlockRate": 42,
            "minPayRatePerHour": 21,
            "arrivalBuffer": 20,
            "desiredWarehouses": [],
            "desiredStartTime": "00:00",
            "desiredEndTime": "23:30",
            "desiredWeekdays": [
            "MON",
                "tue",
                "Wed",
                "Thur",
                "Fri",
                "Sat",
                "Sunday"
            ],
            "chat_id": None,
            "first_name": None,
            "last_name": None,
            "language_code": None,
            "refreshInterval": 2.5,
            "refreshToken": None,
            "accessToken": None
        }
        
        with open("config.json", 'w') as f:
            json.dump(dictionary, f, indent=4)

    @staticmethod
    def as_dict():
        """return a dict full of empty config data"""
        dictionary = {
            "minBlockRate": 42,
            "minPayRatePerHour": 21,
            "arrivalBuffer": 20,
            "desiredWarehouses": [],
            "desiredStartTime": "00:00",
            "desiredEndTime": "23:30",
            "desiredWeekdays": [
            "MON",
                "tue",
                "Wed",
                "Thur",
                "Fri",
                "Sat",
                "Sunday"
            ],
            "chat_id": None,
            "first_name": None,
            "last_name": None,
            "language_code": None,
            "refreshInterval": 2.5,
            "refreshToken": None,
            "accessToken": None
        }

        return dictionary



import json
import os


def get_json_fixture(filename):
    data = None
    location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

    with open(os.path.join(location, filename)) as json_data:
        data = json.load(json_data)
    return data

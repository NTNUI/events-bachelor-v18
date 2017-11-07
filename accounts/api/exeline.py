import requests as req


class Exeline(object):

    def __init__(self, username, password, requests=None):
        if requests == None:
            self.requests = req
        else:
            self.requests = requests

        self.username = username
        self.password = password
        self.base_url = 'http://exceline.net/NTNUI'
        self.gyms = {
            '1': {'name': 'SiT Gløshaugen', 'id': '1'},
            '2': {'name': 'SiT Dragvoll', 'id': '2'},
            '3': {'name': 'SiT Portalen', 'id': '3'},
            '4': {'name': 'SiT DMMH', 'id': '4'},
            '5': {'name': 'SiT Moholt', 'id': '5'},
        }

    def request(self, url):
        r = self.requests.get(self.base_url + url)
        return r.json()

    def get_url(self, func, gym_id=None, customer_number=None, days=0):
        urls = {
            'customer_in_gym': '/Member/%s/%s/%s/%s' % (gym_id, customer_number, self.username, self.password),
            'members_for_gym_since_days': '/Members/%s/%i/%s/%s' % (gym_id, days, self.username, self.password),
            'members_for_gym': '/Members/%s/%s/%s' % (gym_id, self.username, self.password),
        }
        if func in urls:
            return urls[func]
        raise Exception('Invalid URL function.')

    def get_members_for_gym(self, gym_id):
        if gym_id not in self.gyms:
            raise Exception('Invalid gym id.')

        url = self.get_url(func='members_for_gym', gym_id=gym_id)
        response =  self.request(url)
        return response['GetMemberDataResult']['Members']

    def get_members_for_all_gyms(self):
        results = {}
        for gym_id in self.gyms:
            results[gym_id] = self.get_members_for_gym(gym_id)
        return results

    def get_members_for_gym_since(self, gym_id, days):
        if gym_id not in self.gyms:
            raise Exception('Invalid gym id.')
        url = self.get_url(func='members_for_gym_since_days',
                           gym_id=gym_id, days=days)
        response =  self.request(url)
        return response['GetMemberDataChangesResult']['Members']

    def get_members_for_all_gyms_since(self, days):
        results = {}
        for gym_id in self.gyms:
            results[gym_id] = self.get_members_for_gym_since(gym_id, days)
        return results

    def get_customer_info(self, gym_id, customer_number):
        url = self.get_url(func='customer_in_gym',
                           gym_id=gym_id, customer_number=customer_number)
        response =  self.request(url)
        return response['GetMemberDataResult']['Members']

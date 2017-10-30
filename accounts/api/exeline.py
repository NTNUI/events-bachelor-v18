import requests

class Exeline(object):

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.base_url = 'http://exceline.net'

    def request(self, url):
        r = requests.get(self.base_url + url)
        return r.json()

    def get_members_for_gym(self, gym_id):
        pass

    def get_members_for_all_gyms(self):
        pass

    def get_members_for_gym_since(self, gym_id, days):
        pass

    def get_members_for_all_gyms_since(self, gym_id, days):
        pass

    def get_customer_info(self, gym_id, customer_no):
        url = '/NTNUI/Member/%s/%s/%s/%s' % (gym_id, customer_no, self.username, self.password)
        return self.request(url)

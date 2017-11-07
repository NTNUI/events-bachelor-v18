

class ApiFilterer(object):

    def filter_only_ntnui_members(self, all_members):
        ntnui_contract_types = ['10', '20', '359', '483', '485']
        ntnui_members = []
        for member in all_members:
            if member['contract']['type'] in ntnui_contract_types:
                ntnui_members.append(member)
        return ntnui_members

from django.core.urlresolvers import reverse

# We test with the group 'volleyball'

# TEST USERS
# Todd Packer     - todd.packer@online.com            - President
# James Halpert   - jameshalpert@gmail.com            - Vice President
# Angela Martin   - frankela@steinberg.org            - Cashier
# Michael Scott   - michael.scott@dundermifflin.com   - Normal Member
# Meredith Palmer - meredith.palmer@dundermifflin.com - Not a member

# All test users have password "locoloco"

TEST_USERS = {
    'president': 'todd.packer@online.com',
    'vice_president': 'jameshalpert@gmail.com',
    'cashier': 'frankela@steinberg.org',
    'member': 'michael.scott@dundermifflin.com',
    'not_member': 'meredith.palmer@dundermifflin.com'
}

TEST_PASSWORD = 'locoloco'


class LoggedInMixin(object):
    fixtures = ['users.json']

    def setUp(self):
        if not hasattr(self, 'email'):
            raise ValueError('Make sure to specify email in your test class')
        if not hasattr(self, 'url_name'):
            raise ValueError('Make sure to include url_name in your test class')
        self.login_response = self.client.login(email=self.email,
                                                password=TEST_PASSWORD)
        url = reverse(self.url_name, kwargs={'slug': 'volleyball'})
        self.response = self.client.get(url)


class GroupMixin(LoggedInMixin):
    fixtures = ['users.json', 'groups.json',
                'memberships.json', 'invitations.json', 'boards.json', 'requests.json']

    def setUp(self):
        super(GroupMixin, self).setUp()

    def test_status_code_200(self):
        self.assertEquals(self.response.status_code, 200)

    def test_should_contain_group_name(self):
        self.assertContains(self.response, 'NTNUI Volleyball')

    def test_should_link_to_about(self):
        self.assertContains(self.response, reverse(
            'group_index', kwargs={'slug': 'volleyball'}))

    def test_should_link_to_settings(self):
        self.assertContains(self.response, reverse(
            'group_settings', kwargs={'slug': 'volleyball'}))

    # should link to forms page in the future as well
    # def test_should_link_to_forms(self):
    #     self.assertContains(self.response, reverse(
    #         'group_forms', kwargs={'slug': 'volleyball'}))


class GeneralMemberMixin(GroupMixin):
    def setUp(self):
        super(GeneralMemberMixin, self).setUp()

    def test_should_not_link_to_members(self):
        self.assertNotContains(self.response, reverse(
            'group_members', kwargs={'slug': 'volleyball'}))


class CoreBoardMemberMixin(GroupMixin):
    def setUp(self):
        super(CoreBoardMemberMixin, self).setUp()

    def test_should_link_to_members(self):
        self.assertContains(self.response, reverse(
            'group_members', kwargs={'slug': 'volleyball'}))


class GeneralBoardMemberMixin(CoreBoardMemberMixin):
    def setUp(self):
        super(GeneralBoardMemberMixin, self).setUp()


class GeneralGroupLeaderMixin(CoreBoardMemberMixin):
    def setUp(self):
        super(GeneralGroupLeaderMixin, self).setUp()

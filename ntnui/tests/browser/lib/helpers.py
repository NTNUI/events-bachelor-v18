from django.conf import settings


def login_user(cls, browser):
    browser.get(cls.server_url + '/login/')
    username_input = browser.find_element_by_name('username')
    username_input.send_keys(settings.DUMMY_USER_EMAIL)
    password_input = browser.find_element_by_name('password')
    password_input.send_keys(settings.DUMMY_USER_PASSWORD)
    browser.find_element_by_xpath('//button[text()="Log in"]').click()
    account_p = browser.find_element_by_xpath('//p[text()="Account"]')

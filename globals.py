from threading import Lock

'''Uses alternate token named 'test_token' in credentials.py'''
USE_TEST_TOKEN = False

'''True to spin up caching thread'''
USE_CACHING = True

'''Puts bot in test mode, which doesn't make any http requests and only uses a
saved .html file for a single team for player Jarrett. Only really useful if you
are doing an overhaul to the bot infrastructure and need to iterate quickly
without bothering with http requests.

Honestly, not sure if this even still works. Use at your own risk.'''
TEST_MODE = False

'''Don't touch these'''
CACHING_LOCK = Lock()
SEASONS = []

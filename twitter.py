import pymongo
import tweepy

import defaults
import pprint
import csv
import json

TEST_USER = "sven_manske"

try:
    auth = tweepy.OAuthHandler(defaults.api_key, defaults.api_secret)
    auth.set_access_token(defaults.access_token, defaults.access_token_secret)
    api = tweepy.API(auth)
except AttributeError as e:
    print("[WARNING] Twitter API keys are not set in defaults.py. No API connection established.")

def store_timeline_in_db(timeline):
    myclient = pymongo.MongoClient(defaults.DB_CONNECTION)
    mydb = myclient[defaults.DB_NAME]
    mycol = mydb[defaults.DB_COLLECTION_TIMELINES]
    return mycol.insert_one(timeline)


def store_user_in_db(user):
    myclient = pymongo.MongoClient(defaults.DB_CONNECTION)
    mydb = myclient[defaults.DB_NAME]
    mycol = mydb[defaults.DB_COLLECTION_USERS]
    return mycol.insert_one(user)


def get_user_db(user):
    myclient = pymongo.MongoClient(defaults.DB_CONNECTION)
    mydb = myclient[defaults.DB_NAME]
    mycol = mydb[defaults.DB_COLLECTION_USERS]
    return mycol.find_one({'screen_name': user})


# user or status objects from tweepy are not json-serializable
# however, tweepy fetches a json-serializable representation into the _json property
def tweepy_arr_to_json(status_arr):
    return [status._json for status in status_arr]


def tweepy_obj_to_json(obj):
    return obj._json


def retrieve_timeline(username, store_in_db):
    public_tweets = api.user_timeline(screen_name=username)
    timeline_obj = {
        "username": username,
        "timeline": tweepy_arr_to_json(public_tweets)
    }
    if store_in_db: store_timeline_in_db(timeline_obj)
    print([t.text for t in public_tweets])
    return public_tweets

def create_user_profile(tweepy_user):
    return {
        'description': tweepy_user.description,
        'location': tweepy_user.location,
        'name': tweepy_user.name,
        'followerscount': tweepy_user.followers_count,
        'friendscount': tweepy_user.friends_count,
        'listedcount': tweepy_user.listed_count,
        'favouritescount': tweepy_user.favourites_count,
        'verified': tweepy_user.verified,
        'geoenabled': tweepy_user.geo_enabled,
        'statusescount': tweepy_user.statuses_count,
        'protected': tweepy_user.protected,
        'lang': tweepy_user.lang,
        'url': tweepy_user.url
    }


def retrieve_profile(screen_name, caching=True):
    if caching:
        user = get_user_db(screen_name)
        # TODO: this is very simplistic. Probably we need an expiration routine
        # not using mongodb TTL to preserve all data
        if user is None:
            try:
                user = api.get_user(screen_name=screen_name)
                create_user_profile(user)
                store_user_in_db(user._json)
            except tweepy.error.TweepError as e:
                user_obj = {
                    'screen_name': screen_name,
                    'user': 'user',
                    'supsended': True,
                    'error_code': e.args[0][0]['code']
                }
                print("[TWITTER] user", user, "has been suspended by Twitter.")
                store_user_in_db(user_obj)
    else:
        user = api.get_user(screen_name=screen_name)
        store_user_in_db(user._json)
    return user


def retrieve_profiles(screen_name_arr, caching=True):
    print("[TWITTER] Batch profile retrieval started...")
    for name in screen_name_arr:
        print("[TWITTER] Retrieving profile:", name)
        retrieve_profile(name, caching)


# retrieve_timeline(TEST_USER, True)
# retrieve_profile(TEST_USER, True)
# print(retrieve_profile(TEST_USER))

# profile_names = [TEST_USER, "SDGaction", "UNOCHA"]
# retrieve_profiles(profile_names)

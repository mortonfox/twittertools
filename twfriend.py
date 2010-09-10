"""
twfriend.py - Categorize Twitter contacts according to whether they are
mutual friends, only friends, or only followers.
"""

import oauthConsumer
import webbrowser

use_simplejson = False
try:
    import json
except ImportError:
    import simplejson
    use_simplejson = True

import sys
import time
import pprint

use_optparse = False
try:
    import argparse
except ImportError:
    import optparse
    use_optparse = True

OAUTH_FILENAME = 'oauth.key'

CONSUMER_KEY = 'VjwGaraEThGrC81x9ZGjfQ'
CONSUMER_SECRET = 'YlI6JRhqyxP5SFVXXbEbI3G5gO3RKGi68O5i3l7uw'

def init_oauth(force_login=False):
    """
    Log in to OAuth.
    Reads the access token and secret from a file if available.
    Otherwise, does the required authentication.

    Args:
    	force_login = If true, reauth anyway even if oauth key file exists.
    Returns:
	client object
    """
    c = oauthConsumer.Client(
	    key=CONSUMER_KEY,
	    secret=CONSUMER_SECRET,
	    requestTokenURL="https://api.twitter.com/oauth/request_token", 
	    accessTokenURL="https://api.twitter.com/oauth/access_token", 
	    authorizeURL="https://api.twitter.com/oauth/authorize", 
	    callbackURL="oob")

    if not force_login:

	# Use the saved OAuth key info if available.
	try:
	    oauth_file = open(OAUTH_FILENAME, "r")

	    token = oauth_file.readline().rstrip()
	    secret = oauth_file.readline().rstrip()

	    oauth_file.close()

	    if token != "" and secret != "":
		c.setSession(token, secret)

	except IOError:
	    pass

    # If no saved OAuth info, we need to log in.
    if c._sessionToken is None:
	authURL = c.requestAuth()
	webbrowser.open(authURL)

	print >> sys.stderr, "Enter PIN: ",
	pin = raw_input()

	sessionInfo = c.requestSession(c._requestToken, pin)

	oauth_file = open(OAUTH_FILENAME, "w")
	oauth_file.write(c._sessionToken + "\n")
	oauth_file.write(c._sessionSecret + "\n")
	oauth_file.close()

    return c


def process_result(str):
    """
    Process the JSON output from the Twitter API call.

    Args:
	str = JSON string to process

    Returns:
    	dict containing id -> screen_name pairs
    """

    if use_simplejson:
	jsn = simplejson.loads(str)
    else:
	jsn = json.loads(str)

    cursor = jsn['next_cursor']

#     pp = pprint.PrettyPrinter(indent=4)
#     pp.pprint(jsn)

    flist = {}
    for user in jsn['users']:
	flist[user['id']] = user['screen_name']
    return (cursor, flist)


def get_pages(client, what):
    """ 
    Get all pages of friends or followers and add them to a dict.

    Args:
	client = OAuth client
	what = "friends" or "followers"

    Returns:
    	dict containing id -> screen_name pairs
    """

    page = 0
    cursor = -1
    flist = {}

    while True:
	page += 1
	print >> sys.stderr, "Getting %s page %d..." % (what, page)

	req = client.createRequest(path="/statuses/%s.json" % what)
	result = req.get(params = { "cursor" : str(cursor) } )

	(cursor, flist2) = process_result(result)
	flist.update(flist2)  # Add to our cumulative dict.
	if cursor == 0: break

	time.sleep(1)

    return flist


def show_friends(flist, list_type):
    """
    Display a friends or followers list.
    """
    print "%d %s:" % (len(flist), list_type)
    i = 0
    for id in flist.keys():
	i += 1
	print "%d: %s" % (i, flist[id])
    print


def process_friends(friends, followers):
    """
    Seperate friends and followers lists into
    mutual, only friends, and only followers lists.
    """
    mutual = {}
    only_friends = {}
    only_followers = {}

    for id in friends.keys() + followers.keys():
	if id in friends:
	    if id in followers:
		mutual[id] = friends[id]
	    else:
		only_friends[id] = friends[id]
	elif id in followers:
	    only_followers[id] = followers[id]

    show_friends(mutual, "mutual friends")
    show_friends(only_friends, "only friends")
    show_friends(only_followers, "only followers")


def main():
    if use_optparse:

	parser = optparse.OptionParser()

	parser.add_option('-l', '--login', action='store_true', 
		dest='login', default=False, help='Force OAuth login')

	(options, args) = parser.parse_args()

	client = init_oauth(options.login)

    else:
	parser = argparse.ArgumentParser(
		description='Categorize Twitter friends/followers.')

	parser.add_argument('-l', '--login', 
		action='store_true', 
		default=False, 
		help='Force OAuth login')

	args = parser.parse_args()

	client = init_oauth(args.login)


    friends = get_pages(client, "friends")

#     print "Friends:"
#     pp = pprint.PrettyPrinter(indent=4)
#     pp.pprint(friends)

    followers = get_pages(client, "followers")

#     print "Followers:"
#     pp.pprint(followers)

    process_friends(friends, followers)

if __name__ == '__main__':
    main()

# vim:set tw=0:

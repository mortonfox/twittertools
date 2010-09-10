"""
twlistdump.py - Dump out Twitter lists for backup purposes.
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


class Count:
    count = 0

def process_result(str):
    """
    Process the JSON output from the Twitter API call.
    Prints out the list of users.
    """

    if use_simplejson:
	jsn = simplejson.loads(str)
    else:
	jsn = json.loads(str)

    cursor = jsn['next_cursor']

#     pp = pprint.PrettyPrinter(indent=4)
#     pp.pprint(jsn)

    for user in jsn['users']:
	Count.count += 1
	print "%d: %s %s" % (Count.count, 
		user['id'], 
		user['screen_name'])

    return cursor


def get_pages(user, list, client):
    """
    Get all the pages of members of a Twitter list.
    """
    cursor = -1
    page = 0

    while True:
	page += 1
	print >> sys.stderr, "Getting %s/%s list members page %s..." % (
		user, list, page)

	listreq = client.createRequest(
		path="/%s/%s/members.json" % (user, list))
	result = listreq.get(params = { "cursor" : str(cursor) })

	cursor = process_result(result)
	if cursor == 0: break

	time.sleep(1)


def main():
    if use_optparse:

	parser = optparse.OptionParser(
		usage = 'usage: %prog [options] user list')

	parser.add_option('-l', '--login', action='store_true', 
		dest='login', default=False, help='Force OAuth login')

	(options, args) = parser.parse_args()

	if len(args) < 2:
	    parser.error('too few arguments')

	client = init_oauth(options.login)

	get_pages(args[0], args[1], client)

    else:
	parser = argparse.ArgumentParser(description='Dump a Twitter list.')

	parser.add_argument('-l', '--login', 
		action='store_true', 
		default=False, 
		help='Force OAuth login')

	parser.add_argument('user', help="User name")
	parser.add_argument('list', help="List name")

	args = parser.parse_args()

	client = init_oauth(args.login)

	get_pages(args.user, args.list, client)


if __name__ == '__main__':
    main()

# vim:set tw=0:

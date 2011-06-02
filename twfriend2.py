"""
twfriend2.py - Categorize Twitter contacts according to whether they are
mutual friends, only friends, or only followers.
"""

import sys
import time
import pprint
import twlib


def get_ids(client, what):
    """ 
    Get all pages of friends or followers IDs and add them to a list.

    Args:
	client = OAuth client
	what = "friends" or "followers"

    Returns:
    	list of ids
    """
    page = 0
    cursor = -1
    idlist = []

    while True:
	page += 1
	print >> sys.stderr, "Getting %s page %d..." % (what, page)

	result = twlib.twitter_retry(client, 'get',
		path='/1/%s/ids.json' % what,
		params = { "cursor" : str(cursor) } )
	jsn = twlib.parse_json(result)
	cursor = jsn['next_cursor']
	idlist += jsn['ids']

	if cursor == 0:
	    break

	time.sleep(1)

    return idlist

def show_list(client, idlist, list_type):
    """
    Display a friends or followers list.
    """
    namelist = []
    page = 0
    for i in xrange(0, len(idlist), 100):
	page += 1
	print >> sys.stderr, 'Getting %s info page %d...' % (list_type, page)

	result = twlib.twitter_retry(client, 'get',
		path='/1/users/lookup.json',
		params = { 'user_id' : ','.join(map(str, idlist[i : i+100])) })
	jsn = twlib.parse_json(result)

# 	pp = pprint.PrettyPrinter(indent=4)
# 	pp.pprint(jsn)

	for user in jsn:
	    namelist.append(user['screen_name'])

	time.sleep(1)

    count = len(namelist)
    print '%d %s:' % (count, list_type)
    for i in xrange(0, count):
	print '%d: %s' % (i + 1, namelist[i])
    print


def main():
    parser = twlib.CmdlineParser(desc='Categorize Twitter friends/followers.')
    parser.add_option('-l', '--login', action='store_true', 
	    dest='login', default=False, help='Force OAuth login')
    args = parser.do_parse()
    
    client = twlib.init_oauth(args.login)

    friends = get_ids(client, 'friends')
    followers = get_ids(client, 'followers')

    friends_set = set(friends)
    followers_set = set(followers)

    mutual_set = friends_set & followers_set
    only_friends_set = friends_set - mutual_set
    only_followers_set = followers_set - mutual_set

    show_list(client, list(mutual_set), 'mutual friends')
    show_list(client, list(only_friends_set), 'only friends')
    show_list(client, list(only_followers_set), 'only followers')


if __name__ == '__main__':
    main()

# vim:set tw=0:

"""
twfriend.py - Categorize Twitter contacts according to whether they are
mutual friends, only friends, or only followers.
"""

import sys
import time
import pprint
import twlib


def process_result(str):
    """
    Process the JSON output from the Twitter API call.

    Args:
	str = JSON string to process

    Returns:
    	dict containing id -> screen_name pairs
    """
    jsn = twlib.parse_json(str)

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
    parser = twlib.CmdlineParser(desc='Categorize Twitter friends/followers.')
    parser.add_option('-l', '--login', action='store_true', 
	    dest='login', default=False, help='Force OAuth login')
    args = parser.do_parse()
    
    client = twlib.init_oauth(args.login)

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

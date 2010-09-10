"""
twlistcheck.py - Check Twitter list for protected users whom I'm not following.
"""

import sys
import time
import pprint
import twlib

count = 0

def process_result(str):
    """
    Process the JSON output from the Twitter API call.
    Prints out the list of users with protected but not followed timelines.
    """
    jsn = twlib.parse_json(str)

    cursor = jsn['next_cursor']

#     pp = pprint.PrettyPrinter(indent=4)
#     pp.pprint(jsn)

    puser = []

    for user in jsn['users']:
	global count

	if user['protected'] and not user['following']:
	    count += 1
	    print "%d: %s %s" % (count, user['id'], user['screen_name'])
	    puser += [ user['screen_name'] ]

    return (cursor, puser)


def get_pages(user, list, client):
    """
    Get all the pages of members of a Twitter list.
    """
    cursor = -1
    page = 0

    puser = []

    while True:
	page += 1
	print >> sys.stderr, "Getting %s/%s list members page %s..." % (
		user, list, page)

	listreq = client.createRequest(
		path="/1/%s/%s/members.json" % (user, list))
	result = listreq.get(params = { "cursor" : str(cursor) })

	( cursor, puser2 ) = process_result(result)

	puser += puser2

	if cursor == 0: break

	time.sleep(1)

    return puser


def delete_user(user, list, username, client):
    """
    Remove a user from a list.
    """
    listreq = client.createRequest(
	    path = '/1/%s/%s/members.json' % (user, list))
    result = listreq.post(params = {
	'list_id' : list,
	'id' : username,
	'_method' : 'DELETE',
	})
    #print result

    time.sleep(1)


def ask_delete(user, list, puser, client):
    """
    Given a list of protected but non-followed users, ask whether to remove
    them from list.
    """
    if len(puser) == 0:
	print "None found."
	return

    print >> sys.stderr, 'The following users are protected but not followed:'
    for u in puser:
	print >> sys.stderr, '  ' + u
    print >> sys.stderr, 'Remove them from list? (y/n) ',

    resp = raw_input().lstrip().lower()
    if resp[0] == 'y':
	for username in puser:
	    print >> sys.stderr, 'Removing %s from list...' % username
	    delete_user(user, list, username, client)


def main():
    parser = twlib.CmdlineParser(desc='Check a Twitter list for protected users I\'m not following.')
    parser.add_option('-l', '--login', action='store_true', 
	    dest='login', default=False, help='Force OAuth login')
    parser.add_param('user', help="User name")
    parser.add_param('list', help="List name")
    args = parser.do_parse()
    
    client = twlib.init_oauth(args.login)

    puser = get_pages(args.user, args.list, client)

    ask_delete(args.user, args.list, puser, client)


if __name__ == '__main__':
    main()

# vim:set tw=0:

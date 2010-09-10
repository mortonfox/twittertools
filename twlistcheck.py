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
    Prints out the list of users.
    """
    jsn = twlib.parse_json(str)

    cursor = jsn['next_cursor']

#     pp = pprint.PrettyPrinter(indent=4)
#     pp.pprint(jsn)

    for user in jsn['users']:
	global count

	if user['protected'] and not user['following']:
	    count += 1
	    print "%d: %s %s" % (count, user['id'], user['screen_name'])

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
    parser = twlib.CmdlineParser(desc='Check a Twitter list for protected users I\'m not following.')
    parser.add_option('-l', '--login', action='store_true', 
	    dest='login', default=False, help='Force OAuth login')
    parser.add_param('user', help="User name")
    parser.add_param('list', help="List name")
    args = parser.do_parse()
    
    client = twlib.init_oauth(args.login)

    get_pages(args.user, args.list, client)


if __name__ == '__main__':
    main()

# vim:set tw=0:

"""
twlistcheck.py - Check Twitter list for protected users whom I'm not following.

Author: Po Shan Cheah http://mortonfox.com

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
            print("%d: %s %s" % (count, user['id'], user['screen_name']))
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
        print("Getting %s/%s list members page %s..." % (
                user, list, page), file=sys.stderr)

        result = twlib.twitter_retry(client, 'get',
                path='/1.1/lists/members.json',
                params = { 
                    'owner_screen_name' : user, 
                    'slug' : list, 
                    'cursor' : str(cursor)
                })

        ( cursor, puser2 ) = process_result(result)

        puser += puser2

        if cursor == 0: break

        time.sleep(1)

    return puser


def delete_user(user, list, username, client):
    """
    Remove a user from a list.
    """
    result = twlib.twitter_retry(client, 'post',
            path = '/1.1/lists/members/destroy.json',
            params = {
                'slug' : list,
                'owner_screen_name' : user,
                'screen_name' : username,
            })
    #print result

    time.sleep(1)


def ask_delete(user, list, puser, client):
    """
    Given a list of protected but non-followed users, ask whether to remove
    them from list.
    """
    if len(puser) == 0:
        print("None found.")
        return

    print('The following users are protected but not followed:', file=sys.stderr)
    for u in puser:
        print('  ' + u, file=sys.stderr)
    print('Remove them from list? (y/n) ', end=' ', file=sys.stderr)

    resp = input().lstrip().lower()
    if resp[0] == 'y':
        for username in puser:
            print('Removing %s from list...' % username, file=sys.stderr)
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

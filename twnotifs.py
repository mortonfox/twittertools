"""
twnotifs.py - Show users for whom you have phone notifications.

Author: Po Shan Cheah http://mortonfox.com

"""

import sys
import time
import pprint
import twlib

def get_friends(client):
    """
    Iterate through friends list of authenticated user.
    """
    page = 0
    cursor = -1
    flist = {}

    while True:
        page += 1
        print("Getting friends list - page %d..." % page, file=sys.stderr)

        result = twlib.twitter_retry(client, 'get',
                path='/1.1/friends/ids.json',
                params = { "cursor" : str(cursor) } )

        jsn = twlib.parse_json(result)

        cursor = jsn['next_cursor']

#       pp = pprint.PrettyPrinter(indent=4)
#       pp.pprint(jsn)

        idlist = jsn['ids']

        for i in range(0, len(idlist), 100):
            print("User lookup for %d to %d..." % (i, i+100-1), file=sys.stderr)
            idsublist = idlist[i:i+100]
            get_notif(client, idsublist)

        if cursor == 0: break

        time.sleep(1)

    return 


def get_notif(client, userlist):
    """
    Look up a list of up to 100 user IDs.
    Prints out screen names of users on which notifications are enabled.
    """
    users = ','.join([str(x) for x in userlist])
    result = twlib.twitter_retry(client, 'get',
            path = '/1.1/users/lookup.json',
            params = { 'user_id' : users })
    jsn = twlib.parse_json(result)

#     pp = pprint.PrettyPrinter(indent=4)
#     pp.pprint(jsn)

    for user in jsn:
        if user['notifications']:
            print(user['screen_name'])

    time.sleep(1)


def main():
    parser = twlib.CmdlineParser(desc='Show phone notifications')
    parser.add_option('-l', '--login', action='store_true', 
            dest='login', default=False, help='Force OAuth login')
    args = parser.do_parse()
    
    client = twlib.init_oauth(args.login)
    get_friends(client)

if __name__ == '__main__':
    main()

# vim:set tw=0:

"""
twretweet.py - Show users for whom you have turned off retweets.

Author: Po Shan Cheah http://mortonfox.com

"""

import sys
import time
import pprint
import twlib
import urllib.request, urllib.error, urllib.parse

def get_no_retweets(client):
    """
    Get a list of user IDs for which you have turned off retweets.
    """
    result = twlib.twitter_retry(client, 'get',
            path='/1.1/friendships/no_retweets/ids.json',
            params = { } )

    jsn = twlib.parse_json(result)

#     pp = pprint.PrettyPrinter(indent=4)
#     pp.pprint(jsn)

    idlist = jsn

    for i in range(0, len(idlist), 100):
        print("User lookup for %d to %d..." % (i, i+100-1), file=sys.stderr)
        idsublist = idlist[i:i+100]
        get_usernames(client, idsublist)

    return 


def get_usernames(client, userlist):
    """
    Look up a list of up to 100 user IDs.
    Prints out screen names of users.
    """
    if not userlist:
        return

    users = ','.join([str(x) for x in userlist])
    
    try:
        result = twlib.twitter_retry(client, 'get',
                path = '/1.1/users/lookup.json',
                params = { 'user_id' : users })
        jsn = twlib.parse_json(result)

    #     pp = pprint.PrettyPrinter(indent=4)
    #     pp.pprint(jsn)

        for user in jsn:
            if user['following']:
                print(user['screen_name'])

    except urllib.error.HTTPError as httperr:
        print('Error looking up users: %s' % str(httperr), file=sys.stderr)
        jsn = twlib.parse_json(httperr.read())
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(jsn)


    time.sleep(1)


def main():
    parser = twlib.CmdlineParser(desc='Show disabled retweets')
    parser.add_option('-l', '--login', action='store_true', 
            dest='login', default=False, help='Force OAuth login')
    args = parser.do_parse()
    
    client = twlib.init_oauth(args.login)
    get_no_retweets(client)

if __name__ == '__main__':
    main()

# vim:set tw=0:

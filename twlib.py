"""
twlib.py - Module containing some shared functions.

Author: Po Shan Cheah http://mortonfox.com
"""

import json
def parse_json(s):
    return json.loads(s)

import oauthConsumer
import webbrowser
import sys

OAUTH_FILENAME = 'oauth.key'

CONSUMER_KEY = '12372339LkteH0k9UIhgyA'
CONSUMER_SECRET = '8X5MGxZ0MPeSdaIZd8vdNVuOE6rCL28eZPzAM66To'

REQUEST_URL = "https://api.twitter.com/oauth/request_token" 
ACCESS_URL = "https://api.twitter.com/oauth/access_token" 
AUTHORIZE_URL ="https://api.twitter.com/oauth/authorize" 

def init_oauth(force_login=False):
    """
    Log in to OAuth.
    Reads the access token and secret from a file if available.
    Otherwise, does the required authentication.

    Args:
        force_login
        If True, then redo the OAuth handshake even if there is a saved
        access token. Default is False.

    Returns the client object.
    """
    c = oauthConsumer.Client(
            key = CONSUMER_KEY,
            secret = CONSUMER_SECRET,
            requestTokenURL = REQUEST_URL,
            accessTokenURL = ACCESS_URL, 
            authorizeURL = AUTHORIZE_URL, 
            callbackURL = "oob",
            useHttps = True)

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

        print("Enter PIN: ", end=' ', file=sys.stderr)
        pin = input()

        sessionInfo = c.requestSession(c._requestToken, pin)

        oauth_file = open(OAUTH_FILENAME, "w")
        oauth_file.write(c._sessionToken + "\n")
        oauth_file.write(c._sessionSecret + "\n")
        oauth_file.close()

    return c


import urllib.request, urllib.error, urllib.parse
import time
import pprint
import io

def pprint_to_str(obj):
    """
    Pretty print to a string buffer then return the string.
    """
    sb = io.StringIO()
    pp = pprint.pprint(obj, sb, 4)
    return sb.getvalue()

def twitter_retry(client, method, path, params):
    """
    Call the Twitter API with exponential back-off retries in the event of
    API failure.

    Args:
    client - client object from init_oauth()
    method - should be "get" or "post"
    path - API request path
    params - API params
    """
    retry_count = 0
    retry_delay = 0
    exc = None

    while True:
        do_retry = False

        try:
            listreq = client.createRequest(path = path)
            if method == "post":
                result = listreq.post(params = params)
            else:
                result = listreq.get(params = params)
            return result

        except urllib.error.HTTPError as e:
            #print >> sys.stderr, e.code
            #print >> sys.stderr, e.read()
            do_retry = e.code >= 500
            exc = e

        except urllib.error.URLError as e:
            #print >> sys.stderr, e.reason
            do_retry = True
            exc = e

        if do_retry:
            if retry_count < 5:
                retry_count += 1
                retry_delay = retry_delay * 2 + 1

                print("Retrying in %d seconds..." % retry_delay, file=sys.stderr)
                time.sleep(retry_delay)
                continue

        raise exc

use_optparse = False
try:
    import argparse
except ImportError:
    import optparse
    use_optparse = True

class CmdlineParser:
    """
    Wrapper for optparse and argparse. Offers a neutral interface that supports
    both command-line parsing modules and uses whichever one is available.
    """
    def __init__(self, desc, epilog = ''):
        self.desc = desc
        self.epilog = epilog
        self.optionlist = []
        self.paramlist = []

    def add_option(self, *parg, **karg):
        self.optionlist += [ (parg, karg) ]

    def add_param(self, pname, help):
        self.paramlist += [ (pname, help) ]

    def do_parse(self):
        if use_optparse:
            usagestr = 'usage: %prog [options] ' + \
                    ' '.join([x[0] for x in self.paramlist])

            epilog = self.epilog
                    
            if len(self.paramlist) > 0:
                epilog += '\n\nPositional arguments: ' + \
                        ', '.join([x[0] + ' = ' + x[1] 
                            for x in self.paramlist])

            parser = optparse.OptionParser(
                usage = usagestr, 
                description = self.desc,
                epilog = epilog)

            for opt in self.optionlist:
                parser.add_option(*opt[0], **opt[1])

            (options, args) = parser.parse_args()

            if len(args) < len(self.paramlist):
                parser.error('too few arguments')

            for i in range(len(self.paramlist)):
                setattr(options, self.paramlist[i][0], args[i])
            return options

        else:
            parser = argparse.ArgumentParser(description = self.desc, epilog = self.epilog)

            for opt in self.optionlist:
                parser.add_argument(*opt[0], **opt[1])

            for opt in self.paramlist:
                parser.add_argument(opt[0], help=opt[1])

            args = parser.parse_args()

            return args


if __name__ == '__main__':
    pass

# vim:set tw=0:

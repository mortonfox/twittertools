"""
twlib.py - Module containing some shared functions.
"""

use_simplejson = False
try:
    import json
except ImportError:
    import simplejson
    use_simplejson = True


def parse_json(s):
    """
    Parse JSON string. This will work whether we have the simplejson or the
    json library module.
    """
    if use_simplejson:
	return simplejson.loads(s)
    else:
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
    """
    c = oauthConsumer.Client(
	    key = CONSUMER_KEY,
	    secret = CONSUMER_SECRET,
	    requestTokenURL = REQUEST_URL,
	    accessTokenURL = ACCESS_URL, 
	    authorizeURL = AUTHORIZE_URL, 
	    callbackURL = "oob")

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


use_optparse = False
try:
    import argparse
except ImportError:
    import optparse
    use_optparse = True

class CmdlineParser:
    def __init__(self, desc):
	self.desc = desc
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
		    
	    paramhelp = None
	    if len(self.paramlist) > 0:
		paramhelp = 'Positional arguments: ' + \
			', '.join([x[0] + ' = ' + x[1] 
			    for x in self.paramlist])

	    parser = optparse.OptionParser(
		    usage = usagestr, 
		    description = self.desc,
		    epilog = paramhelp)

	    for opt in self.optionlist:
		parser.add_option(*opt[0], **opt[1])

	    (options, args) = parser.parse_args()

	    if len(args) < len(self.paramlist):
		parser.error('too few arguments')

	    for i in range(len(self.paramlist)):
		setattr(options, self.paramlist[i][0], args[i])
	    return options

	else:
	    parser = argparse.ArgumentParser(description = self.desc)

	    for opt in self.optionlist:
		parser.add_argument(*opt[0], **opt[1])

	    for opt in self.paramlist:
		parser.add_argument(opt[0], help=opt[1])

	    args = parser.parse_args()

	    return args


if __name__ == '__main__':
    pass

# vim:set tw=0:

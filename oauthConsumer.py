"""
The MIT License

Copyright (c) 2010 AppHacker apphacker@gmail.com

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.



pyoauthcon

ABOUT

pyoauthconsumer is a client only implementation of the Oauth Spec
(The OAuth Core 1.0 Protocol draft-hammer-oauth-08)
http://tools.ietf.org/html/draft-hammer-oauth-08

Assumes HMAC-SHA1 signature method, other methods not yet supported

USAGE

Create an instance of a client using your credentials from the Server

Use the client to:

#1 request a temporary token and get the authorization request URL to present to the resource owner
#2 request a session
#3 create requests

Use requests to:

#1 create a request instance for each type of request
#2 reuse that same request instance for subsequent requests, changing the parameters as needed

EXAMPLE

(using Twitter)

>>> c = oauthConsumer.Client( consumerKey, consumerSecret, requestTokenURL, accessTokenURL, authorizeURL, "http://example.com/check" )
>>> authURL =  c.requestAuth( )
>>> print authURL
https://twitter.com/oauth/authorize?oauth_token=rLyOuySbpY4yOlk5BVNxAa6bnG861G20S91jZB7PXaA
>>> sessionInfo = c.requestSession( oauth_token, oauth_verifier )
>>> print sessionInfo
oauth_token=20687908-snoIXOqT7StBdYtyeatV0fAzxLTB0DYklIgBh8klx&oauth_token_secret=hPxakZ3tztpiFaxulcHK9VfkCiJ4PIsL40mc9tfw&user_id=20687908&screen_name=apphacker
>>> c._sessionSecret
'hPxakZ3tztpiFaxulcHK9VfkCiJ4PIsL40mc9tfw'
>>> c._sessionToken
'20687908-snoIXOqT7StBdYtyeatV0fAzxLTB0DYklIgBh8klx'

Now make requests via createRequest

>>> update = c.createRequest( path="/statuses/update.json" )
>>> updateResp =  update.post(params = { "status":"testing pyoauthconsumer oauth client python library I'm working on" } )
>>> print updateResp
{"truncated":false, ... }

etc.

"""

import urllib2
import urllib
from urlparse import urlparse
from random import getrandbits
from time import time
import copy
import hmac
import hashlib
import base64
import sys

# from google.appengine.api import urlfetch

class Client ( object ):

  def __init__(self, key, secret, requestTokenURL, accessTokenURL,
	  authorizeURL, callbackURL, host=None, useHttps=False ):
    """
      Initialize the client

      Arguments:

      key - the client key
      secret - the client secret, not the session or request secret
      requestTokenURL - the url this client instance will visit to request temporary oauth token and secret
      accessTokenURL - the url this client instance will visit to request a permanent session oauth token and secret
      authorizeURL - the url to which this client instance will return with oauth_token appended to give to the resource owner to authorize access
      callbackURL - the url to provide to the server to let your program know that a user has authorized the client
      host - optional argument, probably better to ignore it
      useHttps - if True, use https:// when making requests. Otherwise, use http://

      If you already have a session token and session secret, after creating an instance use the setSession method instead of requesting
      a new session from the user!

      If token and session secret are expired urlib2 will probably raise a 401 Not Authorized error which you'll need to handle. How
      a resource provider/server handles an expired session is not well defined.

    """
    self._key = key
    self._secret = secret
    self._sessionToken = None
    self._sessionSecret = None
    self._requestToken = None
    self._requestSecret = None
    self._requestTokenURL = urlparse( requestTokenURL )
    self._accessTokenURL = urlparse( accessTokenURL )
    self._authorizeURL = urlparse( authorizeURL )
    self._callbackURL = callbackURL
    if not host:
      self._host = self._requestTokenURL.netloc
    else:
      self._host = host
    self._useHttps = useHttps

  def setSession ( self, token, secret ):
    self._sessionToken = token
    self._sessionSecret = secret

  def getSessionToken(self):
      return self._sessionToken

  def getSessionSecret(self):
      return self._sessionSecret

  def requestAuth ( self ):
    """
      Request Oauth temporary request token and secret
    """
    obj = self
    params = {
      "oauth_callback": self._callbackURL
    }
    req = Request( self._key, self._secret, "", params=params,
	    path=self._requestTokenURL.path,
	    host=self._requestTokenURL.netloc,
	    useHttps=self._useHttps )
    return self.handleRequestAuth( req.post( ) )

  def handleRequestAuth ( self, data ):
    parts = data.split( "&" )
    for part in parts:
      subparts = part.split( "=" )
      if subparts[ 0 ] == "oauth_token":
        self._requestToken = subparts[ 1 ]
      elif subparts[ 0 ] == "oauth_token_secret":
        self._requestSecret = subparts[ 1 ]
    return self.createAuthRequestURL( self._authorizeURL.geturl( ), self._requestToken )

  def createAuthRequestURL ( self, authorizeURL, token ):
    sep = "?"
    #Assume only one ? in a URL ever and no #:
    if authorizeURL.find( "#" ) != -1:
      raise OauthException( "Hash not supported for authorize URL" )
    if authorizeURL.find( sep ) != -1:
      sep = "&"
    return "%s%soauth_token=%s" % ( authorizeURL, sep, token )

  def getRequestURL ( self ):
    """
      Get the authorization request URL to give the user, only valid after calling requestAuth and before requestSession
    """
    if self._requestToken:
      return self.createAuthRequestURL( self._authorizeURL.geturl( ), self._requestToken )
    else:
      raise OauthException( "No request Token available" )

  def getRequestToken ( self ):
    return self._requestToken

  def getRequestSecret ( self ):
    return self._requestSecret

  def setRequestSession ( self, token, secret ):
    """
      Use this method to update your client with a request already in progress
    """
    self._requestToken = token
    self._requestSecret = secret

  def requestSession ( self, oauth_token, oauth_verifier ):
    """
      Request Oauth temporary request token and secret

      Arguments:

      oauth_token: token received from auth request, if it doesn't match existing temporary token session request fails
      oauth_verifier: verifcation id received from auth request

    """
    if not self._requestToken:
      raise OauthException( "No request Token" )
    if self._requestToken != oauth_token:
      raise OauthException( "provided oauth_token and stored request token do not match" )
    obj = self
    params = {
      "oauth_verifier": oauth_verifier
    }
    req = Request( self._key, self._secret, oauth_token,
	    sessionSecret = self._requestSecret,
	    params=params, path=self._accessTokenURL.path,
	    host=self._accessTokenURL.netloc,
	    useHttps=self._useHttps )
    return self.handleRequestSession( req.post( ) )

  def handleRequestSession ( self, data ):
    parts = data.split( "&" )
    params = {}
    for part in parts:
      subparts = part.split( "=" )
      if subparts[ 0 ] == "oauth_token":
        self._sessionToken = subparts[ 1 ]
      elif subparts[ 0 ] == "oauth_token_secret":
        self._sessionSecret = subparts[ 1 ]
      else:
        params[ subparts[ 0 ] ] = subparts[ 1 ]
    self._requestToken = None
    self._requestSecret = None
    return data

  def createRequest ( self, path=None, params=None, host=None ):
    if not host:
      host = self._host
    if self._sessionToken:
      return Request( self._key, self._secret, self._sessionToken ,
	      path=path, sessionSecret=self._sessionSecret, params=params,
	      host=host, useHttps=self._useHttps )
    else:
      raise OauthException( "No Session Token" )

class Request ( object ):

  POST = "POST"
  GET = "GET"

  def __init__( self, key, secret, token, sessionSecret="", path=None,
	  host=None, params=None, useHttps=False ):
    self.host = host
    self.path = path
    self.params = {}
    self.params = self.addParams( params )
    self._key = key
    self._secret = secret
    self._sessionSecret = sessionSecret
    self._token = token
    self._protocol = 'https' if useHttps else 'http'

  def addParams ( self, params ):
    returnParams = copy.deepcopy( self.params )
    if params:
      for key in params:
        returnParams[ key ] = copy.deepcopy( params[ key ] )
    return returnParams

  def post ( self, path=None, host=None, params=None ):
    return self.makeRequest( self.POST, path=path, host=host, params=params )

  def get ( self, path=None, host=None, params=None ):
    return self.makeRequest( self.GET, path=path, host=host, params=params )

  def makeRequest ( self, kind, path=None, host=None, params=None ):
    params = self.addParams( params )
    if not path:
      path = self.path
    if not host:
      host = self.host
    params.update( {
      'oauth_timestamp': str( int( time( ) ) ),
      'oauth_consumer_key': self._key,
      'oauth_signature_method': 'HMAC-SHA1',
      'oauth_nonce': str( getrandbits( 64 ) ),
      'oauth_version': '1.0',
      'oauth_token': self._token,
    } )
    if len( path) and path[ 0 ] != '/':
      path = '/' + path
    signature = self.createSignature( host, path, params, kind )
    params.update( { "oauth_signature": signature } )
    url = "%s://%s%s" % ( self._protocol, host, path )
    # print >> sys.stderr, "url: %s" % url
    _params = { }
    for k, v in params.iteritems( ):
        _params[ str( k ).encode( 'utf-8' ) ] =  v.encode( 'utf-8' )
    params = _params
    data = urllib.urlencode( params )
    if kind == self.POST:
      req = urllib2.Request( url, data )
      # resp = urlfetch.fetch(url, payload=data, method=urlfetch.POST)
    else:
      req = urllib2.Request( "%s?%s" % ( url, data ) )
      # resp = urlfetch.fetch( "%s?%s" % ( url, data ), method=urlfetch.GET)
    """
    #DEBUG WITH HTTP PROXY LISTENER:
    proxy_handler = urllib2.ProxyHandler( { 'http':'127.0.0.1:8888' } )
    opener = urllib2.build_opener( proxy_handler )
    urllib2.install_opener( opener )
    """
    resp = urllib2.urlopen( req )
    result = resp.read( )
    # result = resp.content
    return result

  def createSignature ( self, host, path, params, kind ):
    values = self.makeValues( params )
    values = self.getOauthEncodedValues( values )
    values.sort( )
    sig_ = "%s&%s&%s" % (
        kind,
        self.oauthEncode( "%s://%s%s" % ( self._protocol, host, path ), '' ),
        self.oauthEncode( "&".join( ( "=".join( v ) for v in values ) ), '' )
    )
    # print >> sys.stderr, "sig_: %s" % sig_
    hashKey = "&".join( ( self._secret, self._sessionSecret ) )
    # print >> sys.stderr, "hashKey: %s" % hashKey
    hash = hmac.new( hashKey, sig_, hashlib.sha1 )
    return base64.b64encode( hash.digest( ) )

  def oauthEncode( self, binStr, safe ):
      return urllib.quote( binStr.encode( 'utf-8' ), safe )

  def getOauthEncodedValues( self, values ):
      #returns new list with oauth encoded values
      return [ ( self.oauthEncode( k, '' ),self.oauthEncode( v, '' ) ) for k, v in values ]

  def makeValues( self, params ):
    values = []
    for key in params:
      values.append( ( str( key ), params[ key ] )  )
    return values

class OauthException ( Exception ):
  def __init__ ( self, value ):
    self.value = value
  def __str__ ( self ):
    return repr( "OauthException: %s" % self.value )



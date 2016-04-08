# twittertools

This is a set of command-line utilities for Twitter.

* twfriend.py - Compares your following and followers and produces 3 lists:
    1. mutual followers
    1. users you're following but aren't following you back
    1. followers you aren't following back
* twlistdump.py - Prints out all the members of a list.
* twlistcheck.py - Checks a list for protected users whom you aren't following.
  Optionally, remove those users from the list. (because you won't see their
  tweets in the list timeline anyway)
* twnotifs.py - Prints out users for whom you have phone notifications turned on.
* twretweet.py - Prints out users for whom you have turned off retweets.

## twfriend.py

By default, twfriend displays all 3 friend/follow categories. You can control
what twfriend displays using the -m, -r, and -o options. The -l option forces
twfriend to perform another OAuth login to get a fresh token.

    bash-4.3$ python twfriend.py -h
    usage: twfriend.py [-h] [-l] [-m] [-r] [-o]

    Categorize Twitter friends/followers.

    optional arguments:
    -h, --help            show this help message and exit
    -l, --login           Force OAuth login
    -m, --mutual          Show mutual friends
    -r, --only-friends    Show only-friends
    -o, --only-followers  Show only-followers

    If none of -m/-r/-o are specified, display all 3 categories.
    bash-4.3$


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


## twlistcheck.py

twlistcheck checks a Twitter list for protected users that you aren't
following. Those users would be easy candidates to cut from the list since you
can't see their tweets anyway. After displaying these users, twlistcheck can
optionally remove those users from the list after a confirmation prompt.

The -l option forces twlistcheck to perform another OAuth login to get a fresh token.

    bash-4.3$ python twlistcheck.py -h
    usage: twlistcheck.py [-h] [-l] user list

    Check a Twitter list for protected users I'm not following.

    positional arguments:
    user         User name
    list         List name

    optional arguments:
    -h, --help   show this help message and exit
    -l, --login  Force OAuth login
    bash-4.3$

## twlistdump.py

twlistdump displays all the members of a list. You could use it to backup a
list, for example, although there is no tool yet to restore a list saved in
this way.

The -l option forces twlistdump to perform another OAuth login to get a fresh token.

    bash-4.3$ python twlistdump.py -h
    usage: twlistdump.py [-h] [-l] user list

    Dump a Twitter list.

    positional arguments:
    user         User name
    list         List name

    optional arguments:
    -h, --help   show this help message and exit
    -l, --login  Force OAuth login
    bash-4.3$

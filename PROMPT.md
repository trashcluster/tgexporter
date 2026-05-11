Make an app that uses the official tdlib library for telegram to take out all user data programatically.

To not overload the telegram takeout API I want you to map all my conversations since the beginning and only export the delta.

The app should store in a DB (sqlite by default but can be made postgres compatible) all the messages IDs for each groups.

The DB should create relations for each groups, create relations between users in each groups and their associated contacts. The relation should work between groups.

Pictures, voice messages, videos and other files should be downloaded as well.



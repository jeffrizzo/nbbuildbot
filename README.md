# nbbuildbot
Buildbot configuration for test-building the NetBSD kernel after changes to src/sys.

This configuration is in use with Buildbot 0.8 and the results can be seen at
http://build.tastylime.net/ .  This is a very basic config, which currently
builds 5 different kernels, and is triggered by commits to CVS.

In addition to the files in this repo, a file called "secrets.json" is required,
to supply credentials for the build slaves and for twitter.py .

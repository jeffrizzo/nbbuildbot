"""
Tweet out build statuses
"""

import tweepy

from buildbot.status.base import StatusReceiverMultiService
from buildbot.status.builder import Results, SUCCESS

from twisted.python import log

class TwitterStatusPush(StatusReceiverMultiService):

  def __init__(self, authDict, **kwargs):
      StatusReceiverMultiService.__init__(self)

      self.auth = tweepy.OAuthHandler(authDict['consumer_key'], authDict['consumer_secret'])
      self.auth.set_access_token(authDict['access_token'], authDict['access_token_secret'])
      self.api = tweepy.API(self.auth)

      self.watched = []

  def setServiceParent(self, parent):
      StatusReceiverMultiService.setServiceParent(self, parent)
      log.msg('setServiceParent')
      self.master_status = self.parent
      self.master_status.subscribe(self)
      self.master = self.master_status.master

  def disownServiceParent(self):
      log.msg('disownServiceParent')
      self.master_status.unsubscribe(self)
      self.master_status = None
      for w in self.watched:
          w.unsubscribe(self)
      return StatusReceiverMultiService.disownServiceParent(self)

  def builderAdded(self, name, builder):
      log.msg('builderAdded: %s' % name)
      self.watched.append(builder)
      return self  # subscribe to this builder

  def builderChangedState(self, builderName, state):
      log.msg('builderChangedState: %s %s' % (builderName, state))

  def buildStarted(self, builderName, build):
      url = self.master_status.getURLForThing(build)
      message = "started: %s %s" % (builderName, url)
      log.msg('buildStarted: %s' % message)
      self.api.update_status(message)

  def buildFinished(self, builderName, build, result):
      url = self.master_status.getURLForThing(build)
      message = "finished: %s %s %s" % (builderName, Results[result].upper(), url)
      log.msg('buildFinished: %s' % message)
      self.api.update_status(message)

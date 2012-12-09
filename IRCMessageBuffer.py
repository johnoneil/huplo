# vim: set ts=2 expandtab:

#******************************************************************************
#
# IRCMessageBuffer.py
# John O'Neil
# Wednesday, December 5th 2012
#
# Simple buffer of IRC messages (nick,vhost,msg etc.) that will be rendered
# atop a video in an arbitrary way.
#
#******************************************************************************

class IRCMessage(object):
  def __init__(self, nick, vhost, msg ):
    self.nick = nick
    self.vhost = vhost
    self.msg = msg

class IRCMessageBuffer(list):
  def __init__(self, bufferlength = 5):
    super(IRCMessageBuffer, self).__init__()
    self.bufferlength = bufferlength

  def push(self,message):
    super(IRCMessageBuffer,self).insert(0, message)
    if( len(self) > self.bufferlength ):
      super(IRCMessageBuffer,self).pop()

  def message(self,index):
    return self.buffer[index]


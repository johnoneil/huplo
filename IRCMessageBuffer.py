#!/usr/bin/python

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

class IRCMessage:
  def __init__(self, nick, vhost, msg ):
    self.nick = nick
    self.vhost = vhost
    self.msg = msg

class IRCMessageBuffer:
  def __init__(self, bufferlength = 5):
    self.buffer = []
    self.bufferlength = bufferlength

  def Push(self,message):
    self.buffer.append(message)
    if( len(self.buffer) > self.bufferlength ):
      self.buffer.pop(0)

  def Clear(self):
    self.buffer.clear()

  def Message(self,index):
    return self.buffer[index]

  def __len__(self):
    return len(self.buffer)

  def __getitem__(self, index):
    return self.buffer[index]

  def Pop(self,item=0):
    return self.buffer.pop(item)


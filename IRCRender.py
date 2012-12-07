#!/usr/bin/python

# vim: set ts=2 expandtab:

#******************************************************************************
#
# IRCRender.py
# John O'Neil
# Wednesday, December 5th 2012
# 
# classes that collect (and buffer in their own way) IRC messages
# and render their buffer to a cairo surface when asked to
#
#******************************************************************************

from IRCMessageBuffer import IRCMessage
from IRCMessageBuffer import IRCMessageBuffer
from math import pi

class Simple:
  def __init__(self):
    self.buffer = IRCMessageBuffer()
    self.lastTimestamp = 0
  def Push(self, msg ):
    self.buffer.Push(msg)
  def OnDraw(self,ctx,width,height,timestamp,deltaT):
    ul_x = width/16
    ul_y = 2*height/3
    for entry in self.buffer:
      nick = entry.nick
      msg = entry.nick + ":" + entry.msg
      ctx.set_source_rgba (1.0, 1.0, 1.0, 1.0)
      ctx.set_font_size(24)
      extents = ctx.text_extents(msg)
      ctx.move_to( ul_x+2,ul_y+2 )
      ctx.set_source_rgb(0,0,0)
      ctx.show_text(msg)
      ctx.move_to( ul_x,ul_y )
      ctx.set_source_rgb(1,1,0)
      ctx.show_text(msg)
      ul_y = ul_y + 1.25 * extents[3]

class TickerIRCMsg( IRCMessage ):
  def __init__( self, message ):
    IRCMessage.__init__(self,message.nick,message.vhost,message.msg )
    self.x = 0
    self.y = 0
    self.w = 0

class Ticker:
  def __init__(self):
    self.buffer = IRCMessageBuffer( bufferlength = 10 )
    self.current_w = 0
    self.current_h = 0

  def Push(self, msg ):
    newmsg = TickerIRCMsg( msg )
    newmsg.x = self.current_w
    newmsg.y = 6 * self.current_h / 8
    bufferlength = len( self.buffer )
    if( bufferlength > 0 ):
      lastEntry = self.buffer[bufferlength - 1]
      if( lastEntry.x + lastEntry.w + 20 > self.current_w ):
        newmsg.x = lastEntry.x + lastEntry.w + 20
    self.buffer.Push( newmsg )
  def OnDraw(self,ctx,width,height,timestamp,deltaT):
    self.current_w = width
    self.current_h = height
    #move the ul_x corner to the left a little according to deltaT
    #distance = speed * time = pixels/second * dt
    #here, I want a given character to traverse the screen in 4 seconds. 1e-9 scales nanoseconds (dt) to seconds.
    delta_x = ( width / 6.0 ) * deltaT * 1e-9

    for entry in self.buffer:
      entry.x = entry.x - delta_x

    buffercopy = self.buffer[:]
    for (ientry,entry) in enumerate( buffercopy ):
      nick = entry.nick
      msg = entry.nick + ":" + entry.msg
      ctx.set_source_rgba (1.0, 1.0, 1.0, 1.0)
      ctx.set_font_size(24)
      extents = ctx.text_extents(msg)
      entry.w = extents[2]
      ctx.move_to( entry.x + 2, entry.y + 2 )
      ctx.set_source_rgb(0,0,0)
      ctx.show_text(msg)
      ctx.move_to( entry.x , entry.y )
      ctx.set_source_rgb(1,1,0)
      ctx.show_text(msg)
      if( entry.x + entry.w < 0 ):
        self.buffer.Pop( ientry )





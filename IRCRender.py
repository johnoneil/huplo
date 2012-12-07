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

class Ticker:
  def __init__(self):
    self.buffer = IRCMessageBuffer()
    self.lastTimestamp = 0
    self.ul_x = -1
    self.ul_y = -1
  def Push(self, msg ):
    self.buffer.Push(msg)
  def OnDraw(self,ctx,width,height,timestamp,deltaT):
    if( self.ul_y < 0 ):
      self.ul_x = width
      self.ul_y = 2*height/3

    #pop the topmost buffered message?
    if( len(self.buffer) > 0 ):
      entry = self.buffer[0]
      msg = msg = entry.nick + ":" + entry.msg
      ctx.set_font_size(24)
      extents = ctx.text_extents(msg)
      width = extents[2]
      if( self.ul_x + width < 0 ):
        self.buffer.Pop()
        self.ul_x = self.ul_x + width
    else:
      self.ul_x = width
      return
    
    current_msg_ul_x = self.ul_x
    current_msg_ul_y = self.ul_y
    for entry in self.buffer:
      nick = entry.nick
      msg = entry.nick + ":" + entry.msg
      ctx.set_source_rgba (1.0, 1.0, 1.0, 1.0)
      ctx.set_font_size(24)
      extents = ctx.text_extents(msg)
      ctx.move_to( current_msg_ul_x+2,current_msg_ul_y+2 )
      ctx.set_source_rgb(0,0,0)
      ctx.show_text(msg)
      ctx.move_to( current_msg_ul_x,current_msg_ul_y )
      ctx.set_source_rgb(1,1,0)
      ctx.show_text(msg)
      current_msg_ul_x = current_msg_ul_x + extents[2]

    #move the ul_x corner to the left a little according to deltaT
    #distance = speed * time = pixels/second * dt
    #here, I want a given character to traverse the screen in 3 seconds. 1e-9 scales nanoseconds (dt) to seconds.
    delta_x = ( width / 3.0 ) * deltaT * 1e-9
    self.ul_x = self.ul_x - delta_x


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
      #ctx.text_path(msg)
      #ctx.set_line_width(1.5)
      #ctx.set_source_rgb(0,0,0)
      #ctx.stroke_preserve()
      ctx.move_to( ul_x+2,ul_y+2 )
      ctx.set_source_rgb(0,0,0)
      ctx.show_text(msg)
      ctx.move_to( ul_x,ul_y )
      ctx.set_source_rgb(1,1,0)
      ctx.show_text(msg)
      ul_y = ul_y + 1.25 * extents[3]
      #ctx.move_to(center_x - extents[2]/2, center_y + extents[3]/2)


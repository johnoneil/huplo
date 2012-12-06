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
  def Push(self, msg ):
    self.buffer.Push(msg)
  def OnDraw(self,ctx,width,height,framerate):
    if( len(self.buffer) > 0 ):
      center_x = width/4
      center_y = 3*height/4

      # draw a circle
      radius = float (min (width, height)) * 0.25
      ctx.set_source_rgba (0.0, 0.0, 0.0, 0.9)
      ctx.move_to (center_x, center_y)
      ctx.arc (center_x, center_y, radius, 0, 2.0*pi)
      ctx.close_path()
      ctx.fill()
      msg = self.buffer.Message( 0 )
      ctx.set_source_rgba (1.0, 1.0, 1.0, 1.0)
      ctx.set_font_size(0.3 * radius)
      txt = msg.msg
      extents = ctx.text_extents (txt)
      ctx.move_to(center_x - extents[2]/2, center_y + extents[3]/2)
      ctx.text_path(txt)
      ctx.fill()

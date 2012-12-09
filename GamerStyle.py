#!/usr/bin/python

# vim: set ts=2 expandtab:

#******************************************************************************
#
# GamerStyle.py
# John O'Neil
# Saturday, December 8th 2012
# 
# A traditional "Gamer" style IRC overlay onto a video stream
#
#******************************************************************************

from IRCMessageBuffer import IRCMessage
from IRCMessageBuffer import IRCMessageBuffer
from math import pi
import cairo
import pango
import pangocairo

class GamerStyle:
  def __init__(self):
    self.buffer = IRCMessageBuffer()
    self.lastTimestamp = 0
  def Push(self, msg ):
    self.buffer.Push(msg)
  def OnDraw(self,ctx,width,height,timestamp,deltaT):
    pangoCtx = pangocairo.CairoContext(ctx)
    layout = pangoCtx.create_layout()
    layout.set_width( pango.SCALE * (3*width/8) )
    layout.set_alignment(pango.ALIGN_LEFT)
    layout.set_wrap(pango.WRAP_WORD_CHAR)
    layout.set_font_description(pango.FontDescription("Arial 12"))
    layout.set_indent(-1* pango.SCALE * 40 )
    ul_x = width/16
    ul_y = 2*height/3
    totaltext = ""
    for entry in self.buffer:
      nick = entry.nick
      msg = entry.nick + ":" + entry.msg
      totaltext = totaltext + msg + "\n"
      #ctx.set_source_rgba (1.0, 1.0, 1.0, 1.0)
      #ctx.set_font_size(24)
      #extents = ctx.text_extents(msg)
      #ctx.move_to( ul_x+2,ul_y+2 )
    
    #ctx.show_text(msg)
    ctx.move_to( ul_x,ul_y )
    #ctx.set_source_rgb(1,1,0)
    #ctx.show_text(msg)
    #ul_y = ul_y + 1.25 * extents[3]
    layout.set_text(totaltext)
    pangoCtx.update_layout(layout)
    (device_extents,logical_extents) = layout.get_pixel_extents()
    ctx.set_source_rgba(0,0,0,0.4)
    ctx.rectangle(ul_x,ul_y,device_extents[2],device_extents[3])
    ctx.fill()
    ctx.move_to( ul_x,ul_y )
    ctx.set_source_rgb(1,1,0)
    pangoCtx.show_layout(layout)


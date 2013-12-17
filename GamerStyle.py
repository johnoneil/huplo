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
from AnimatedMessageQueue import AnimatedMessageQueue
import cairo
import pango
import pangocairo

class GamerStyle(object):
  def __init__(self):
    self._buffer = []
    self._messages = AnimatedMessageQueue(x = 10, y = 10)
  def push(self, msg ):
    self._buffer.insert(0,msg)
    self._messages.notice(msg.msg)
  def on_draw(self,ctx,width,height,timestamp,deltaT):
    self._messages.update(deltaT)
    self._messages.render(ctx)
    pangoCtx = pangocairo.CairoContext(ctx)
    #layout the messages as follows:
    #nick column is 1/8 total screen width, right justified
    #message column is 3/8 total screen width, left justified
    #top of messages is at 1/2 down the screen
    #left border of messages is 1/32 across the screen
    nick_ul_x = width/32
    nick_ul_y = height/2
    nick_width = width/8
    msg_width = 3*width/8
    gutter_width = 5
    gutter_height = 1
    msg_ul_x = nick_ul_x + nick_width + gutter_width
    msg_ul_y = nick_ul_y
    
    entries_that_fit = 0
    for entry in self._buffer:
      nick = entry.nick
      msg = entry.msg

      nicklayout = pangoCtx.create_layout()
      nicklayout.set_width( pango.SCALE * nick_width )
      nicklayout.set_alignment(pango.ALIGN_RIGHT)
      nicklayout.set_wrap(pango.WRAP_WORD_CHAR)
      nicklayout.set_font_description(pango.FontDescription("Arial 12"))
      nickattrs, nicktext, nickaccel = pango.parse_markup(nick)
      nicklayout.set_attributes( nickattrs )
      nicklayout.set_text( nicktext )
      pangoCtx.update_layout(nicklayout)
      (nick_dextents,nick_lextents) = nicklayout.get_pixel_extents()

      msglayout = pangoCtx.create_layout()
      msglayout.set_width( pango.SCALE * msg_width )
      msglayout.set_alignment(pango.ALIGN_LEFT)
      msglayout.set_wrap(pango.WRAP_WORD_CHAR)
      msglayout.set_font_description(pango.FontDescription("Arial 12"))
      #msglayout.set_indent( pango.SCALE * 25 )
      msgattrs, msgtext, msgaccel = pango.parse_markup(msg)
      msglayout.set_attributes( msgattrs )
      msglayout.set_text( msgtext )
      pangoCtx.update_layout(msglayout)
      (msg_dextents,msg_lextents) = msglayout.get_pixel_extents()

      #the height of the total entry is the greater of the nick and msg heights
      total_height = 0
      if( msg_lextents[3] > nick_lextents[3]):
        total_height = msg_lextents[3]
      else:
        total_height = nick_lextents[3]

      if( nick_ul_y + total_height > height ):
        break
      else:
        entries_that_fit = entries_that_fit + 1
    
      #draw the nick entry
      #ctx.move_to( nick_ul_x,nick_ul_y )
      #ctx.set_source_rgba(0,0,0,0.4)
      #ctx.rectangle(nick_ul_x,nick_ul_y,nick_width,total_height)
      #ctx.fill()
      ctx.move_to( nick_ul_x+1,nick_ul_y+2 )
      ctx.set_source_rgb(0,0,0)
      pangoCtx.show_layout(nicklayout)
      ctx.move_to( nick_ul_x,nick_ul_y )
      ctx.set_source_rgb(1,1,1)
      pangoCtx.show_layout(nicklayout)

      #and draw the msg
      #ctx.move_to( msg_ul_x,msg_ul_y )
      #ctx.set_source_rgba(0,0,0,0.4)
      #ctx.rectangle( msg_ul_x, msg_ul_y, msg_width, total_height)
      #ctx.fill()
      ctx.move_to( msg_ul_x+1,msg_ul_y+2 )
      ctx.set_source_rgb(0,0,0)
      pangoCtx.show_layout(msglayout)
      ctx.move_to( msg_ul_x,msg_ul_y )
      ctx.set_source_rgb(1,1,0)
      pangoCtx.show_layout(msglayout)

      nick_ul_y = nick_ul_y + total_height + gutter_height
      msg_ul_y = nick_ul_y

    #make sure the buffer only keeps entries that fit
    while(len(self._buffer) > entries_that_fit):
      self._buffer.pop()
      



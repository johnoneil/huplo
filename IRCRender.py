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

class Simple(object):
  def __init__(self):
    self.buffer = IRCMessageBuffer()
    self.lastTimestamp = 0
  def push(self, msg ):
    self.buffer.push(msg)
  def on_draw(self,ctx,width,height,timestamp,deltaT):
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

class TickerIRCMsg(IRCMessage):
  def __init__(self, message):
    IRCMessage.__init__(self,message.nick,message.vhost,message.msg )
    self.x = 0
    self.y = 0
    self.w = 0

class Ticker(object):
  def __init__(self):
    self.buffer = IRCMessageBuffer( bufferlength = 10 )
    self.current_w = 0
    self.current_h = 0

  def push(self, msg ):
    newmsg = TickerIRCMsg( msg )
    newmsg.x = self.current_w
    newmsg.y = 7 * self.current_h / 8
    bufferlength = len( self.buffer )
    if( bufferlength > 0 ):
      lastEntry = self.buffer[bufferlength - 1]
      if( lastEntry.x + lastEntry.w + 20 > self.current_w ):
        newmsg.x = lastEntry.x + lastEntry.w + 20
    #as the default behavior for the IRCMessagebuffer is to push to its front,
    #we'll append this new message to the back (i.e. newest messages queued at the end )
    self.buffer.append( newmsg )
  def on_draw(self,ctx,width,height,timestamp,deltaT):
    self.current_w = width
    self.current_h = height
    #we want a font size that is readable for the current window height
    font_height_device = height / 15
    (font_width_user,font_height_user) = ctx.device_to_user_distance(1,font_height_device)
    #move the ul_x corner to the left a little according to deltaT
    #distance = speed * time = pixels/second * dt
    #here, I want a given character to traverse the screen in 4 seconds.
    delta_x = ( width / 6.0 ) * deltaT 

    #draw a shaded background for messages to traverse (f there are any messages )
    if( len( self.buffer ) > 0 ):
      ctx.set_source_rgba (0, 0, 0, 0.5)
      y = 7 * height / 8
      ctx.rectangle ( 0, y - 1.5 * font_height_device, width, 2 * font_height_device )
      ctx.fill()

    for (ientry,entry) in enumerate( self.buffer ):
      entry.x = entry.x - delta_x
      nick = entry.nick
      msg = entry.nick + ":" + entry.msg
      ctx.select_font_face("Arial")
      ctx.set_source_rgba (1.0, 1.0, 1.0, 1.0)
      ctx.set_font_size(font_height_user)
      extents = ctx.text_extents(msg)
      entry.w = extents[2]
      #ctx.move_to( entry.x + 2, entry.y + 2 )
      #ctx.set_source_rgb(0,0,0)
      #ctx.show_text(msg)
      ctx.move_to( entry.x , entry.y )
      ctx.set_source_rgb(1,1,0)
      ctx.show_text(msg)

    if( len(self.buffer) > 0 ):
      entry = self.buffer[0]
      if( entry.x + entry.w < 0 ):
        self.buffer.pop(0)




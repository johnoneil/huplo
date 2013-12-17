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
from color import Color

class DropShadow(object):
  '''
  Drop shadow of certain color beneath text at offset pixels x,y
  '''
  def __init__(self, is_visible=True, x_offset=2, y_offset=2, color=Color.Black):
    self.IsVisible = is_visible
    self.XOffset = x_offset
    self.YOffset = y_offset
    self.Color = color

class Shading(object):
  '''
  Shaded area beneath text of some dimentions
  Meant to make text easier to read
  '''
  def __init__(self, x=0, y=0, w=0, h=0, color=Color(r=0.0, g=0.0, b=0.0, a=0.5), is_visible=True):
    self.X = x
    self.Y = y
    self.W = w
    self.H = h
    self.Color = color
    self.IsVisible=is_visible

  def Draw(self, ctx, width, height, timestamp, deltaT):
    ctx.set_source_rgba(self.Color.R, self.Color.G, self.Color.B, self.Color.A)
    ctx.rectangle ( self.X, self.Y, self.W, self.H)
    ctx.fill()

class Simple(object):
  '''
  Simple non animated mesage queue displayed on screen.
  Newest messages appear on top.
  Does not currently properly wrap messages to bounding box.
  '''
  def __init__(self, x=0, y=0, w=100, h=100, num_entries=10, font_size=24, vertical_spacing=12, color=Color.White, is_visible=True, drop_shadow=DropShadow()):
    self.lastTimestamp = 0
    self.X = x
    self.Y = y
    self.W = w
    self.H = h
    self.buffer = IRCMessageBuffer(bufferlength = num_entries)
    self.Color = color
    self.FontSize = font_size
    self.VerticalSpacing = vertical_spacing
    self.DropShadow = drop_shadow
    self.IsVisible = is_visible
  
  def push(self, msg ):
    self.buffer.push(msg)
  
  def on_draw(self, ctx, width, height, timestamp, deltaT):
    if not self.IsVisible:
      return
    ul_x = self.X
    ul_y = self.Y
    for entry in self.buffer:
      nick = entry.nick
      msg = entry.nick + ":" + entry.msg
      ctx.set_font_size(self.FontSize)
      extents = ctx.text_extents(msg)
      if self.DropShadow.IsVisible:
        ctx.move_to(ul_x+self.DropShadow.XOffset,ul_y+self.DropShadow.YOffset)
        ctx.set_source_rgb(self.DropShadow.Color.R, self.DropShadow.Color.G, self.DropShadow.Color.B)
        ctx.show_text(msg)
      ctx.move_to(ul_x,ul_y)
      ctx.set_source_rgb(self.Color.R, self.Color.G, self.Color.B)
      ctx.show_text(msg)
      ul_y = ul_y + extents[3] + self.VerticalSpacing


class TickerIRCMsg(IRCMessage):
  def __init__(self, message):
    IRCMessage.__init__(self,message.nick,message.vhost,message.msg )
    self.DistanceMoved = 0

class Ticker(object):
  def __init__(self, y=300, scroll_left=True, font_height=24, color=Color.White, is_visible=True, movement=100, drop_shadow=DropShadow()):
    self.buffer = IRCMessageBuffer( bufferlength = 10 )
    self.Y = y
    self.ScrollLeft = scroll_left
    self.FontHeight = font_height
    self.Color = color
    self.Movement = movement
    self.DropShadow = drop_shadow
    self.IsVisible = is_visible
    self.Shading = Shading()

  def push(self, msg):
    newmsg = TickerIRCMsg(msg)
    bufferlength = len(self.buffer)
    self.buffer.append(newmsg)
  def on_draw(self, ctx, width, height, timestamp, deltaT):
    if not self.IsVisible:
      return
    if len(self.buffer)<1:
      return
    #calculate current font dimensions
    entry = self.buffer[0]
    msg = '*** <'+entry.nick+'> : '+entry.msg+' ***'
    ctx.set_font_size(self.FontHeight)
    xbearing, ybearing, msg_width, msg_height, xadvance, yadvance = ctx.text_extents(msg)

    #distance = speed * time = pixels/second * dt
    delta_x = self.Movement*deltaT 

    #draw a shaded background for messages to traverse (if there are any messages )
    if self.Shading.IsVisible:
      self.Shading.X=0
      self.Shading.Y=self.Y+ybearing
      self.Shading.W=width
      self.Shading.H=msg_height
      self.Shading.Draw(ctx, width, height, timestamp, deltaT)

    entry.DistanceMoved+=delta_x
    
    ctx.select_font_face("Arial")
    ctx.set_source_rgba (self.Color.R, self.Color.G, self.Color.B)
 
    current_x = width-entry.DistanceMoved
    if not self.ScrollLeft:
      current_x = width+entry.DistanceMoved-msg_width
    ctx.move_to(current_x, self.Y)
    ctx.show_text(msg)
    if entry.DistanceMoved>msg_width+width:
      self.buffer.pop(0)
      

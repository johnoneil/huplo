#!/usr/bin/python
# vim: set ts=2 expandtab:
"""
Module: ticker.py
Desc: Ticker style text display crawls across screen
Author: John O'Neil
Email: oneil.john@gmail.com
DATE: Monday, Dec 16th 2013
  
""" 
from color import Color
import gobject
import dbus
import dbus.service
import dbus.mainloop.glib
import argparse
from traceback import print_exc
import sys

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


class TickerMsg(object):
  def __init__(self, message):
    self.Message = message
    self.DistanceMoved = 0


class Ticker(object):
  def __init__(self, message, y=300, scroll_left=True, font_height=24, color=Color.White,
    is_visible=True, movement=100, drop_shadow=DropShadow()):
    self.Buffer = []
    self.Y = y
    self.ScrollLeft = scroll_left
    self.FontHeight = font_height
    self.Color = color
    self.Movement = movement
    self.DropShadow = drop_shadow
    self.IsVisible = is_visible
    self.Shading = Shading()
    self.push(message)

  def push(self, msg):
    self.Buffer.append(TickerMsg(msg))

  def on_draw(self, ctx, width, height, timestamp, deltaT):
    if not self.IsVisible:
      return
    if len(self.Buffer)<1:
      return
    #calculate current font dimensions
    entry = self.Buffer[0]
    msg = '*** '+entry.Message+' ***'
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
      if len(self.Buffer)>1:
        self.Buffer.pop(0)
      else:
        entry.DistanceMoved=0


class TickerManager(object):
  def __init__(self):
    self.Tickers = {}
    self.server = TickerServer(self)
  
  def Add(self, message, name='',y=300, scroll_left=True, font_height=24,
    color=Color.White, is_visible=True, movement=100, drop_shadow=DropShadow()):
    self.Tickers[name] = Ticker(message, y, scroll_left, font_height, color, is_visible, movement, drop_shadow)

  def Remove(self, name=''):
    if self.Tickers[name] is not None:
      self.Tickers.pop(name, None)

  def Clear(self):
    self.Tickers.clear()

  def on_draw(self, ctx, width, height, timestamp, deltaT):
    for name, ticker in self.Tickers.iteritems():
      ticker.on_draw(ctx, width, height, timestamp, deltaT)


class TickerServer(dbus.service.Object):

  def __init__(self, manager):
    bus_name = dbus.service.BusName('com.VideoOverlay.Ticker', bus=dbus.SessionBus())
    dbus.service.Object.__init__(self, bus_name, '/TickerServer')
    self.manager = manager
  #def __init__(self, session_bus, object_path, manager):
  #  dbus.service.Object.__init__(self, session_bus, object_path)
  #  self.manager = manager

  @dbus.service.method("com.VideoOverlay.Ticker",
                       in_signature='s', out_signature='')
  def AddTicker(self, json_data):
    print 'Add ticker ' + json_data
    self.manager.Add(json_data)

  @dbus.service.method("com.VideoOverlay.Ticker",
                       in_signature='s', out_signature='')
  def RemoveTicker(self, json_data):
    print 'Remove ticker ' + json_data
    self.manager.Remove(json_data)

  @dbus.service.method("com.VideoOverlay.Ticker",
                       in_signature='', out_signature='')
  def Clear(self):
    self.manager.Clear()

def main():
  parser = argparse.ArgumentParser(description='Ticker client interface.')
  parser.add_argument('-a', '--add', help='Friendly name of new ticker to add.')
  parser.add_argument('-m', '--message', help='Message in ticker to add or update', default='')
  parser.add_argument('-r', '--remove', help='Remove ticker with specified name')
  parser.add_argument('-c', '--clear', help='Clear all current tickers on screen', action='store_true')
  parser.add_argument('-y', '--y_pos', help='y position of ticker on screen', default=300)
  parser.add_argument('-f', '--fontsize', help='Text font size.', default=24)
  parser.add_argument('-s', '--speed', help='Speed of text movement across screen in pixels per second', default=100)
  parser.add_argument('-v', '--verbose', help='Verbose operation. Print status messages during processing', action="store_true")
  args = parser.parse_args()
  
  #get ahold of the debus published object and call its methods
  try:
    bus = dbus.SessionBus()
    remote_object = bus.get_object("com.VideoOverlay.Ticker",
                                   "/TickerServer")

    ticker_iface = dbus.Interface(remote_object, "com.VideoOverlay.Ticker")

    #todo: form json data from input arguments
    msg = ''
    if args.message:
      msg = args.message

    if args.clear:
      ticker_iface.Clear()
    elif args.add:
      ticker_iface.AddTicker(msg)
    elif args.remove:
      ticker_iface.RemoveTicker(msg)
  
  except dbus.DBusException:
    print_exc()
    sys.exit(1)

if __name__ == '__main__':
  main()   
      

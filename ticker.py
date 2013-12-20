#!/usr/bin/python
# vim: set ts=2 expandtab:
'''
Module: ticker.py
Desc: Ticker style text display crawls across screen
Author: John O'Neil
Email: oneil.john@gmail.com
DATE: Monday, Dec 16th 2013
'''
from color import Color
import gobject
import dbus
import dbus.service
import dbus.mainloop.glib
import argparse
from traceback import print_exc
import sys
import jsonpickle
import cairo
import pango
import pangocairo

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
    self.Text = message
    self.DistanceMoved = 0


class Ticker(object):
  def __init__(self, message, y=300, scroll_left=True, font_height=24, color=Color.White,
    is_visible=True, movement=100, drop_shadow=DropShadow()):
    self.Message = TickerMsg(message)
    self.Y = y
    self.ScrollLeft = scroll_left
    self.FontHeight = font_height
    self.Color = color
    self.Movement = movement
    self.DropShadow = drop_shadow
    self.IsVisible = is_visible
    self.Shading = Shading()

  def on_draw(self, ctx, width, height, timestamp, deltaT):
    if not self.IsVisible:
      return

    #calculate current font dimensions
    msg = self.Message.Text
    #distance = speed * time = pixels/second * dt
    delta_x = self.Movement*deltaT

    current_x = width-self.Message.DistanceMoved
    if not self.ScrollLeft:
      current_x = self.Message.DistanceMoved-msg_width

    pangoCtx = pangocairo.CairoContext(ctx)
    msglayout = pangoCtx.create_layout()
    msglayout.set_alignment(pango.ALIGN_RIGHT)
    msglayout.set_wrap(pango.WRAP_WORD_CHAR)
    msglayout.set_font_description(pango.FontDescription("Arial 24"))
    msgattrs, msgtext, msgaccel = pango.parse_markup(msg)
    msglayout.set_attributes(msgattrs)
    msglayout.set_text(msgtext)
    pangoCtx.update_layout(msglayout)
    [ink_rect, logical_rect] = msglayout.get_pixel_extents()
    msg_width = logical_rect[2]
    msg_height = logical_rect[3]

    self.Message.DistanceMoved += delta_x
    if self.Message.DistanceMoved>msg_width+width:
      self.Message.DistanceMoved=0

    #draw a shaded background for messages to traverse (if there are any messages )
    if self.Shading.IsVisible:
      self.Shading.X=0
      self.Shading.Y=self.Y #+ybearing
      self.Shading.W=width
      self.Shading.H=msg_height
      self.Shading.Draw(ctx, width, height, timestamp, deltaT)

    #ctx.move_to( nick_ul_x+1,nick_ul_y+2 )
    #ctx.set_source_rgb(0,0,0)
    #pangoCtx.show_layout(nicklayout)
    ctx.move_to( current_x, self.Y)
    ctx.set_source_rgb(1,1,1)
    pangoCtx.show_layout(msglayout)

class TickerManager(object):
  def __init__(self):
    self.Tickers = {}
    self.server = TickerServer(self)
  
  def Add(self, name, ticker):
    self.Tickers[name] = ticker

  def Remove(self, name):
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

  @dbus.service.method("com.VideoOverlay.Ticker",
                       in_signature='ss', out_signature='')
  def AddTicker(self, name, json_data):
    ticker = jsonpickle.decode(unicode(json_data))
    if not isinstance(ticker, Ticker):
      print str(type(ticker)) +': This is not an instance of Ticker'
      return
    self.manager.Add(name, ticker)

  @dbus.service.method("com.VideoOverlay.Ticker",
                       in_signature='s', out_signature='')
  def RemoveTicker(self, name):
    self.manager.Remove(name)

  @dbus.service.method("com.VideoOverlay.Ticker",
                       in_signature='', out_signature='')
  def Clear(self):
    self.manager.Clear()

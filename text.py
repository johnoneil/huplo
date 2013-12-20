#!/usr/bin/python
# vim: set ts=2 expandtab:
'''
Module: text.py
Desc: Simple static text that can be put on a video stream
Author: John O'Neil
Email: oneil.john@gmail.com
DATE: Thursday, Dec 19th 2013
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
import re
from time import gmtime, strftime


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


class Text(object):
  def __init__(self, message, x=300, y=300, show_shading=False, drop_shadow=DropShadow()):
    self.Message = message
    self.X = x
    self.Y = y
    self.DropShadow = drop_shadow
    self.Shading = Shading(is_visible=show_shading)

  def on_draw(self, ctx, width, height, timestamp, deltaT):
    msg = self.Message
    #update text string with current time if time markup found
    #for example "%{%a, %d %b %Y %H:%M:%S}%"
    def ReplaceMarkupTagWithDate(match):
      datestring = match.group(1).strip()
      #print 'datestring ' + datestring
      return strftime(datestring, gmtime())
    #regex_with_arg = re.compile(r"\%{(.*?)\}%")
    msg = re.sub(r"\%{(.*?)\}%", ReplaceMarkupTagWithDate, msg)
  
    pangoCtx = pangocairo.CairoContext(ctx)
    msglayout = pangoCtx.create_layout()
    #msglayout.set_width( pango.SCALE * self.Width )
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

    #draw a shaded background for messages to traverse (if there are any messages )
    if self.Shading.IsVisible:
      self.Shading.X=self.X
      self.Shading.Y=self.Y
      self.Shading.W=msg_width
      self.Shading.H=msg_height
      self.Shading.Draw(ctx, width, height, timestamp, deltaT)

    #ctx.move_to( nick_ul_x+1,nick_ul_y+2 )
    #ctx.set_source_rgb(0,0,0)
    #pangoCtx.show_layout(nicklayout)
    ctx.move_to(self.X, self.Y)
    ctx.set_source_rgb(1,1,1)
    pangoCtx.show_layout(msglayout)

class TextManager(object):
  def __init__(self):
    self.Texts = {}
    self.server = TextServer(self)
  
  def Add(self, name, text):
    self.Texts[name] = text

  def Remove(self, name):
    if self.Texts[name] is not None:
      self.Texts.pop(name, None)

  def Clear(self):
    self.Texts.clear()

  def on_draw(self, ctx, width, height, timestamp, deltaT):
    for name, text in self.Texts.iteritems():
      text.on_draw(ctx, width, height, timestamp, deltaT)


class TextServer(dbus.service.Object):

  def __init__(self, manager):
    bus_name = dbus.service.BusName('com.VideoOverlay.Text', bus=dbus.SessionBus())
    dbus.service.Object.__init__(self, bus_name, '/TextServer')
    self.manager = manager

  @dbus.service.method("com.VideoOverlay.Text",
                       in_signature='ss', out_signature='')
  def AddText(self, name, json_data):
    text = jsonpickle.decode(unicode(json_data))
    if not isinstance(text, Text):
      print str(type(text)) +': This is not an instance of Text'
      return
    self.manager.Add(name, text)

  @dbus.service.method("com.VideoOverlay.Text",
                       in_signature='s', out_signature='')
  def RemoveText(self, name):
    self.manager.Remove(name)

  @dbus.service.method("com.VideoOverlay.Text",
                       in_signature='', out_signature='')
  def Clear(self):
    self.manager.Clear()

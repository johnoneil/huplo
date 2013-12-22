#!/usr/bin/python
# vim: set ts=2 expandtab:
'''
Module: list.py
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
    ctx.set_source_rgba(self.Color.r, self.Color.g, self.Color.b, self.Color.a)
    ctx.rectangle ( self.X, self.Y, self.W, self.H)
    ctx.fill()


class List(object):
  def __init__(self, size=10, x=300, y=300, width=200, show_shading=False):
    self.Messages = []
    self.Size = size
    self.X = x
    self.Y = y
    self.W = width
    self.Shading = Shading(is_visible=show_shading)

  def Add(self, msg):
    self.Messages.insert(0, msg)
    if len(self.Messages)>self.Size:
      self.Messages.pop()

  def Clear(self):
    self.Messages.clear()

  def on_draw(self, ctx, width, height, timestamp, deltaT):
    ul_x = self.X
    ul_y = self.Y
    for msg in self.Messages:
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
      msglayout.set_width( pango.SCALE * self.W )
      msglayout.set_alignment(pango.ALIGN_LEFT)
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
        self.Shading.X=ul_x
        self.Shading.Y=ul_y
        self.Shading.W=self.W
        self.Shading.H=msg_height
        self.Shading.Draw(ctx, width, height, timestamp, deltaT)

      #ctx.move_to( nick_ul_x+1,nick_ul_y+2 )
      #ctx.set_source_rgb(0,0,0)
      #pangoCtx.show_layout(nicklayout)
      ctx.move_to(ul_x, ul_y)
      ctx.set_source_rgb(1,1,1)
      pangoCtx.show_layout(msglayout)
    
      ul_y += msg_height

class ListManager(object):
  def __init__(self):
    self.Lists = {}
    self.server = ListServer(self)

  def AddList(self, name, newlist):
    self.Lists[unicode(name)] = newlist
  
  def Add(self, name, text):
    if self.Lists[name] is not None:
      self.Lists[name].Add(text)

  def Remove(self, name):
    if self.Lists[name] is not None:
      self.Lists.pop(name, None)

  def Clear(self, name):
    if self.Lists[name] is not None:
      self.Lists[name].Clear()

  def ClearAllLists(self):
    self.Lists.clear()

  def on_draw(self, ctx, width, height, timestamp, deltaT):
    for name, l in self.Lists.iteritems():
      l.on_draw(ctx, width, height, timestamp, deltaT)


class ListServer(dbus.service.Object):

  def __init__(self, manager):
    bus_name = dbus.service.BusName('com.VideoOverlay.List', bus=dbus.SessionBus())
    dbus.service.Object.__init__(self, bus_name, '/ListServer')
    self.manager = manager

  @dbus.service.method("com.VideoOverlay.List",
                       in_signature='ss', out_signature='')
  def AddList(self, name, json_data):
    list = jsonpickle.decode(unicode(json_data))
    if not isinstance(list, List):
      print str(type(list)) +': This is not an instance of Text'
      return
    self.manager.AddList(unicode(name), list)

  @dbus.service.method("com.VideoOverlay.List",
                       in_signature='s', out_signature='')
  def RemoveList(self, name):
    self.manager.Remove(unicode(name))

  @dbus.service.method("com.VideoOverlay.List",
                       in_signature='ss', out_signature='')
  def AddMsg(self, listname, msg):
    self.manager.Add(unicode(listname), unicode(msg))

  @dbus.service.method("com.VideoOverlay.List",
                       in_signature='s', out_signature='')
  def ClearList(self, name):
    self.manager.Remove(unicode(name))

  @dbus.service.method("com.VideoOverlay.List",
                       in_signature='', out_signature='')
  def ClearAllLists(self):
    self.manager.Clear()

  

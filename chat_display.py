# vim: set ts=2 expandtab:
'''
Module: chat_display.py
Desc: Display an IRC chat on a video stream. Nicely animated movement
Author: John O'Neil
Email: oneil.john@gmail.com
DATE: Saturday, December 22nd 2013
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
    ctx.set_source_rgba(self.Color.R, self.Color.G, self.Color.B, self.Color.A)
    ctx.rectangle ( self.X, self.Y, self.W, self.H)
    ctx.fill()

class ChatMsg(object):
  def __init__(self, speaker, msg):
    self.speaker = speaker
    self.msg = msg
    self.timestamp = gmtime()


class Chat(object):
  def __init__(self, size=10, x=20, y=400, width=200, show_shading=False):
    self.Messages = []
    self.Size = size
    self.X = x
    self.Y = y
    self.W = width
    self.Shading = Shading(is_visible=show_shading)
    self.timestamp_column_width = 50
    self.nick_column_width = 50
    self.horizontal_gutter = 2
    self.timestamp_format = '%H:%M:%S'

  def add_msg(self, nick, msg):
    self.Messages.insert(0, ChatMsg(nick, msg))
    if len(self.Messages)>self.Size:
      self.Messages.pop()

  def clear(self):
    self.Messages.clear()

  def on_draw(self, ctx, width, height, timestamp, deltaT):
    ul_x = self.X
    ul_y = self.Y
    for msg in self.Messages:
      message = msg.msg
      timestamp_string = strftime(self.timestamp_format, msg.timestamp)
      nick = msg.speaker

      #need to first get layouts for all three columns to compute the max height
      #of each
      pangoCtx = pangocairo.CairoContext(ctx)

      msglayout = pangoCtx.create_layout()
      msglayout.set_width( pango.SCALE * self.W )
      msglayout.set_alignment(pango.ALIGN_LEFT)
      msglayout.set_wrap(pango.WRAP_WORD_CHAR)
      msglayout.set_font_description(pango.FontDescription("Courier new 12"))
      msgattrs, msgtext, msgaccel = pango.parse_markup(message)
      msglayout.set_attributes(msgattrs)
      msglayout.set_text(msgtext)
      pangoCtx.update_layout(msglayout)
      [ink_rect, logical_rect] = msglayout.get_pixel_extents()
      msg_width = logical_rect[2]
      msg_height = logical_rect[3]

      timestamp_layout = pangoCtx.create_layout()
      timestamp_layout.set_width( pango.SCALE * self.timestamp_column_width)
      timestamp_layout.set_alignment(pango.ALIGN_RIGHT)
      timestamp_layout.set_wrap(pango.WRAP_WORD_CHAR)
      timestamp_layout.set_font_description(pango.FontDescription("Courier new 8"))
      timestamp_attrs, timestamp_text, timestamp_accel = pango.parse_markup(timestamp_string)
      timestamp_layout.set_attributes(timestamp_attrs)
      timestamp_layout.set_text(timestamp_text)
      pangoCtx.update_layout(timestamp_layout)
      [ink_rect, logical_rect] = timestamp_layout.get_pixel_extents()
      timestamp_width = logical_rect[2]
      timestamp_height = logical_rect[3]

      nick_layout = pangoCtx.create_layout()
      nick_layout.set_width( pango.SCALE * self.timestamp_column_width)
      nick_layout.set_alignment(pango.ALIGN_RIGHT)
      nick_layout.set_wrap(pango.WRAP_WORD_CHAR)
      nick_layout.set_font_description(pango.FontDescription("Courier new 8"))
      nick_attrs, nick_text, nick_accel = pango.parse_markup(nick)
      nick_layout.set_attributes(nick_attrs)
      nick_layout.set_text(nick_text)
      pangoCtx.update_layout(nick_layout)
      [ink_rect, logical_rect] = nick_layout.get_pixel_extents()
      nick_width = logical_rect[2]
      nick_height = logical_rect[3]

      #comput general geometry of the layout for this row
      entry_height = max([timestamp_height, nick_height, msg_height])
      timestamp_x = ul_x
      nick_x = ul_x + self.timestamp_column_width + self.horizontal_gutter
      msg_x = ul_x + self.timestamp_column_width + self.nick_column_width + 2*self.horizontal_gutter
      
      #first draw our timestamp column
      if self.Shading.IsVisible:
        ctx.set_source_rgba(0.0, 0.0, 0.0, 0.5)
        ctx.rectangle ( ul_x, ul_y, self.timestamp_column_width, entry_height)
        ctx.fill()
      ctx.move_to(timestamp_x, ul_y)
      ctx.set_source_rgb(1,1,1)
      pangoCtx.show_layout(timestamp_layout)

      #next draw our nick column
      if self.Shading.IsVisible:
        ctx.set_source_rgba(0.0, 0.0, 0.0, 0.5)
        ctx.rectangle ( nick_x, ul_y, self.nick_column_width, entry_height)
        ctx.fill()
      ctx.move_to(nick_x, ul_y)
      ctx.set_source_rgb(1,1,1)
      pangoCtx.show_layout(nick_layout)

      #and our actual message
      if self.Shading.IsVisible:
        ctx.set_source_rgba(0.0, 0.0, 0.0, 0.5)
        ctx.rectangle ( msg_x, ul_y, self.W, entry_height)
        ctx.fill()
      ctx.move_to(msg_x, ul_y)
      ctx.set_source_rgb(1,1,1)
      pangoCtx.show_layout(msglayout)
    
      ul_y += entry_height

class ChatManager(object):
  def __init__(self):
    self.chats = {}
    self.server = ChatServer(self)

  def add_chat(self, chat_name, new_chat):
    self.chats[unicode(chat_name)] = new_chat
  
  def add_msg(self, chat_name, nick, text):
    if self.chats[chat_name] is not None:
      self.chats[chat_name].add_msg(nick, text)

  def remove_chat(self, chat_name):
    if self.chats[chat_name] is not None:
      self.chats.pop(chat_name, None)

  def clear_chat(self, chat_name):
    if self.chats[chat_name] is not None:
      self.chats[chat_name].clear()

  def clear_all_chats(self):
    self.chats.clear()

  def on_draw(self, ctx, width, height, timestamp, deltaT):
    for name, chat in self.chats.iteritems():
      chat.on_draw(ctx, width, height, timestamp, deltaT)


class ChatServer(dbus.service.Object):

  def __init__(self, manager):
    bus_name = dbus.service.BusName('com.VideoOverlay.Chat', bus=dbus.SessionBus())
    dbus.service.Object.__init__(self, bus_name, '/ChatServer')
    self.manager = manager

  @dbus.service.method("com.VideoOverlay.Chat",
                       in_signature='ss', out_signature='')
  def add_chat(self, chat_name, json_data):
    chat = jsonpickle.decode(unicode(json_data))
    if not isinstance(chat, Chat):
      print str(type(list)) +': This is not an instance of Chat'
      return
    self.manager.add_chat(unicode(chat_name), chat)

  @dbus.service.method("com.VideoOverlay.Chat",
                       in_signature='s', out_signature='')
  def remove_chat(self, chat_name):
    self.manager.remove_chat(unicode(chat_name))

  @dbus.service.method("com.VideoOverlay.Chat",
                       in_signature='sss', out_signature='')
  def add_msg(self, chat_name, nick, msg):
    self.manager.add_msg(unicode(chat_name), unicode(nick), unicode(msg))

  @dbus.service.method("com.VideoOverlay.Chat",
                       in_signature='s', out_signature='')
  def clear_chat(self, chat_name):
    self.manager.remove_chat(unicode(chat_name))

  @dbus.service.method("com.VideoOverlay.Chat",
                       in_signature='', out_signature='')
  def clear_all_chats(self):
    self.manager.clear_all_chats()

  

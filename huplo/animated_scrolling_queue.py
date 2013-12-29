# vim: set ts=2 expandtab:
'''
Module: animated_srolling_queue.py
Desc: scrolling messages that bound/slide in, pause and exit after X seconds
Author: John O'Neil
Email: oneil.john@gmail.com
DATE: Wedndesday, December 25th 2013
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
from position import Position
from pause import Pause
from pyTweener import Tweener
from animation import Animation

class Remove(Animation):
  def __init__(self, msg):
    super(Remove, self).__init__()
    self.msg = msg

  def before_first_update(self, dt):
    self.msg.manager.remove(self.msg)
    self.done()

class Message(Position):
  ttl = 10.0
  def __init__(self, manager, text, x=0, y=0, default_style='Arial 16'):
    Position.__init__(self, x=x, y=y)
    self.manager = manager
    self.text = text
    self.default_style = default_style
    self.animation = None
    self.time_onscreen = 0.0

  def is_viable(self):
    return self.time_onscreen < Message.ttl

  def slide_in(self, y, w, h):
    self.x = w+20
    self.y = y
    self.animation = self.to(y=self.y, x=50, t=2.5, tween_type=Tweener.OUT_BOUNCE)

  def slide_up(self):
    up = self.to_relative(0, -30, t=1.0)
    if self.animation:
      self.animation.THEN(up)
    else:
      self.animation = up

  def slide_out(self):
    out = self.to_relative(1200, 0, t=1.0).THEN(Remove(self))
    if self.animation:
      self.animation.THEN(out)
    else:
      self.animation = out

  def do_update(self, dt):
    self.time_onscreen += dt

    if not self.is_viable():
      self.slide_out()

    if self.animation:
      self.animation = self.animation.update(dt)

  def on_draw(self, ctx, width, height, timestamp, deltaT):
    msg = self.text
    #update text string with current time if time markup found
    #for example "%{%a, %d %b %Y %H:%M:%S}%"
    def ReplaceMarkupTagWithDate(match):
      datestring = match.group(1).strip()
      return strftime(datestring, gmtime())
    msg = re.sub(r"\%{(.*?)\}%", ReplaceMarkupTagWithDate, msg)

    pangoCtx = pangocairo.CairoContext(ctx)
    msglayout = pangoCtx.create_layout()
    #make sure all messages fit on the screen?
    msglayout.set_width( pango.SCALE * width *2 / 3 )
    msglayout.set_alignment(pango.ALIGN_LEFT)
    #msglayout.set_wrap(pango.WRAP_WORD_CHAR)
    msglayout.set_ellipsize(pango.ELLIPSIZE_END)
    msglayout.set_font_description(pango.FontDescription(self.default_style))
    msgattrs, msgtext, msgaccel = pango.parse_markup(msg)
    msglayout.set_attributes(msgattrs)
    msglayout.set_text(msgtext)
    pangoCtx.update_layout(msglayout)
    [ink_rect, logical_rect] = msglayout.get_pixel_extents()
    msg_width = logical_rect[2]
    msg_height = logical_rect[3]

    
    ctx.set_source_rgba(0.0, 0.0, 0.0, 0.5)
    linear = cairo.LinearGradient(self.x+msg_width/2, self.y-5, self.x+msg_width/2, self.y+msg_height+5)
    linear.add_color_stop_rgba(0, 0.0, 0.0, 0.0, 0.0)
    linear.add_color_stop_rgba(0.5, 0.0, 0.0, 0.0, 0.75)
    linear.add_color_stop_rgba(1.0, 0.0, 0.0, 0.0, 0.0)

    #radial = cairo.RadialGradient(msg_width/2, msg_height/2, msg_height/4, msg_width/2, msg_height/2, 3*msg_height/4)
    #radial.add_color_stop_rgba(0, 0, 0, 0, 1)
    #radial.add_color_stop_rgba(0.8, 0, 0, 0, 0)

    
    ctx.set_source(linear)
    #ctx.set_source_rgba(0.0, 0.0, 0.0, 0.5)
    #ctx.mask(linear)
    #ctx.move_to(self.x, self.y)
    #ctx.rectangle (self.x, self.y, msg_width, msg_height)
    ctx.rectangle(self.x, self.y-5, msg_width, msg_height+10)
    ctx.fill()

    ctx.move_to(self.x, self.y)
    ctx.set_source_rgb(1,1,0)
    pangoCtx.show_layout(msglayout)


class Queue(object):
  def __init__(self, size=10, y=550, speed=200, pause_in_seconds=3):
    self.messages = []
    self.size = size
    self.y = y
    self.speed = speed
    self.pause_in_seconds = pause_in_seconds
    self.animation = None
    self.current_message = None

  def add(self, msg):
    '''
    Don't add any new messages if it'll oveflow the queue
    Overlfow is just lost (ignored)
    '''
    #queue up an upward movement for all messages onscreen that are still viable
    for message in self.messages:
      if message.is_viable():
        message.slide_up()
    if len(self.messages)<self.size:
      new_msg = Message(self, msg, x=-900, y=self.y)
      new_msg.slide_in(self.y, 1200, 700)
      self.messages.append(new_msg)

  def remove(self, msg):
    '''
    remove an instance of Message class from our queue
    '''
    if msg in self.messages:
      self.messages.remove(msg)

  def clear(self):
    self.messages.clear()

  def on_draw(self, ctx, width, height, timestamp, deltaT):
    #it's not strictly necessary, but I'm going to update
    #and draw current messages separately.
    for msg in self.messages:
      msg.do_update(deltaT)

    for msg in self.messages:
      msg.on_draw(ctx, width, height, timestamp, deltaT)

class QueueManager(object):
  def __init__(self, display_name):
    self.queues = {}
    self.display_name = display_name
    self.server = QueueServer(self)
    

  def add_queue(self, queue_name, new_queue):
    self.queues[queue_name] = new_queue
  
  def add_message(self, queue_name, text):
    if self.queues[queue_name] is not None:
      self.queues[queue_name].add(text)

  def remove_queue(self, queue_name):
    if self.queues[queue_name] is not None:
      self.queues.pop(queue_name, None)

  def clear_queue(self, queue_name):
    if self.queues[queue_name] is not None:
      self.queues[queue_name].clear()

  def clear_all_queues(self):
    self.queues.clear()

  def on_draw(self, ctx, width, height, timestamp, deltaT):
    for name, q in self.queues.iteritems():
      q.on_draw(ctx, width, height, timestamp, deltaT)


class QueueServer(dbus.service.Object):

  def __init__(self, manager):
    self.manager = manager
    bus_name = dbus.service.BusName('com.VideoOverlay.AnimatedScrollingQueue', bus=dbus.SessionBus())
    remote_object_name = '/QueueServer'+self.manager.display_name
    dbus.service.Object.__init__(self, bus_name, remote_object_name)
    

  @dbus.service.method("com.VideoOverlay.AnimatedScrollingQueue",
                       in_signature='ss', out_signature='')
  def add_queue(self, queue_name, json_data):
    queue = jsonpickle.decode(unicode(json_data))
    if not isinstance(queue, Queue):
      print str(type(queue)) +': This is not an instance of queue'
      return
    self.manager.add_queue(unicode(queue_name), queue)

  @dbus.service.method("com.VideoOverlay.AnimatedScrollingQueue",
                       in_signature='s', out_signature='')
  def remove_queue(self, queue_name):
    self.manager.remove_queue(unicode(queue_name))

  @dbus.service.method("com.VideoOverlay.AnimatedScrollingQueue",
                       in_signature='ss', out_signature='')
  def add_message(self, queue_name, msg):
    self.manager.add_message(unicode(queue_name), unicode(msg))

  @dbus.service.method("com.VideoOverlay.AnimatedScrollingQueue",
                       in_signature='s', out_signature='')
  def clear_queue(self, queue_name):
    self.manager.remove_queue(unicode(queue_name))

  @dbus.service.method("com.VideoOverlay.AnimatedScrollingQueue",
                       in_signature='', out_signature='')
  def clear_all_queues(self):
    self.manager.clear()


class QueueClient(object):
  def __init__(self, display_name):
    self.display_name = display_name
    self.remote_object_name = '/TextServer'+ self.display_name
    self.chat_iface = None
    self.get_dbus()

  def get_dbus(self):
    if self.chat_iface:
      return
    try:
      bus = dbus.SessionBus()
      remote_object = bus.get_object("com.VideoOverlay.AnimatedScrollingQueue",
                                   self.remote_object_name)

      self.chat_iface = dbus.Interface(remote_object,\
      "com.VideoOverlay.AnimatedScrollingQueue")
    except dbus.DBusException:
      print 'Unable to get dbus at this time.'

  def add_queue(self, queue_name, size=10, y=550, speed=200, pause_in_seconds=3):
    self.get_dbus()
    if not self.chat_iface:
      return;
    queue = Queue(size=size, y=y, speed=speed, pause_in_seconds=pause_in_seconds)
    pickled = jsonpickle.encode(queue)
    self.chat_iface.add_queue(queue_name, unicode(pickled))

  def add_message(self, queue_name, text):
    self.get_dbus()
    if not self.chat_iface:
      return
    self.chat_iface.add_message(queue_name, text)

  def remove_queue(self, queue_name):
    self.get_dbus()
    if not self.chat_iface:
      return
    self.chat_iface.remove_queue(queue_name)

  def clear_queue(self, queue_name):
    self.get_dbus()
    if not self.chat_iface:
      return
    self.chat_iface.clear_queue(queue_name)

  def clear_all_queues(self):
    self.get_dbus()
    if not self.chat_iface:
      return
    self.chat_iface.clear_all_queues()
  

#!/usr/bin/python
# vim: set ts=2 expandtab:
"""
Module: IRCVideoStream
Desc: A simple gstreamer based way to monitor an IRC chat atop a video stream
Author: John O'Neil
Email:

"""

import sys, os
import pygtk
pygtk.require ("2.0")
import gtk
import gobject
gobject.threads_init()

import pygst
pygst.require('0.10')
import gst

from CustomCairoOverlay import CustomCairoOverlay
from IRCMessageBuffer import IRCMessageBuffer
from IRCMessageBuffer import IRCMessage
#from IRCRender import Simple
from ticker import TickerManager
from GamerStyle import GamerStyle
from text import TextManager
from list import ListManager
from chat_display import ChatManager
from animated_scrolling_queue import QueueManager as AnimatedQueueManager

import logging
import argparse

from math import pi

from overlay_server import ChatServer
import dbus
import dbus.service

class IRCOverlayVideoStream(object):
  """
    Primary module class. Instantiate to create a rendered video stream
  with an overlaid IRC chat.
  """
  def __init__(self, URI):
    """ Initialize and start rendered gstreamer video stream with IRC overlay.

    :param URI: URI address of video stream to render.
    :type URI: str.   
    """
    #self.msgbuffer = IRCMessageBuffer()
    self.DrawHandlers = []
    #self.DrawHandlers.append(Simple(x=100, y=100))
    #self.DrawHandlers.append(Ticker(y=400))
    self.DrawHandlers.append(TickerManager())
    self.DrawHandlers.append(TextManager())
    #self.DrawHandlers.append(GamerStyle())
    self.DrawHandlers.append(ListManager())
    self.DrawHandlers.append(ChatManager())
    self.DrawHandlers.append(AnimatedQueueManager())

    self.pipeline = gst.Pipeline("mypipeline")

    self.uribin = gst.element_factory_make("uridecodebin","uribin")
    self.uribin.set_property("uri", URI )
    self.pipeline.add(self.uribin)

    self.playsink = gst.element_factory_make("playsink", "playsink")
    self.pipeline.add(self.playsink)

    self.text = CustomCairoOverlay(self.DrawHandlers)
    self.pipeline.add(self.text)

    self.convert1 = gst.element_factory_make("ffmpegcolorspace","convert1")
    self.pipeline.add(self.convert1)

    self.convert2 = gst.element_factory_make("ffmpegcolorspace","convert2")
    self.pipeline.add(self.convert2)

    self.uribin.connect("pad-added", self._demuxer_callback)
    
    bus = self.pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", self._on_message)  

    self.pipeline.set_state(gst.STATE_PAUSED)
    self.pipeline.set_state(gst.STATE_PLAYING)

  def push(self, msg):
    """ Push an IRCMessage into the current IRC queue.

    :param msg: The IRC message we'd like to push to the front of the current
      queue
    :type msg: IRCMessage.
    """
    #for handler in self.DrawHandlers:
    #  handler.push(msg)
    pass

  def _demuxer_callback(self, uribin, pad):
    caps = pad.get_caps()
    name = caps[0].get_name()
    if( name == 'video/x-raw-rgb' ):
      pad.link(self.convert1.get_pad('sink'))
      self.convert1.get_pad('src').link(self.text.get_pad('sink'))
      #pad.link(self.text.get_pad('sink'))
      #self.text.get_pad('src').link(self.playsink.get_pad('video_sink'))
      self.text.get_pad('src').link(self.convert2.get_pad('sink'))
      self.convert2.get_pad('src').link(self.playsink.get_pad('video_sink'))
    else:
      pad.link(self.playsink.get_pad('audio_sink'))

    return True

  def OnMessage(self, message):
    #print '***client msg*** ' + message
    self.push(IRCMessage('UNKNOWN', 'vhost', message))

  def _on_message(self, bus, message):
    t = message.type
    if t == gst.MESSAGE_EOS:
      self.pipeline.set_state(gst.STATE_NULL)
      print "message EOS"
      gtk.main_quit()
    elif t == gst.MESSAGE_ERROR:
      self.pipeline.set_state(gst.STATE_NULL)
      err, debug = message.parse_error()
      print "Error: %s" % err, debug
      gtk.main_quit()


def main():
  usage = 'usage: --host <irc hostname> --port <irc port> --nick <irc nickname> --channel <irc channel> --stream <media stream to overlay>'
  parser = argparse.ArgumentParser(description=usage)
  parser.add_argument("-s", "--stream", dest="STREAM_URL",
                      help="stream URL to open")
  parser.add_argument("-v", "--verbose",
                      action="store_true", dest="verbose")
  parser.add_argument("-q", "--quiet",
                      action="store_false", dest="verbose")
  args = parser.parse_args()
  if not args.STREAM_URL:
    parser.error(usage)
  if args.verbose:
    logging.basicConfig(level=logging.DEBUG)

  dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

  stream = IRCOverlayVideoStream(args.STREAM_URL)
  '''
  session_bus = dbus.SessionBus()
  name = dbus.service.BusName("com.VideoOverlay.ChatInterface", session_bus)
  object = ChatServer(session_bus, '/ChatServer', client=stream)
  '''
  gtk.main()
  

if __name__ == "__main__":
  main()

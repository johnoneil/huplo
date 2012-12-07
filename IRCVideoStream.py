#!/usr/bin/python

# vim: set ts=2 expandtab:

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
from IRCRender import Simple
from IRCRender import Ticker

import logging
from oyoyo.client import IRCClient
from oyoyo.cmdhandler import DefaultCommandHandler
from oyoyo import helpers
from optparse import OptionParser

from math import pi


#Thanks to Dunk Fordyce, former author of oyoyo IRC library for this section
class MyHandler(DefaultCommandHandler):
  def __init__(self, client, parent):
    DefaultCommandHandler.__init__(self, client)
    self.parent = parent
  def privmsg(self, nick, chan, msg):
    msg = msg.decode()
    rawnick = nick.split('!')[0]
    fullmsg =  rawnick  + ' : ' + msg.strip()
    self.parent.render.Push( IRCMessage( rawnick,"www.someting.com",msg) )

def MyHandlerFactory(data):
  def f(client):
    return MyHandler(client, data)
  return f

class IRCOverlayVideoStream:
  def __init__(self, URI, host, port, channel, nick ):
    self.URI = URI
    self.host = host
    self.port = port
    self.channel = channel
    self.nick = nick

    self.msgbuffer = IRCMessageBuffer()
    #self.render = Simple()
    self.render = Ticker()

    self.pipeline = gst.Pipeline("mypipeline")

    self.uribin = gst.element_factory_make("uridecodebin","uribin")
    self.uribin.set_property("uri", URI )
    self.pipeline.add(self.uribin)

    self.playsink = gst.element_factory_make("playsink", "playsink")
    self.pipeline.add(self.playsink)

    self.text = CustomCairoOverlay(self.render.OnDraw)
    self.pipeline.add(self.text)

    self.convert1 = gst.element_factory_make("ffmpegcolorspace","convert1")
    self.pipeline.add(self.convert1)

    self.convert2 = gst.element_factory_make("ffmpegcolorspace","convert2")
    self.pipeline.add(self.convert2)

    self.uribin.connect("pad-added", self.demuxer_callback)
    
    bus = self.pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", self.on_message)  

    self.pipeline.set_state(gst.STATE_PAUSED)
    self.pipeline.set_state(gst.STATE_PLAYING)

    self.cli = IRCClient(MyHandlerFactory(self), host=self.host, port=self.port, nick=self.nick, connect_cb=self.connect_cb)
    self.conn = self.cli.connect()

    gobject.idle_add(self.conn.next)

  def SetURI(self,URI):
    self.uribin.set_property("uri", URI )

  def connect_cb(self,cli):
    helpers.join(self.cli, self.channel)

  def demuxer_callback(self, uribin, pad):
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

  def on_message(self, bus, message):
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
  usage = 'usage: %prog --host <irc hostname> --port <irc port> --nick <irc nickname> --channel <irc channel> --stream <media stream to overlay>'
  parser = OptionParser(usage)
  parser.add_option("-s", "--stream", dest="STREAM_URL",
                      help="stream URL to open")
  parser.add_option("-H", "--host", dest="HOST",
                      help="IRC host address")
  parser.add_option("-p", "--port", type="int",dest="PORT",
                      help="IRC port")
  parser.add_option("-n", "--nick", dest="NICK",
                      help="IRC nickname")
  parser.add_option("-c", "--channel", dest="CHANNEL",
                      help="IRC nickname")
  parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose")
  parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose")
  (options, args) = parser.parse_args()
  if not options.HOST or not options.PORT or not options.NICK or not options.CHANNEL or not options.STREAM_URL:
    parser.error(usage)
  if options.verbose:
    logging.basicConfig(level=logging.DEBUG)

  stream = IRCOverlayVideoStream( options.STREAM_URL, options.HOST, options.PORT, options.CHANNEL, options.NICK )

  gtk.main()
  

if __name__ == "__main__":
  main()

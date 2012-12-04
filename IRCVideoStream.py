#!/usr/bin/python

# vim: set ts=2 expandtab:

import pygst
pygst.require("0.10")
import gst
import pygtk
import gtk
import logging
import re
from oyoyo.client import IRCClient
from oyoyo.cmdhandler import DefaultCommandHandler
from oyoyo import helpers
import sys
from optparse import OptionParser

gtk.threads_init()

#currently ineptly carrying info around in globals
CHANNEL = ''

class MyMain:
  def __init__(self, URI):
    self.URI = URI

    self.pipeline = gst.Pipeline("mypipeline")

    self.uribin = gst.element_factory_make("uridecodebin","uribin")
    self.uribin.set_property("uri", URI )
    self.pipeline.add(self.uribin)

    self.playsink = gst.element_factory_make("playsink", "playsink")
    self.pipeline.add(self.playsink)

    self.text = gst.element_factory_make("textoverlay","text")
    self.text.set_property("text","testing, one, two, three")
    self.pipeline.add(self.text)
    self.text.set_property("font-desc", "arial 16")
    self.text.set_property("shaded-background","TRUE")

    self.convert2 = gst.element_factory_make("ffmpegcolorspace","convert2")
    self.pipeline.add(self.convert2)

    self.uribin.connect("pad-added", self.demuxer_callback)
    
    bus = self.pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", self.on_message)  

    self.pipeline.set_state(gst.STATE_PAUSED)
    self.pipeline.set_state(gst.STATE_PLAYING)

  def SetURI(self,URI):
    self.uribin.set_property("uri", URI )

  def demuxer_callback(self, uribin, pad):
    caps = pad.get_caps()
    print 'on_padadded:',caps[0].get_name()
    name = caps[0].get_name()
    if( name == 'video/x-raw-rgb' ):
      pad.link(self.text.get_pad('video_sink'))
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
      gtk.main_quit ()
    elif t == gst.MESSAGE_ERROR:
      self.pipeline.set_state(gst.STATE_NULL)
      err, debug = message.parse_error()
      print "Error: %s" % err, debug
      gtk.main_quit ()

start = None

class MyHandler(DefaultCommandHandler):
  def privmsg(self, nick, chan, msg):
    msg = msg.decode()
    rawnick = nick.split('!')[0]
    #match = re.match('\!say (.*)', msg)
    #if match:
    to_say =  rawnick  + ' : ' + msg.strip()
    #self.messagebuffer.append( to_say )
    #if( len(self.messagebuffer) > 5 ):
    #  self.messagebuffer.pop(0)
    #newtext = ''
    #for message in self.messagebuffer:
    #  newtext += ( message + '\n' )
    
    #print('Saying, "%s"' % to_say)
    #helpers.msg(self.client, chan, to_say)
    #start.text.set_property('text',newtext)
    start.text.set_property('text',to_say)

def connect_cb(cli):
  helpers.join(cli, CHANNEL)

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

  global CHANNEL
  CHANNEL = options.CHANNEL
  global start
  start=MyMain( options.STREAM_URL )

  cli = IRCClient(MyHandler, host=options.HOST, port=options.PORT, nick=options.NICK,
          connect_cb=connect_cb)
  conn = cli.connect()

  gtk.idle_add(conn.next)
  gtk.main()
  

if __name__ == "__main__":
    main()

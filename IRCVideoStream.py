#!/usr/bin/python

import pygst
pygst.require("0.10")
import gst
import pygtk
import gtk

import logging
import re
from pprint import pprint

from oyoyo.client import IRCClient
from oyoyo.cmdhandler import DefaultCommandHandler
from oyoyo import helpers

import sys
import getopt
from optparse import OptionParser

gtk.threads_init()

#currently ineptly carrying info around in globals
CHANNEL = ''

class MyMain:
	def __init__(self, URI):
		self.URI = URI
		#self.ircclient = ircClient
		self.pipeline = gst.Pipeline("mypipeline")

		#self.audiotestsrc = gst.element_factory_make("audiotestsrc", "audio")
		self.uribin = gst.element_factory_make("uridecodebin","uribin")
		self.uribin.set_property("uri", URI )
		#self.uribin.set_property("uri", 'mms://mediaserver2.otn.ca/mediasite/8a4d5589-ec55-4117-827f-709b325f65e6.wmv')
		self.pipeline.add(self.uribin)

		#self.audio = gst.element_factory_make("input-selector","audio")
		#self.audio.set_property("sync-streams","TRUE")
		#self.pipeline.add(self.audio)

		#self.video = gst.element_factory_make("input-selector","video")
		#self.video.set_property("sync-streams","TRUE")
		#self.pipeline.add(self.video)

		#self.sink = gst.element_factory_make("alsasink", "sink")
		self.playsink = gst.element_factory_make("playsink", "playsink")
		self.pipeline.add(self.playsink)

		self.text = gst.element_factory_make("textoverlay","text")
		self.text.set_property("text","testing, one, two, three")
		self.pipeline.add(self.text)
		self.text.set_property("font-desc", "arial 16")
		self.text.set_property("shaded-background","TRUE")

		self.convert2 = gst.element_factory_make("ffmpegcolorspace","convert2")
		self.pipeline.add(self.convert2)

		#self.audiotestsrc.link(self.sink)
		#gst.element_link_many(self.uribin,self.audio,self.video, self.playsink)

		self.uribin.connect("pad-added", self.demuxer_callback)
		
		#self.uribin.get_pad('src1').link(self.audio)
		#self.audio.link(self.playsink.get_pad('audio_sink'))
		#self.uribin.get_pad('src0').link(self.video)
		#self.video.link(self.playsink.get_pad('video_sink'))	

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
			#pad.link(self.playsink.get_pad('video_sink'))
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
		#newselector = gst.element_factory_make("input-selector","input")
		#newselector.set_property("sync-streams","TRUE")
		#self.pipeline.add(newselector)

		#sinkpad = newselector.get_compatible_pad(pad, pad.get_caps())
		#pad.link(sinkpad)
		#endpad = self.playsink.get_compatible_pad(sinkpad,sinkpad.get_caps())
		#newselector.link(endpad)

		#if pad.get_property("template").name_template == "video_%02d":
		#	qv_pad = self.playsink.get_pad("video_sink")
		#	pad.link(qv_pad)
		#elif pad.get_property("template").name_template == "audio_%02d":
		#	qa_pad = self.playsink.get_pad("audio_sink")
		#	pad.link(qa_pad)
		



#conn.next()



#pprint(start)
#start=MyMain()
start = None

class MyHandler(DefaultCommandHandler):
  #def __init__(self,handler):
  #  super( DefaultCommandHandler, self ).__init__(self)
  #  self.messagebuffer = []

  #def send(self,msg,server):
  #  super( DefaultCommandHandler, self).send(msg,server)

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

#myHandler = MyHandler(start)

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
  # process arguments
  #for arg in args:
  #    process(arg) # process() is defined elsewhere
  cli = IRCClient(MyHandler, host=options.HOST, port=options.PORT, nick=options.NICK,
          connect_cb=connect_cb)
  conn = cli.connect()

  #print(dir(start))
  gtk.idle_add(conn.next)
  gtk.main()
  

if __name__ == "__main__":
    main()

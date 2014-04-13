#!/usr/bin/python3
# vim: set ts=2 expandtab:
"""
Module: relay-stream
Desc: Relay an existing video stream via a TCP server and allow text overlay
Author: John O'Neil
Email: oneil.john@gmail.com
Date: Sat, April 12th 2014

Simple stream realy with text overlay.
Point the relay at an existing stream URL and we can relay it
via another TCP server.
Relaying like this (and transcoding to H264/MP3) allows us
to access the video and overlay dynamic text and graphics atop
the video.

"""

import argparse
import signal

#gstreamer 1.0 support
import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst, Gtk

#carry out GTK initialization after imports.
GObject.threads_init()
Gst.init(None)


class StreamRelayWithTextOverlay(object):
  def __init__(self, uri, display_name, hostname='127.0.0.1', port=10000):
    '''Initialize a video+audios stream relay via URI, display name etc.
    This has been tested on .nsv(vp6.2/mpga) and .ts(h264/mp3) streams
    but could easily fail for others.
    Had to adopt gstreamer 1.0 to get .nsv to work
    :param uri: uri of stream (http acceptable)
    :param display_name: friendly name of relay display. Text overlay hook.
    :param hostname: hostname of relay (necessary?)
    :param port: port at which clients can connect to relay.

    Relay transcodes ALL sources into an mpeg TS(h264/mp3) for simplicity.
    We need to decode/re-encode all streams anyway since we want to draw
    Text on it, so we might as well send out a uniform format.
    '''
    self.uri = uri
    self.display_name = display_name
    self.hostname = hostname
    self.port = port

    # Create GStreamer pipeline
    self.pipeline = Gst.Pipeline()

    # Create bus to get events from GStreamer pipeline
    self.bus = self.pipeline.get_bus()
    self.bus.add_signal_watch()
    self.bus.connect('message::eos', self.on_eos)
    self.bus.connect('message::error', self.on_error)

    #Create the video pipeline elements
    self.uridecodebin = Gst.ElementFactory.make('uridecodebin', None)
    self.pipeline.add(self.uridecodebin)
    self.videoconvert = Gst.ElementFactory.make('videoconvert', None)
    self.pipeline.add(self.videoconvert)
    self.x264enc = Gst.ElementFactory.make('x264enc', None)
    self.pipeline.add(self.x264enc)
    self.mpegtsmux = Gst.ElementFactory.make('mpegtsmux', None)
    self.pipeline.add(self.mpegtsmux)
    self.tcpserversink = Gst.ElementFactory.make('tcpserversink', None)
    self.pipeline.add(self.tcpserversink)

    #create the audio pipeline elements
    self.audioconvert = Gst.ElementFactory.make('audioconvert', None)
    self.pipeline.add(self.audioconvert)
    self.lamemp3enc = Gst.ElementFactory.make('lamemp3enc', None)
    self.pipeline.add(self.lamemp3enc)
 
    #connect up the pipeline (as much as possible disregarding dynamic
    #pad connections
    self.videoconvert.link(self.x264enc)
    self.x264enc.link(self.mpegtsmux)
    self.mpegtsmux.link(self.tcpserversink)
    self.audioconvert.link(self.lamemp3enc)
    self.lamemp3enc.link(self.mpegtsmux) 

    # Set properties
    self.uridecodebin.connect('pad-added', self.on_pad_added)
    self.uridecodebin.set_property('uri', self.uri)
    self.tcpserversink.set_property('host', self.hostname)
    self.tcpserversink.set_property('port', self.port)


  def on_pad_added(self, uribin, pad):
    '''Callback invoked when dynamic output (source) pads
    are added to uridecodebin.
    When these pads appear, we connect them to the appropriate
    audio or video pipeline.
    '''
    pad_type = pad.query_caps(None).to_string()
    if pad_type.startswith('video/'):
      pad.link(self.videoconvert.get_static_pad('sink'))
    elif pad_type.startswith('audio/'):
      pad.link(self.audioconvert.get_static_pad('sink'))
    else:
      pass

  def run(self):
    '''Run the relay. Will run until quit() method is invoked.
    '''
    self.pipeline.set_state(Gst.State.PLAYING)
    Gtk.main()

  def quit(self):
    '''Stop the relay and shut down.
    '''
    self.pipeline.set_state(Gst.State.NULL)
    Gtk.main_quit()

  def on_eos(self, bus, msg):
    '''End of stream handler invoked when pipeline detects EOS.
    '''
    print('on_eos()')
    self.quit()

  def on_error(self, bus, msg):
    print('on_error():', msg.parse_error())
    self.quit()


def main():
  usage = 'Relay a video stream, adding text overlay.'
  parser = argparse.ArgumentParser(description=usage)
  parser.add_argument('uri', help='URI of stream to relay.', type=str)
  parser.add_argument("-n", "--name",
                      help="display name. Clients can attach text displays via this friendlyname.",
                      type=str, default='')
  parser.add_argument("-r", "--relay_hostname",
                      help='Hostname for relay TCP server.', type=str, default='127.0.0.1')
  parser.add_argument("-p", "--relay_port",
                      help='Port for relay TCP server.', type=int, default=10000)
  args = parser.parse_args()

  uri = args.uri
  display_name = args.name
  hostname = args.relay_hostname
  port = args.relay_port

  #dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

  ##support ctrl-c escape as per http://askubuntu.com/questions/160343/quit-application-on-ctrlc-in-quickly-framework
  signal.signal(signal.SIGINT, signal.SIG_DFL)

  relay = StreamRelayWithTextOverlay(uri, display_name, hostname, port)
  relay.run()
  

if __name__ == "__main__":
  main()


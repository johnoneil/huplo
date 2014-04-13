#!/usr/bin/python3

#from os import path
import argparse
#support ctrl-c escape as per http://askubuntu.com/questions/160343/quit-application-on-ctrlc-in-quickly-framework
import signal

import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst, Gtk
#from gi.repository import GdkX11, GstVideo

#carry out GTK initialization after imports.
GObject.threads_init()
Gst.init(None)


class StreamRelayWithTextOverlay(object):
  def __init__(self, uri, display_name, hostname='127.0.0.1', port=10000):
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

    # This is needed to make the video output in our DrawingArea:
    #self.bus.enable_sync_message_emission()
    #self.bus.connect('sync-message::element', self.on_sync_message)

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

    # Add playbin to the pipeline
    #self.pipeline.add(self.playbin)

    # Set properties
    #self.playbin.set_property('uri', uri)
    self.uridecodebin.connect('pad-added', self.on_pad_added)
    self.uridecodebin.set_property('uri', self.uri)
    self.tcpserversink.set_property('host', self.hostname)
    self.tcpserversink.set_property('port', self.port)


  def on_pad_added(self, uribin, pad):
    pad_type = pad.query_caps(None).to_string()
    if pad_type.startswith('video/'):
      pad.link(self.videoconvert.get_static_pad('sink'))
    elif pad_type.startswith('audio/'):
      pad.link(self.audioconvert.get_static_pad('sink'))
    else:
      pass

  def run(self):
    #self.window.show_all()
    # You need to get the XID after window.show_all().  You shouldn't get it
    # in the on_sync_message() handler because threading issues will cause
    # segfaults there.
    #self.xid = self.drawingarea.get_property('window').get_xid()
    self.pipeline.set_state(Gst.State.PLAYING)
    Gtk.main()

  def quit(self):#, window):
    self.pipeline.set_state(Gst.State.NULL)
    Gtk.main_quit()

  def on_sync_message(self, bus, msg):
    if msg.get_structure().get_name() == 'prepare-window-handle':
      print('prepare-window-handle')
      msg.src.set_window_handle(self.xid)

  def on_eos(self, bus, msg):
    print('on_eos()')
    self.quit()
    #self.pipeline.seek_simple(
    #  Gst.Format.TIME,        
    #  Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT,
    #  0
    #  )

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

  #support ctrl-c signal handling
  signal.signal(signal.SIGINT, signal.SIG_DFL)

  relay = StreamRelayWithTextOverlay(uri, display_name, hostname, port)
  relay.run()
  

if __name__ == "__main__":
  main()


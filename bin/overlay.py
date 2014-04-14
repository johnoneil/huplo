#!/usr/bin/python3
# vim: set ts=2 expandtab:
"""
Module: overlay.py
Desc: Gst 1.0 dynamic text overlay plugin
Author: John O'Neil
Email:

Stand-in for evidently non-functional (in python) gstreamer CairoOverlay
This is based on
http://cgit.freedesktop.org/gstreamer/gst-python/tree/examples/buffer-draw.py

This currently requires the pycairo development branch that
supports cairo.ImageSurface.create_for_data as described at:
http://cgit.freedesktop.org/pycairo/commit/?id=2f9e604ac7bb5f6386179a3d0fad6f095c386f66

"""
import sys
import traceback
from math import pi

#gstreamer 1.0 support
import signal

#gstreamer 1.0 support
import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst, Gtk, GstBase

#carry out GTK initialization after imports.
GObject.threads_init()
Gst.init(None)

import cairo

#hack defined at http://lists.freedesktop.org/archives/gstreamer-bugs/2013-March/100008.html
def get_element_class(klass):
    element_class = GObject.type_class_peek(klass.__gtype__)
    element_class.__class__ = Gst.ElementClass
    return element_class

class DynamicTextOverlay(Gst.Element):
  __gstdetails__ = (
    'DynamicTextOverlay plugin',
    'overlay.py',
    'gst.Element that places dynamic text on a frame buffer',
    'John O\'Neil <oneil.john@gmail.com>')

  __gstmetadata__ = (
        'DynamicTextOverlay plugin',
        'video processing plugin',
        'gst.Element that places dynamic text on a frame buffer',
        'John O\'Neil <oneil.john@gmail.com>',
    )
    
  __gsttemplates__ = (
    Gst.PadTemplate.new('sink',
                     Gst.PadDirection.SINK,
                     Gst.PadPresence.ALWAYS,
                     Gst.caps_from_string('video/x-raw,bpp=32,depth=32,blue_mask=-16777216,green_mask=16711680, red_mask=65280, alpha_mask=255,width=[ 1, 2147483647 ],height=[ 1, 2147483647 ],framerate=[ 0/1, 2147483647/1 ]')),
    Gst.PadTemplate.new('src',
                     Gst.PadDirection.SRC,
                     Gst.PadPresence.ALWAYS,
                     Gst.caps_from_string('video/x-raw,bpp=32,depth=32,blue_mask=-16777216,green_mask=16711680, red_mask=65280, alpha_mask=255,width=[ 1, 2147483647 ],height=[ 1, 2147483647 ],framerate=[ 0/1, 2147483647/1 ]')),
  )
  _sinkpadtemplate = __gsttemplates__[0]
  _srcpadtemplate = __gsttemplates__[1]

  def __init__(self):
    #Gst.Element.__init__(self, *args, **kwargs)
    super(DynamicTextOverlay, self).__init__()
    #self.set_passthrough(True)
    self.customDrawHandlers = []
    self.lastTimestamp = 0

    self.sinkpad = Gst.Pad.new_from_template(self._sinkpadtemplate, 'sink')
    self.sinkpad.set_chain_function_full(self.chainfunc, None)
    self.sinkpad.set_event_function_full(self.eventfunc, None)
    #self.sinkpad.set_getcaps_function_full(Gst.Pad.proxy_getcaps)
    #self.sinkpad.set_setcaps_function_full(Gst.Pad.proxy_setcaps)
    self.add_pad(self.sinkpad)

    self.srcpad = Gst.Pad.new_from_template(self._srcpadtemplate, 'src')
    self.srcpad.set_event_function_full(self.srceventfunc, None)
    self.srcpad.set_query_function_full(self.srcqueryfunc, None)
    #self.srcpad.set_getcaps_function_full(Gst.Pad.proxy_getcaps)
    #self.srcpad.set_setcaps_function_full(Gst.Pad.proxy_setcaps)
    self.add_pad(self.srcpad)

  def add_overlay(self, custom_draw_handler):
    self.customDrawHandlers.append(custom_draw_handler)

  def do_transform(self, buff_in, buff_out):
    print('I am called!')
    return Gst.FlowReturn.OK

  def chainfunc(self, pad, parent, buffer):
    try:
      #(success, outbuf) = buffer.map(Gst.MapFlags.READ | Gst.MapFlags.WRITE)
      #writeable_buf = outbuf.make_writable()
      outbuf = buffer.copy()
      self.draw_on(pad, outbuf)
      return self.srcpad.push(outbuf)
    except:
      return GST_FLOW_ERROR

  #def eventfunc(self, pad, event, user_data):
  def eventfunc(self, pad, parent, event):
    return self.srcpad.push_event(event)
    
  def srcqueryfunc(self, pad, object, query):
    return self.sinkpad.query(query)

  def srceventfunc(self, pad, parent, event):
    return self.sinkpad.push_event(event)

  def draw_on (self, pad, buf):
    deltaT = 0#buf.timestamp - self.lastTimestamp
    #self.lastTimestamp = buf.timestamp
    #try:
    caps = pad.query_caps(None)
    #width = caps[0]['width']
    #height = caps[0]['height']
    #framerate = caps[0]['framerate']
    (success, width) = caps.get_structure(0).get_int('width')
    (success, height) = caps.get_structure(0).get_int('height')
    #(success, framerate) = caps.get_structure(0).get_fraction('framerate')
    
    #cairo.ImageSurface.create_for_data currently raises a 'not implemented' exception
    #thus we've got to use a local branch of pycairo until this issue is addressed
    #surface = cairo.ImageSurface.create_for_data(buf, cairo.FORMAT_ARGB32, width, height, 4 * width)
    #ctx = cairo.Context(surface)
    #except as e:
    #  print str(e)
    #  print "Failed to create cairo surface for buffer"
    #  traceback.print_exc()
    #  return

    #try:
    #  for drawHandler in self.customDrawHandlers:
    #    drawHandler.on_draw(ctx,width,height,buf.timestamp*1e-9,deltaT*1e-9)
    #except:
    #  print "Failed cairo render"
    #  traceback.print_exc()

#hack defined at http://lists.freedesktop.org/archives/gstreamer-bugs/2013-March/100008.html
get_element_class(DynamicTextOverlay).set_metadata('dynamictextoverlay', 'classification', 'description',
'author')
DynamicTextOverlay.register(None, 'dynamictextoverlay', Gst.Rank.NONE, DynamicTextOverlay.__gtype__)


class DynamicOverlayTestPipeline(object):
  def __init__(self):
    '''Test filter via simple pipeline.
    videotestsrc-->videoconv-->dynamictextoverlay-->videoconv-->autovideosink
    '''
    # Create GStreamer pipeline
    self.pipeline = Gst.Pipeline()

    # Create bus to get events from GStreamer pipeline
    self.bus = self.pipeline.get_bus()
    self.bus.add_signal_watch()
    self.bus.connect('message::eos', self.on_eos)
    self.bus.connect('message::error', self.on_error)

    #Create the video pipeline elements
    self.videotestsrc = Gst.ElementFactory.make('videotestsrc', None)
    self.pipeline.add(self.videotestsrc)
    self.videoconvert = Gst.ElementFactory.make('videoconvert', None)
    self.pipeline.add(self.videoconvert)
    self.dynamictextoverlay = Gst.ElementFactory.make('dynamictextoverlay', None)
    self.pipeline.add(self.dynamictextoverlay)
    self.videoconvert2 = Gst.ElementFactory.make('videoconvert', None)
    self.pipeline.add(self.videoconvert2)
    self.autovideosink = Gst.ElementFactory.make('autovideosink', None)
    self.pipeline.add(self.autovideosink)
 
    #connect up the pipeline (as much as possible disregarding dynamic
    #pad connections
    self.videotestsrc.link(self.videoconvert)
    self.videoconvert.link(self.dynamictextoverlay)
    self.dynamictextoverlay.link(self.videoconvert2)
    self.videoconvert2.link(self.autovideosink)


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
  #dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

  #support ctrl-c escape as per http://askubuntu.com/questions/160343/quit-application-on-ctrlc-in-quickly-framework
  signal.signal(signal.SIGINT, signal.SIG_DFL)

  pipeline = DynamicOverlayTestPipeline()
  pipeline.run()
  

if __name__ == "__main__":
  main()


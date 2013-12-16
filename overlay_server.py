#!/usr/bin/python
# vim: set ts=2 expandtab:
"""
Module: overlay_server.py
Desc: dbus server to pick up commands
Author: John O'Neil
Email: oneil.john@gmail.com
DATE: Sunday, December 15th 2013
  
""" 
import gobject
import dbus
import dbus.service
import dbus.mainloop.glib
import argparse
  
#class DemoException(dbus.DBusException):
#    _dbus_error_name = 'com.example.DemoException'
  
class ChatServer(dbus.service.Object):

  @dbus.service.method("com.VideoOverlay.ChatInterface",
                       in_signature='s', out_signature='s')
  def HelloWorld(self, hello_message):
    print hello_message
    return 'echo: ' + hello_message

  @dbus.service.method("com.VideoOverlay.ChatInterface",
                       in_signature='', out_signature='(ss)')
  def GetTuple(self):
    return ("Hello Tuple", " from example-service.py")

  @dbus.service.method("com.VideoOverlay.ChatInterface",
                       in_signature='', out_signature='a{ss}')
  def GetDict(self):
    return {"first": "Hello Dict", "second": " from example-service.py"}

  @dbus.service.method("com.VideoOverlay.ChatInterface",
                       in_signature='', out_signature='')
  def Exit(self):
    mainloop.quit()
  
  
def main():
  parser = argparse.ArgumentParser(description='Pick up overlay commands from dbus.')
  #parser.add_argument('infile', help='Input domain specific text description of C++ structures to generate.')
  parser.add_argument('-v','--verbose', help='Verbose operation. Print status messages during processing', action="store_true")
  args = parser.parse_args()

  dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

  session_bus = dbus.SessionBus()
  name = dbus.service.BusName("com.VideoOverlay.ChatInterface", session_bus)
  object = ChatServer(session_bus, '/ChatServer')

  mainloop = gobject.MainLoop()
  if args.verbose:
    print "Running overlay dbus server."
  mainloop.run()

if __name__ == '__main__':
  main()

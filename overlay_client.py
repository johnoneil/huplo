#!/usr/bin/python
# vim: set ts=2 expandtab:
"""
Module: overlay_client.py
Desc: dbus client to send overlay dbus server commands
Author: John O'Neil
Email: oneil.john@gmail.com
DATE: Sunday, December 15th 2013
  
""" 
import sys
from traceback import print_exc
import dbus
import argparse
  
def main():
  parser = argparse.ArgumentParser(description='Pick up overlay commands from dbus.')
  #parser.add_argument('infile', help='Input domain specific text description of C++ structures to generate.')
  parser.add_argument('-v','--verbose', help='Verbose operation. Print status messages during processing', action="store_true")
  args = parser.parse_args()
  bus = dbus.SessionBus()

  #get ahold of the debus published object and call its methods
  try:
    remote_object = bus.get_object("com.VideoOverlay.ChatInterface",
                                   "/ChatServer")

    #get ahold of interface off remote object and make simple call
    overlay_iface = dbus.Interface(remote_object, "com.VideoOverlay.ChatInterface")
    reply = overlay_iface.HelloWorld('Yet another hello world from client.')
    print 'Reply from server is ' + reply
  
  except dbus.DBusException:
    print_exc()
    sys.exit(1)
  '''
    # you can either specify the dbus_interface in each call...
    #hello_reply_list = remote_object.HelloWorld("Hello from example-client.py!",
    #    dbus_interface = "com.VideoOverlay.ChatInterface")
  
  print (hello_reply_list)

  # ... or create an Interface wrapper for the remote object
  iface = dbus.Interface(remote_object, "com.VideoOverlay.ChatInterface")
  hello_reply_tuple = iface.GetTuple()

  print hello_reply_tuple

  hello_reply_dict = iface.GetDict()

  print hello_reply_dict

  # D-Bus exceptions are mapped to Python exceptions
  try:
    iface.RaiseException()
  except dbus.DBusException, e:
    print str(e)

  # introspection is automatically supported
  print remote_object.Introspect(dbus_interface="org.freedesktop.DBus.Introspectable")

  if sys.argv[1:] == ['--exit-service']:
    iface.Exit()
  '''

if __name__ == '__main__':
  main()

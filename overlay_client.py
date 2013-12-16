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
  parser.add_argument('msg', help='message to send to overlay server.')
  parser.add_argument('-v','--verbose', help='Verbose operation. Print status messages during processing', action="store_true")
  args = parser.parse_args()
  bus = dbus.SessionBus()

  #get ahold of the debus published object and call its methods
  try:
    remote_object = bus.get_object("com.VideoOverlay.ChatInterface",
                                   "/ChatServer")

    #get ahold of interface off remote object and make simple call
    overlay_iface = dbus.Interface(remote_object, "com.VideoOverlay.ChatInterface")
    reply = overlay_iface.HelloWorld(args.msg)
    print 'Reply from server is ' + reply
  
  except dbus.DBusException:
    print_exc()
    sys.exit(1)

if __name__ == '__main__':
  main()

#!/usr/bin/python
# vim: set ts=2 expandtab:
'''
Module: irc_client.py
Desc: Simple irc client driving video overlay
Author: John O'Neil
Email: oneil.john@gmail.com
DATE: Tuesday, Dec 24th 2013

This is based on the old twisted IRC client 'scaffold' which
is weird, but fine.

'''

import re
import sys
import unicodedata
from twisted.internet import reactor
from twisted.internet import protocol
from twisted.internet import ssl
from twisted.python import log
from twisted.words.protocols import irc as twisted_irc
from color import Color
import dbus
import argparse
from traceback import print_exc
import sys
import jsonpickle
from chat_display import Chat
import string
import irc

DEFAULT_PORT = 6660


class IRCVideoOverlayClient(twisted_irc.IRCClient):
  def connectionMade(self):
    twisted_irc.IRCClient.connectionMade(self)
    bus = dbus.SessionBus()
    remote_object = bus.get_object("com.VideoOverlay.Chat",
                                   "/ChatServer")

    self.chat_iface = dbus.Interface(remote_object, "com.VideoOverlay.Chat")


  def connectionLost(self, reason):
    twisted_irc.IRCClient.connectionLost(self, reason)

  def signedOn(self):
    '''
    Called when we've connected to the IRC server.
    We can use this opportunity to communicate with nickserv
    if necessary
    '''
    network = self.factory.network

    if network['identity']['nickserv_pw']:
      self.msg('NickServ', 
            'IDENTIFY %s' % network['identity']['nickserv_pw'])

    for channel in network['autojoin']:
      print('join channel %s' % channel)
      self.join(channel)

  def joined(self, channel):
    '''
    Called when we've joined a channel. This is here used to
    Initialize a chat dialog on the screen that will later
    be updated with posts as the chat progresses.
    '''
    chat = Chat(show_shading=True)
    pickled = jsonpickle.encode(chat)
    self.chat_iface.add_chat(unicode(channel), unicode(pickled))

  def privmsg(self, user, channel, msg):
    '''
    Invoked upon receipt of a message in channel X.
    Here it's used to pass chat posts to video overlay via dbus
    '''
    nick, vhost = irc.split_speaker(user)
    msg = irc.formatting_to_pango_markup(msg)
    self.chat_iface.add_msg(unicode(channel), unicode(nick), msg)


  def irc_RPL_TOPIC(self, prefix, params):
    '''
    Called when the topic for a channel is initially reported or when it      subsequently changes.
    params[0] is your nick
    params[1] is channel joined
    params[2] is topic for channel

    '''
    channel = params[1]
    topic = params[2]
    topic = irc.formatting_to_pango_markup(topic)
    #print 'channel ' + channel + ' topic: ' + topic

  def alterCollidedNick(self, nickname):
      return nickname+'_'

class IRCVideoOverlayClientFactory(protocol.ClientFactory):
  protocol = IRCVideoOverlayClient

  def __init__(self, network_name, network):
    self.network_name = network_name
    self.network = network

  def clientConnectionLost(self, connector, reason):
    connector.connect()

  def clientConnectionFailed(self, connector, reason):
    reactor.stop()

def split_server_port(hostname):
  hostname, port = string.split(hostname, ':', maxsplit=1)
  if not port:
    port = DEFAULT_PORT
  else:
    try:
      port = int(port)
    except ValueError:
      port = DEFAULT_PORT
  return (hostname, port)

def main():
  parser = argparse.ArgumentParser(description='Inject IRC channel into video stream.')
  parser.add_argument('hostname', help='IRC server URL as domain:port (e.g. www.freenode.net:6660).', type=str)
  parser.add_argument('nickname', help='Nick to use at signon. Multiple nicks not yet supported.', type=str)
  parser.add_argument('channel', help='Channel to join on server', type=str)
  parser.add_argument('-u', '--username', help='Username to use at signon.', type=str, default='')
  parser.add_argument('-r', '--realname', help='Realname to use at signon.', type=str, default='')
  parser.add_argument('-p', '--password', help='Optional password to use at signon', type=str, default=None)
  parser.add_argument('-x', '--x_pos', help='x position of chat box on screen in pixels.', default=20, type=int)
  parser.add_argument('-y', '--y_pos', help='y position of chat box on screen in pixels.', default=400,type=int)
  parser.add_argument('-w', '--width', help='Max width of chat text box colum in pixels.', default=200, type=int)
  parser.add_argument('-m', '--max_posts', help='Max number of chat box posts shown.', default=10, type=int)
  parser.add_argument('-b', '--background', help='Show shaded background behind text', action="store_true")
  parser.add_argument('-v', '--verbose', help='Log debug info to screen', action="store_true")
  parser.add_argument('-s', '--ssl', help='Connect to server via SSL.', action="store_true")
  args = parser.parse_args()
  
  try:
    hostname, port = split_server_port(args.hostname)
    if args.verbose:
      print 'Connecting to ' + hostname + ' on port ' + str(port) +'.'
    
    credentials = {
        'nickname': args.nickname,
        'realname': args.realname if len(args.realname)>0 else args.nickname,
        'username': args.username if len(args.username)>0 else args.nickname,
        'nickserv_pw': args.password
    }
    #we've got to add thise to the client, which is odd as fuq
    IRCVideoOverlayClient.nickname = credentials['nickname']
    IRCVideoOverlayClient.realname = credentials['realname']
    IRCVideoOverlayClient.username = credentials['username']
    IRCVideoOverlayClient.password = credentials['nickserv_pw']
    
    channels = (args.channel,)

    network = {
        'host': hostname,
        'port': port,
        'ssl': args.ssl,
        'identity': credentials,
        'autojoin': channels
    }

    factory = IRCVideoOverlayClientFactory(hostname, network)
    if args.ssl:
      reactor.connectSSL(hostname, port, factory, ssl.ClientContextFactory())
    else:
      reactor.connectTCP(hostname, port, factory)

    reactor.run()

  except dbus.DBusException:
    print_exc()
    sys.exit(1)

if __name__ == '__main__':
  main() 



# vim: set ts=2 expandtab:
"""

Module: irc.py
Desc: Helpers for IRC clients (msg decoding, paring, formatting)
Author: John O'Neil
Email: oneil.john@gmail.com
DATE: Tuesday, Dec 24th 2013
  
""" 

import re
import string

def split_speaker(user):
  '''
  split a nick most likely in the form:
  "SoapKills!~ring@banana.phone"
  or (nick)!~(realname)@(vhost)
  into a tuble of (nick, vhost)
  '''
  nick, vhost = string.split(user, '!', maxsplit=1)
  if not vhost:
    vhost = 'nick@unknown'
  vhost = vhost.replace('~', '', 1)
  return nick, vhost

color_dict = {
  0 : 'white',
  1 : 'black',
  2 : 'dark blue',
  3 : 'dark green',
  4 : 'red',
  5 : 'dark red',
  6 : 'dark violet',
  7 : 'dark orange',
  8 : 'yellow',
  9 : 'light green',
  10 : 'cyan',
  11 : 'light cyan',
  12 : 'blue',
  13 : 'violet',
  14 : 'dark gray',
  15 : 'light gray',
  }

def color_code_to_X11(code):
  if not isinstance(code, int):
    return 'black'
  if code<0:
    return 'black'
  if code>15:
    return 'black'
  return color_dict[code]

def formatting_to_pango_markup(msg):
  '''
  Take an irc message already decoded from utf-8/latin1 etc
  and replace typical binary irc color code formatting with
  pango markup.
  '''
  class MarkupFunctor(object):
    def __init__(self):
      self.match_found = False
      self.bold = False
      self.underline = False
      self.fg_color = -1
      self.bg_color = -1
      
    def __call__(self, match):
      '''
      function call operator called by regex replace
      upon the finding of a match in msg sring
      '''
      if match.groupdict()['reset'] is not None:
        self.bold = False
        self.underline = False
        self.fg_color = -1
        self.bg_color = -1

      if match.groupdict()['bold'] is not None:
        self.bold = not self.bold

      if match.groupdict()['underline'] is not None:
        self.underline = not self.underline

      if match.groupdict()['color'] is not None:
        print str(match.groupdict())
        if match.groupdict()['fg'] is not None:
          self.fg_color = int(match.groupdict()['fg'])
      if match.groupdict()['bg'] is not None:
          self.bg_color = int(match.groupdict()['bg'])

      output = ''

      if not self.match_found:
        self.match_found=True
        output = '<span '
      else:
        output = '</span><span '

      if self.bold:
        output += 'weight="bold" '

      if self.underline:
        output += 'underline="single" '

      if self.fg_color >=0:
        output += 'color="' + color_code_to_X11(self.fg_color) + '" '

      if self.bg_color >=0:
        output += 'background="' +color_code_to_X11(self.bg_color) + '" '

      output += '>'

      return output

  regex = r'((?P<reset>\x0f)|(?P<underline>\x1f)|(?P<bold>\x02)|(?P<color>\x03(?P<fg>\d{1,2})?(,(?P<bg>\d{1,2}))?))+'
  markup_transform = MarkupFunctor()
  msg = re.sub(regex, markup_transform, msg)
  if markup_transform.match_found:
    msg += '</span>'
  return msg

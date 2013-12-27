# vim: set ts=2 expandtab:
"""

Module: pause.py
Desc: simple pause in animated queue of events
Author: John O'Neil
Email: oneil.john@gmail.com
DATE: Saturday, December 21st 2013
  
""" 
from animation import Animation


class Pause(Animation):

  def __init__(self, time_in_seconds):
    super(Pause,self).__init__()
    self.time_in_seconds = time_in_seconds
    self.time_elapsed = 0.0

  def do_update(self, dt):
    self.time_elapsed = self.time_elapsed + dt
    if self.time_elapsed >= self.time_in_seconds:
      self.done()

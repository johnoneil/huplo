# vim: set ts=2 expandtab:
"""

Module: position.py
Desc: Typical 2D position that can be tweened
Author: John O'Neil
Email: oneil.john@gmail.com
DATE: Saturday, December 21st 2013
  
""" 
from animation import Animation
from pyTweener import Tweener

class To(Animation):
  def __init__(self, position, x, y, t, tween_type=Tweener.LINEAR, relative=False):
    super(To, self).__init__()
    self.pos = position
    self.final_x = x
    self.final_y = y
    self.tween_type = tween_type
    self.relative = relative
    self.t = t

  def before_first_update(self, dt):
    self.tweener = Tweener()
    delta_x = self.final_x - self.pos.x
    delta_y = self.final_y - self.pos.y
    if self.relative:
      self.tweener.addTween(self.pos, x=self.final_x, y=self.final_y, tweenTime=self.t, tweenType=self.tween_type)
    else:
      self.tweener.addTween(self.pos, x=delta_x, y=delta_y, tweenTime=self.t, tweenType=self.tween_type)

  def do_update(self,dt):
    if self.tweener:
      self.tweener.update(dt)
      if not self.tweener.has_tweens():
        self.done()
      print str(self.pos.x) + ':' + str(self.pos.y)

class Position(object):
  def __init__(self, x, y):
    super(Position, self).__init__()
    self.x = x
    self.y = y

  def to(self, x, y, t, tween_type=Tweener.LINEAR):
    return To(self, x, y, t, tween_type)

  def to_relative(self, x, y, t, tween_type=Tweener.LINEAR):
    return To(self, x, y, t, tween_type, relative=True)



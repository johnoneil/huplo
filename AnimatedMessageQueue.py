# vim: set ts=2 expandtab:
"""
Module: AnimatedMessageQueue
Desc: A Cairo animated message display that neatly fades in/out a message queue
Author: John O'Neil
Email:

"""
import pyTweener
from pyTweener import Tweener

class color(object):
  def __init__(self, r, g, b, a=1.0):
    self._r = r
    self._g = g
    self._b = b
    self._a = a
    self._tweener = pyTweener.Tweener()

  @property
  def r(self):
    return self._r
  @r.setter
  def r(self,value):
    self._r = value
  @property
  def g(self):
    return self._g
  @g.setter
  def g(self,value):
    self._g = value
  @property
  def b(self):
    return self._b
  @b.setter
  def b(self,value):
    self._b = value
  @property
  def a(self):
    return self._a
  @a.setter
  def a(self,value):
    self._a = value

  def set_r(self,value):
    self._r = value
  def set_g(self,value):
    self._g = value
  def set_b(self,value):
    self._b = value
  def set_a(self,value):
    self._a = value

  def fade_out(self, t):
    self._tweener.addTween(self, set_a=0.0, tweenTime = t, tweenType=self._tweener.OUT_BOUNCE)
  def fade_in(self, t):
    self._tweener.addTween(self, set_a=1.0, tweenTime = t, tweenType=self._tweener.OUT_BOUNCE)
  def to(self, rv, gv, bv, av, t):
    self._tweener.addTween(self, set_r=rv, set_g=gv, set_b=bv, set_a=av, tweenTime = t, tweenType=self._tweener.OUT_QUAD)
  def update(self,dt):
    self._tweener.update(dt)

  @staticmethod
  def red():
    return color(1.0,0.0,0.0,1.0)
  @staticmethod
  def green():
    return color(0.0,1.0,0.0,1.0)
  @staticmethod
  def blue():
    return color(0.0,0.0,1.0,1.0)
  @staticmethod
  def yellow():
    return color(1.0,1.0,0.0,1.0)
  @staticmethod
  def white():
    return color(1.0,1.0,1.0,1.0)
  @staticmethod
  def black():
    return color(0.0,0.0,0.0,1.0)

class pos(object):
  def __init__(self, x, y):
    self._x = x
    self._y = y
    self._tweener = pyTweener.Tweener()

  @property
  def x(self):
    return self._x
  @x.setter
  def x(self,value):
    self._x = value
  @property
  def y(self):
    return self._y
  @y.setter
  def y(self,value):
    self._y = value

  def set_x(self,value):
    self._x = value

  def set_y(self,value):
    self._y = value

  def to(self, xv, yv, t):
    self._tweener.addTween(self, set_x=xv, set_y=yv, tweenTime = t, tweenType=self._tweener.OUT_BOUNCE)

  def update(self,dt):
    self._tweener.update(dt)

class AnimatedMessageQueEntry(object):
  def __init__(self, text, c = color.white() , p = pos(0.0,0.0) ):
    self._pos = p
    self._color = c
    self._text = text

  def update(self, dt):
    self._color.update(dt)
    self._pos.update(dt)

  def render(self,ctx):
    ctx.select_font_face("Arial")
    ctx.set_font_size(22)
    ctx.move_to( self._pos._x, self._pos._y)
    ctx.set_source_rgba(self._color.r, self._color.g, self._color.b, self._color.a)
    ctx.show_text(self._text)

class AnimatedMessageQueue(list):
  def __init__(self,  x, y, length = 5):
    self._length = length
    self._pos = pos(x,y)

  def push(self, item):
    self.insert(0, item)
    if(len(self) > self._length):
      self.pop()

  def notice(self, text, pos=pos(0.0,0.0), color=color.white()):
    new_entry = AnimatedMessageQueEntry(text, c=color,p=pos)
    self.push( new_entry )
    new_entry._pos.to( pos._x + 200.0, pos._y + 200.0, 5.0)

  def update(self, deltaT):
    for item in self:
      item.update(deltaT)

  def render(self, ctx):
    for item in self:
      item.render(ctx)
    

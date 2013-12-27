#!/usr/bin/python
# vim: set ts=2 expandtab:
"""
Module: color.py
Desc: local color implementation
Author: John O'Neil
Email: oneil.john@gmail.com
DATE: Monday, Dec 16th 2013
  
"""

from animation import Animation
from pyTweener import Tweener
from pyTweener import Tween

class Color(object):
  def __init__(self, r=1.0, g=1.0, b=1.0, a=1.0):
    self.r = r
    self.g = g
    self.b = b
    self.a = a

  def fade_out(self, t, tween_type=Tweener.LINEAR):
    self._tweener.addTween(self, set_a=0.0, tweenTime = t, tweenType=tween_type)

  def fade_in(self, t, tween_type=Tweener.LINEAR):
    self._tweener.addTween(self, set_a=1.0, tweenTime = t, tweenType=tween_type)

  def to(self, rv, gv, bv, av, t, tween_type=Tweener.LINEAR):
    self._tweener.addTween(self, set_r=rv, set_g=gv, set_b=bv, set_a=av, tweenTime = t, tweenType=tween_type)

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


Color.Red = Color(1.0, 0.0, 0.0)
Color.Green = Color(0.0, 1.0, 0.0)
Color.Blue = Color(0.0, 0.0, 1.0)
Color.Yellow = Color(1.0, 1.0, 0.0)
Color.White = Color(1.0, 1.0, 1.0)
Color.Black = Color(0.0, 0.0, 0.0)


class FadeIn(Animation):
  def __init__(self, obj, time_seconds, tween_type=Tweener().LINEAR):
    super(FadeIn,self).__init__()
    self.obj = obj
    self.time_seconds = time_seconds
    self.tweener = pyTweener.Tweener()
    self.tween_type = tween_type
    self.tween = None
  
  def Update(self, dt):
    if not self.tween:
      delta_a =  1.0 - self._obj.a
      self.tween = pyTweener.Tween(self.obj, self.time_seconds, self.tween_type, None, None, 0.0, a=delta_a)
    self.tween.update(dt)
    return self.update_siblings(dt, self.tween.complete)

class FadeOut(Animation):
  def __init__(self, obj, time_seconds, tween_type=Tweener().LINEAR):
    super(FadeOut,self).__init__()
    self.obj = obj
    self.time_seconds = time_seconds
    self.tweener = Tweener()
    self.tween_type = tween_type
    self.tween = None
  
  def Update(self, dt):
    if not self.tween:
      delta_a =  0.0 - self._obj.a
      self._tween = pyTweener.Tween(self.obj, self.time_seconds, self.tween_type, None, None, 0.0, a=delta_a)
    self.tween.update(dt)
    return self.update_siblings(dt, self.tween.complete)

'''
class ColorToRelative(Animation):
  def __init__(self, obj, r, g, b, a, time_seconds, tween_type=Tweener().LINEAR):
    super(ColorToRelative,self).__init__()
    self._target = color(r, g, b, a)
    self._obj = obj
    self._time_seconds = time_seconds
    self._tweener = pyTweener.Tweener()
    self._tween_type = self._tweener.LINEAR
    if( tween_type is not None):
      self._tween_type = tween_type
    self._tween = None
  
  def Update(self, dt):
    if( self._tween is None):
      self._tween = pyTweener.Tween(self._obj, self._time_seconds, self._tween_type, None, None, 0.0, set_r=self._target.r,set_g=self._target.g,set_b=self._target.b,set_a=self._target.a)
    self._tween.update(dt)
    return self.UpdateSiblings(dt, self._tween.complete )

class ColorToAbsolute(Animation):
  def __init__(self, obj, r, g, b, a, time_seconds, tween_type=Tweener().LINEAR):
    super(ColorToAbsolute,self).__init__()
    self._target = color(r, g, b, a)
    self._obj = obj
    self._time_seconds = time_seconds
    self._tweener = pyTweener.Tweener()
    self._tween_type = self._tweener.LINEAR
    if( tween_type is not None):
      self._tween_type = tween_type
    self._tween = None
  
  def Update(self, dt):
    if( self._tween is None):
      #pytweener (mysteriously) only uses relative tween values (tween to current value -1, e.g.)
      #here we assume input arguments are absolute, so we need to calculate deltas and pass them to the tween
      delta_r = self._target.get_r() - self._obj.get_r() 
      delta_g = self._target.get_g() - self._obj.get_g() 
      delta_b = self._target.get_b() - self._obj.get_b()
      delta_a = self._target.get_a() - self._obj.get_a() 
      self._tween = pyTweener.Tween(self._obj, self._time_seconds, self._tween_type, None, None, 0.0, set_r=delta_r,set_g=delta_g,set_b=delta_b,set_a=delta_a)
    self._tween.update(dt)
    return self.UpdateSiblings(dt, self._tween.complete )

class ColorTo(object):
  def ColorToRel(obj, r, g, b, a, time_seconds, tween_type = None):
    return ColorToRelative(obj._color, r, g, b, a, time_seconds, tween_type)
  def ColorTo(obj, r, g, b, a, time_seconds, tween_type =  None):
    return ColorToAbsolute(obj._color, r, g, b, a, time_seconds, tween_type)
  def FadeIn(obj, time_seconds, tween_type = None):
    return FadeIn(obj._color, time_seconds, tween_type)
  def FadeOut(obj, time_seconds, tween_type = None):
    return FadeOut(obj._color, time_seconds, tween_type)

'''

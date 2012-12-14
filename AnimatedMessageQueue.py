# vim: set ts=2 expandtab:
"""
Module: AnimatedMessageQueue
Desc: A Cairo animated message display that neatly fades in/out a message queue
Author: John O'Neil
Email:

"""
import pyTweener

class color(object):
  def __init__(self, r, g, b, a=1.0):
    self.r = r
    self.g = g
    self.b = b
    self.a = a

  @property
  def r(self):
    return self.r
  @r.setter
  def r(self,value):
    self.r = value
  @property
  def g(self):
    return self.g
  @g.setter
  def g(self,value):
    self.g = value
  @property
  def b(self):
    return self.b
  @b.setter
  def b(self,value):
    self.b = value
  @property
  def a(self):
    return self.a
  @a.setter
  def a(self,value):
    self.a = value

  def update(self,dt):
    pass

  @staticmethod
  def red():
    return color(1,0,0,1)
  @staticmethod
  def green():
    return color(0,1,0,1)
  @staticmethod
  def blue():
    return color(0,0,1,1)
  @staticmethod
  def yellow():
    return color(1,1,0,1)
  @staticmethod
  def white():
    return color(1,1,1,1)
  @staticmethod
  def black():
    return color(0,0,0,1)

class pos(object):
  def __init__(self, x, y):
    self.x = x
    self.y = y

  @property
  def x(self):
    return self.x
  @x.setter
  def x(self,value):
    self.x = value
  @property
  def y(self):
    return self.y
  @y.setter
  def y(self,value):
    self.y = value

class AnimatedMessageQueEntry(object):
  def __init__(self, text ):#c = color.white() , p = pos(0,0) ):
    #self.pos = p
    #self.color = c
    self.text = text
    self.tweener = Tweener()
    self.x = 0
    #@property
    #def x(self):
    #  return self.x
    #@x.setter
    #def x(self,value):
    #  self.x = value
  def fade_out(self):
    self.tweener.addTween(self, x=10, tweenTime=2.0, tweenType=Tweener.OUT_QUAD)
    #self.tweener.addTween(self, self.color.a=0, tweenTime=2.0, tweenType=Tweener.OUT_QUAD)
  #def fade_in(self):
  #  self.tweener.addTween(self, self.color.a=1, tweenTime=2.0, tweenType=Tweener.OUT_QUAD)
  #def move_to(self, xf, yf):
  #  self.tweener.addTween(self, pos.x = xf, pos.y = yf, tweenTime = 2.0, tweenType=Tweener.OUT_QUAD)
  #def update(self, dt):
  #  self.tweener.update(dt)
  #def render(self,ctx):
    ctx.select_font_face("Arial")
    #ctx.set_source_rgba (1.0, 1.0, 1.0, 1.0)
    ctx.set_font_size(22)
    #extents = ctx.text_extents(msg)
    #entry.w = extents[2]
    #ctx.move_to( entry.x + 2, entry.y + 2 )
    #ctx.set_source_rgb(0,0,0)
    #ctx.show_text(msg)
    #ctx.move_to( entry.x , entry.y )
    ctx.move_to( self.pos.x, self.pos.y)
    ctx.set_source_rgba(self.color.r, self.color.g, self.color.b, self.color.a)
    ctx.show_text(self.text)

class AnimatedMessageQueue(list):
  def __init__(self, length):
    self.length = length

  def push(self, length ):
    if(len(self) > self.length):
      self.pop()

  def render(self, deltaT):
    pass
    

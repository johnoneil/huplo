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
  @property
  def g(self):
    return self._g
  @property
  def b(self):
    return self._b
  @property
  def a(self):
    return self._a

  def get_r(self):
    return self._r
  def set_r(self,value):
    self._r = value
  def get_g(self):
    return self._g
  def set_g(self,value):
    self._g = value
  def get_b(self):
    return self._b  
  def set_b(self,value):
    self._b = value
  def get_a(self):
    return self._a  
  def set_a(self,value):
    self._a = value

  def fade_out(self, t, tween_type=None):
    if not tween_type:
      tween_type = self._tweener.LINEAR
    self._tweener.addTween(self, set_a=0.0, tweenTime = t, tweenType=tween_type)
  def fade_in(self, t, tween_type=None):
    if not tween_type:
      tween_type = self._tweener.LINEAR
    self._tweener.addTween(self, set_a=1.0, tweenTime = t, tweenType=tween_type)
  def to(self, rv, gv, bv, av, t, tween_type=None):
    if not tween_type:
      tween_type = self._tweener.LINEAR
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

class pos(object):
  def __init__(self, x, y):
    self._x = x
    self._y = y
    self._tweener = pyTweener.Tweener()

  @property
  def x(self):
    return self._x

  @property
  def y(self):
    return self._y

  def get_x(self):
    return self._x

  def set_x(self,value):
    self._x = value

  def get_y(self):
    return self._y  

  def set_y(self,value):
    self._y = value

  def to(self, xv, yv, t, tween_type=None):
    if not tween_type:
      tween_type = self._tweener.LINEAR
    self._tweener.addTween(self, set_x=xv, set_y=yv, tweenTime=t, tweenType=tween_type)

  def update(self,dt):
    self._tweener.update(dt)

class AnimatedMessageQueEntry(object):
  def __init__(self, text, c=None , p = None ):
    if p is None:
      p = pos(0.0,0.0)
    if c is None:
      c = color.white()
    self._pos = p
    self._color = c
    self._text = text

  def update(self, dt):
    self._color.update(dt)
    self._pos.update(dt)

  def render(self,ctx, offset_x, offset_y):
    ctx.select_font_face("Arial")
    ctx.set_font_size(22)
    ctx.move_to( self._pos._x + offset_x, self._pos._y + offset_y)
    ctx.set_source_rgba(self._color.r, self._color.g, self._color.b, self._color.a)
    ctx.show_text(self._text)

class Animation(object):
  """Basic animation queueable object. Top of a tree structure that describes
    various actions that will be performed (updated) simultaneous to the 
    current action ("Do X AND y") and what whill be performed AFTER the current
    action is completed ("do X THEN Y").
    Intended as a base class for various sorts of animations, simplest of which
    is a Pause.
  """
  def __init__(self):
    super(Animation, self).__init__()
    self._sibling = None
    self._child = None

  def UpdateSiblings(self, dt, complete):
    """Basic implementation of update functionality (uptate siblings,
      return child when this animation is complete, isolated in a
      method so that derived implementations can reuse it easily.
      :param dt: Floating point time in seconds elapsed since last update
      :type dt: float.
      :param complete: Is the current animation task complete?
      :type complete: bool.
      :returns a reference to the current object (self) or the next if
      this animation is complete.
    """
    if(self._sibling is not None):
      self._sibling = self._sibling.Update(dt)
      return self
    elif( complete is not True):
      return self
    else:
      return self._child

  def Update(self, dt):
    """Update the animation.
       This is meant to be called like:
       >>>
        if( myAnimation is not None):
          myAnimation = myAnimation.Update(dt)
       >>>
       thus
       using the state pattern, myAnimation will be assigned with the subsequent 
       next animation after the initial action (and its siblings) are complete.
       When the entire animation is complete myAnimation.Update(dt) returns None
      :param dt: Time elapsed in seconds since last update
      :type dt: float
      :returns Animation object or None if the animation is complete
    """
    return UpdateSiblings(self, True)
    

  def And(self, sibling):
    """Add a sibling (simultaneously updated) animation to the current
    animation. The current animation will not complete until all siblings
    are complete.
    Note, this method returns the self instance, so we can 
    chain calls:
    >>>
    animation1 = Animation().And(Animation()).And(Animation())
    while( animation1 is not None):
      animation1 = animation1.Update(1.0)
    >>>
    :param sibling: The next simultaneously updated animation object you
    wish to add
    :type sibling: Animation
    :returns Last sibling in the current animation chain, so we can chain calls.
    """
    if( self._sibling is not None):
      self._sibling.And(sibling)
    else:
      self._sibling = sibling
    return self

  def Then(self, child):
    """
    Add a subsequent ("child") animation to the current animation.
    The idea is we call Update() on a given animation, and when the parent completes,
    the child is returned from the Update() call. We therefore only need to keep track of
    one referene to the animation chain.
    >>>
    animation1 = Animation().Then(Animation()).Then(Animation())
    while( animation1 is not None):
      animation1 = animation1.Update(1.0)
    >>>
    """
    if( self._child is not None):
      self._child.Then(child)
    else:
      self._child = child
    return self
      

class Pause(Animation):
  def __init__(self, timeSec):
    super(Pause,self).__init__()
    self._timeSec(timeSec)
    self._timeElapsed = 0.0
  def Update(self, dt):
    self._timeElapsed = self._timeElapsed + dt
    return self.UpdateSibling(dt, (self._timeElapsed >= self._timeSec) )

class FadeIn(Animation):
  def __init__(self, obj, time_seconds, tween_type = None):
    super(FadeIn,self).__init__()
    self._obj = obj
    self._time_seconds = time_seconds
    self._tweener = pyTweener.Tweener()
    self._tween_type = self._tweener.LINEAR
    if( tween_type is not None):
      self._tween_type = tween_type
    self._tween = None
  
  def Update(self, dt):
    if( self._tween is None):
      self._tween = pyTweener.Tween(self._obj, self._time_seconds, self._tween_type, None, None, 0.0, set_a=1.0)
    self._tween.update(dt)
    return self.UpdateSiblings(dt, self._tween.complete )

class FadeOut(Animation):
  def __init__(self, obj, time_seconds, tween_type = None):
    super(FadeOut,self).__init__()
    self._obj = obj
    self._time_seconds = time_seconds
    self._tweener = pyTweener.Tweener()
    self._tween_type = self._tweener.LINEAR
    if( tween_type is not None):
      self._tween_type = tween_type
    self._tween = None
  
  def Update(self, dt):
    if( self._tween is None):
      self._tween = pyTweener.Tween(self._obj, self._time_seconds, self._tween_type, None, None, 0.0, set_a=0.5)
    self._tween.update(dt)
    return self.UpdateSiblings(dt, self._tween.complete )

class ColorTo(Animation):
  def __init__(self, obj, r, g, b, a, time_seconds, tween_type = None):
    super(ColorTo,self).__init__()
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

  

class MoveTo(Animation):
  def __init__(self, obj, pos, time_seconds, tween_type = None):
    super(MoveTo,self).__init__()
    self._obj = obj
    self._pos = pos
    self._time_seconds = time_seconds
    self._tweener = pyTweener.Tweener()
    self._tween_type = self._tweener.LINEAR
    if( tween_type is not None):
      self._tween_type = tween_type
    self._tween = None
    #self._tween = pyTweener.Tween(self._obj, self._time_seconds, self._tween_type, None, None, 0.0, set_x=pos.x, set_y=pos.y)
    #self._tween = pyTweener.Tween(self._obj, self._time_seconds, self._tween_type, None, None, 0.0, **kwargs)
    #self._tween = pyTweener.Tween(self._obj, self._time_seconds, self._tween_type, None, None, 0.0)
  
  def Update(self, dt):
    if( self._tween is None):
      self._tween = pyTweener.Tween(self._obj, self._time_seconds, self._tween_type, None, None, 0.0, set_x=self._pos.x, set_y=self._pos.y)
    self._tween.update(dt)
    return self.UpdateSiblings(dt, self._tween.complete )
    

class TextBox(object):
  def __init__(self, text, pos, text_color = None, bg_color = None, font = None):
    self._text = text
    self._pos = pos
    if text_color is None:
      self._text_color = color.white()
    else:
      self._text_color = text_color
    self._bg_color = bg_color
    self._font = font
    self._animation = None

  def MoveTo(self, pos, time_seconds, tween_type = None):
    return MoveTo(self, pos, time_seconds, tween_type)

class AnimatedMessageQueue(list):
  def __init__(self,  x, y, length = 5):
    self._length = length
    self._pos = pos(x,y)
    self._animation = None

  def push(self, item):
    self.insert(0, item)
    if(len(self) > self._length):
      self.pop()

  def notice(self, text, po=None, co=None):
    if po is None:
      po = pos(0.0,0.0)
    if co is None:
      co = color.white()
    new_entry = AnimatedMessageQueEntry(text, c=co,p=po)
    self.push( new_entry )
    new_entry._color.set_a(0.0)
    #self._animation = FadeIn(new_entry._color,3.0).Then(MoveTo(new_entry._pos,pos(100,100),4.0)).Then(MoveTo(new_entry._pos,pos(200,0),4.0)).Then(MoveTo(new_entry._pos,pos(0,200),4.0))
    #self._animation = MoveTo(new_entry._pos,pos(100,100),4.0).Then(MoveTo(new_entry._pos,pos(200,0),4.0)).Then(MoveTo(new_entry._pos,pos(0,200),4.0))
    self._animation = MoveTo(new_entry._pos,pos(100,100),4.0).And(FadeIn(new_entry._color,3.0)).Then(MoveTo(new_entry._pos,pos(200,0),4.0)).Then(MoveTo(new_entry._pos,pos(0,200),4.0)).Then(FadeOut(new_entry._color,3.0))
    self._animation = MoveTo(new_entry._pos,pos(100,100),4.0).And(FadeIn(new_entry._color,3.0)).Then(MoveTo(new_entry._pos,pos(200,0),4.0)).Then(MoveTo(new_entry._pos,pos(0,200),4.0)).Then(ColorTo(new_entry._color,1.0,0.0,0.0,1.0,3.0))
    #new_entry._pos.to( new_entry._pos._x + 200.0, new_entry._pos._y + 200.0, 5.0)

  def update(self, dt):
    if( self._animation is not None):
      self._animation = self._animation.Update(dt)
    for item in self:
      item.update(dt)

  def render(self, ctx):
    for item in self:
      item.render(ctx, self._pos.x, self._pos.y)
    

# vim: set ts=2 expandtab:
"""

Module: animation
Desc: Build structures of consecutive and parallel animated events
Author: John O'Neil
Email: oneil.john@gmail.com
DATE: Saturday, December 21st 2013
  
""" 

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
    self.sibling = None
    self.child = None
    self.complete = False
    self.updated = False

  def done(self):
    '''
    Method that derived classes ought to call when they complete what they've got to do
    '''
    self.complete = True

  def is_complete(self):
    return self.complete

  def before_first_update(self, dt):
    pass

  def after_last_update(self, dt):
    pass

  def update(self, dt):
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
    if not self.updated:
      self.before_first_update(dt)
      self.updated = True

    self.do_update(dt)

    if self.sibling:
      self.sibling = self.sibling.update(dt)

    if not self.complete:
      return self

    if self.child:
      self.child.AND(self.sibling)
      return self.child
    else:
      return self.sibling

  def do_update(self, dt):
    '''
    Derived classes ought to override this method to implement update loops
    They ought not override update() as that contains most of the basic update
    support and calls this update at the appropriate point.
    '''
    pass
    

  def AND(self, sibling):
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
    if not sibling:
      return self

    if self.sibling:
      self.sibling.AND(sibling)
    else:
      self.sibling = sibling
    return self

  def THEN(self, child):
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
    if not child:
      return self

    if self.child:
      self.child.THEN(child)
    else:
      self.child = child
    return self

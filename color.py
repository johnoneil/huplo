#!/usr/bin/python
# vim: set ts=2 expandtab:
"""
Module: color.py
Desc: local color implementation
Author: John O'Neil
Email: oneil.john@gmail.com
DATE: Monday, Dec 16th 2013
  
""" 

class Color(object):
  def __init__(self, r=1.0, g=1.0, b=1.0, a=1.0):
    self.R = r
    self.G = g
    self.B = b
    self.A = a

Color.Red = Color(1.0, 0.0, 0.0)
Color.Green = Color(0.0, 1.0, 0.0)
Color.Blue = Color(0.0, 0.0, 1.0)
Color.Yellow = Color(1.0, 1.0, 0.0)
Color.White = Color(1.0, 1.0, 1.0)
Color.Black = Color(0.0, 0.0, 0.0)

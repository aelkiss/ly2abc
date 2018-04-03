from fractions import Fraction

from ly2abc import flat,natural,sharp

import ly.document
import ly.music
import ly.music.items

def ly_snippet(snippet):
  return ly.music.document(ly.document.Document(snippet))[0]

class Pitch:
  def __init__(self,note,alter,octave):
    self.note = note
    self.alter = alter
    self.octave = octave
    self.absolute = None

  def makeAbsolute(self,last_pitch):
    self.absolute = last_pitch

  def copy(self):
    return self

Pitch.low_c = Pitch(0,0,0)
Pitch.c = Pitch(0,0,1)
Pitch.cs = Pitch(0,sharp,1)
Pitch.high_c = Pitch(0,0,2)
Pitch.d = Pitch(1,0,1)
Pitch.ds = Pitch(1,sharp,1)
Pitch.ef = Pitch(2,flat,1)
Pitch.e = Pitch(2,0,1)
Pitch.ff = Pitch(3,flat,1)
Pitch.f = Pitch(3,0,1)
Pitch.fs = Pitch(3,sharp,1)
Pitch.g = Pitch(4,0,1)
Pitch.af = Pitch(5,flat,1)
Pitch.a = Pitch(5,0,1)
Pitch.b = Pitch(6,0,1)
Pitch.bf = Pitch(6,flat,1)

class TestOutputter:
  def __init__(self):
    self.items = []

  def output(self,text):
    if text != "\n" or self.items[-1][-1] != "\n":
      self.items.append(text)

  def all_output(self):
    return "".join(self.items)


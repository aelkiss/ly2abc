from mamba import description, context, it
from expects import expect, equal
from fractions import Fraction

from ly2abc import NoteConverter

class FakePitch:
  def __init__(self,note,alter,octave):
    self.note = note
    self.alter = alter
    self.octave = octave

with description('ly2abc.NoteConverter') as self:

  with context('1/8 note'): 
    def length(self):
      return Fraction(1/8)

    with it('can convert a middle C 8th note to ABC'):
      pitch = FakePitch(0,0,1)
      expect(NoteConverter(pitch,self.length()).to_abc()).to(equal("C"))

    with it('can convert a high C 8th note to ABC'):
      pitch = FakePitch(0,0,2)
      expect(NoteConverter(pitch,self.length()).to_abc()).to(equal("c"))

    with it('can convert a low C 8th note to ABC'):
      pitch = FakePitch(0,0,0)
      expect(NoteConverter(pitch,self.length()).to_abc()).to(equal("C,"))

    with it('can convert a D above middle C to ABC'):
      pitch = FakePitch(1,0,1)
      expect(NoteConverter(pitch,self.length()).to_abc()).to(equal("D"))

    with it('can convert a Bb below middle C to ABC'):
      pitch = FakePitch(6,Fraction(-1,2),0)
      expect(NoteConverter(pitch,self.length()).to_abc()).to(equal("_B,"))

    with it('can convert a F# above middle C to ABC'):
      pitch = FakePitch(3,Fraction(1,2),0)
      expect(NoteConverter(pitch,self.length()).to_abc()).to(equal("^F,"))



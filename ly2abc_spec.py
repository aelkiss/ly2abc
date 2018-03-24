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
  def expect_abc(self,pitch,length,expected_abc):
    expect(NoteConverter(pitch,length).to_abc()).to(equal(expected_abc))

  with context('8th note'): 
    def length(self):
      return Fraction(1/8)

    with it('can convert a high C 8th note to ABC'):
      self.expect_abc(FakePitch(0,0,2),self.length(), "c")

    with it('can convert a low C 8th note to ABC'):
      self.expect_abc(FakePitch(0,0,0),self.length(), "C,")

    with it('can convert a D above middle C to ABC'):
      self.expect_abc(FakePitch(1,0,1),self.length(), "D")

    with it('can convert a Bb below middle C to ABC'):
      self.expect_abc(FakePitch(6,Fraction(-1,2),0),self.length(),"_B,")

    with it('can convert a F# above middle C to ABC'):
      self.expect_abc(FakePitch(3,Fraction(1,2),0),self.length(),"^F,")

  with context('middle C'):
    def middle_c(self):
      return FakePitch(0,0,1)

    with it('can convert an 8th note to ABC'):
      self.expect_abc(self.middle_c(),Fraction(1/8),"C")

    with it('can convert a quarter note to ABC'):
      self.expect_abc(self.middle_c(),Fraction(1/4),"C2")

    with it('can convert a dotted quarter note to ABC'):
      self.expect_abc(self.middle_c(),Fraction(3/8),"C3")

    with it('can convert a whole note to ABC'):
      self.expect_abc(self.middle_c(),Fraction(1),"C8")

    with it('can convert a 16th note to ABC'):
      self.expect_abc(self.middle_c(),Fraction(1/16),"C/")

    with it('can convert a 128th note to ABC'):
      self.expect_abc(self.middle_c(),Fraction(1/128),"C////")

    with _it('can convert a dotted 16th note to ABC'):
      self.expect_abc(self.middle_c(),Fraction(3/32),"C3/4")

    with _it('can convert a dotted 8th note to ABC'):
      self.expect_abc(self.middle_c(),Fraction(3/16),"C3/2")



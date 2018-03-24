from mamba import description, context, it
from expects import expect, equal
from fractions import Fraction

from ly2abc import *


class Pitch:
  def __init__(self,note,alter,octave):
    self.note = note
    self.alter = alter
    self.octave = octave

Pitch.low_c = Pitch(0,0,0)
Pitch.c = Pitch(0,0,1)
Pitch.high_c = Pitch(0,0,2)
Pitch.d = Pitch(1,0,1)
Pitch.ef = Pitch(2,Fraction(-1/2),1)
Pitch.e = Pitch(2,0,1)
Pitch.f = Pitch(3,0,1)
Pitch.fs = Pitch(3,Fraction(1/2),1)
Pitch.g = Pitch(4,0,1)
Pitch.a = Pitch(5,0,1)
Pitch.b = Pitch(6,0,1)
Pitch.bf = Pitch(6,Fraction(-1,2),1)


with description('ly2abc.NoteContext') as self:
  with it('can be constructed with number of sharps and a unit length'):
    expect(NoteContext(5,Fraction(1/4))).not_to(equal(None))

  with it('returns its number of sharps'):
    expect(NoteContext(5,Fraction(1/4)).sharps).to(equal(5))
  
  with it('returns its unit length'):
    expect(NoteContext(5,Fraction(1/4)).unit_length).to(equal(Fraction(1/4)))

  with it('defaults to no sharps'):
    expect(NoteContext().sharps).to(equal(0))

  with it('defaults to unit length of an 8th note'):
    expect(NoteContext().unit_length).to(equal(Fraction(1,8)))


with description('ly2abc.Note') as self:
  def expect_abc_note(self,pitch,length,context,expected_abc):
    expect(Note(pitch,length,context).to_abc()).to(equal(expected_abc))

  with context('with no sharps and a unit length of 1/8'):
    def context(self):
      return NoteContext(0,Fraction(1/8))

    def expect_abc_pitch(self,pitch,abc):
      self.expect_abc_note(pitch,self.context().unit_length,self.context(),abc)

    with it('converts a high C 8th note to ABC with no accidental'):
      self.expect_abc_pitch(Pitch.high_c,"c")

    with it('converts a low C 8th note to ABC with no accidental'):
      self.expect_abc_pitch(Pitch.low_c,"C,")

    with it('converts a D above middle C to ABC with no accidental'):
      self.expect_abc_pitch(Pitch.d, "D")

    with it('converts a Bb above middle C to ABC with an accidental'):
      self.expect_abc_pitch(Pitch.bf,"_B")

    with it('converts a F# above middle C to ABC with an accidental'):
      self.expect_abc_pitch(Pitch.fs,"^F")

    with context('middle C'):
      def expect_abc_note_length(self,duration,abc):
        self.expect_abc_note(Pitch.c,duration,self.context(),abc)

      with it('converts an 8th note to ABC'):
        self.expect_abc_note_length(Fraction(1/8),"C")

      with it('converts a quarter note to ABC'):
        self.expect_abc_note_length(Fraction(1/4),"C2")

      with it('converts a dotted quarter note to ABC'):
        self.expect_abc_note_length(Fraction(3/8),"C3")

      with it('converts a whole note to ABC'):
        self.expect_abc_note_length(Fraction(1),"C8")

      with it('converts a 16th note to ABC'):
        self.expect_abc_note_length(Fraction(1/16),"C/")

      with it('converts a 128th note to ABC'):
        self.expect_abc_note_length(Fraction(1/128),"C////")

      with it('converts a dotted 16th note to ABC'):
        self.expect_abc_note_length(Fraction(3/32),"C3//")

      with it('converts a dotted 8th note to ABC'):
        self.expect_abc_note_length(Fraction(3/16),"C3/")

  with context('with one sharp'):
    def context(self):
      return NoteContext(1,Fraction(1/8))

    def expect_abc_pitch(self,pitch,abc):
      self.expect_abc_note(pitch,self.context().unit_length,self.context(),abc)

    with it('does not put an accidental before F#'):
      self.expect_abc_pitch(Pitch.fs,"F")

    with it('puts an natural before F'):
      self.expect_abc_pitch(Pitch.f,"=F")

    with it('does not put an accidental before C'):
      self.expect_abc_pitch(Pitch.c,"C")

  with description('key_alter') as self:

    def expect_alter(self,note,sharps,alter):
      expect(Note(getattr(Pitch,note),1,NoteContext(sharps=sharps)).key_alter()).to(equal(alter))

    with it("has no accidentals in C major"):
      for note in ["c","d","e","f","g","a","b"]:
        self.expect_alter(note,sharps('C','major'),0)

    with it("has an F sharp in G major"):
      for note in "f":
        self.expect_alter(note,sharps('G','major'),Fraction(1/2))
      for note in ["c","d","e","g","a","b"]:
        self.expect_alter(note,sharps('G','major'),0)

    with it("has an F,C, and G sharp in A major"):
      for note in ["f","c","g"]:
        self.expect_alter(note,sharps('A','major'),Fraction(1/2))
      for note in ["d","e","a","b"]:
        self.expect_alter(note,sharps('A','major'),0)

    with it("has all sharps in C# major"):
      for note in ["c","d","e","g","a","b"]:
        self.expect_alter(note,sharps('C#','major'),Fraction(1/2))

    with it("has one flat in F major"):
      for note in ["b"]:
        self.expect_alter(note,sharps('F','major'),Fraction(-1/2))
      for note in ["c","d","e","f","g"]:
        self.expect_alter(note,sharps('F','major'),Fraction(0))

    with it("has three flats in C minor"):
      for note in ["b","e","a"]:
        self.expect_alter(note,sharps('C','minor'),Fraction(-1/2))
      for note in ["c","d","f","g"]:
        self.expect_alter(note,sharps('C','minor'),Fraction(0))

    with it("has all flats in Ab minor"):
      for note in ["c","d","e","g","a","b"]:
        self.expect_alter(note,sharps('Ab','minor'),Fraction(-1/2))

with description('Key') as self:
  with it('takes a pitch and a mode'):
    expect(Key(Pitch.c,'major')).not_to(equal(None))

with description('sharps') as self:
  with _it('has 0 sharps for Cmajor'):
    expect(Key(Pitch.c,'major').sharps).to(equal(0))

with description('to_abc') as self:
  with _it('handles Cmajor'):
    expect(Key(Pitch.c,'major').to_abc).to(equal("Cmajor"))
        
        
#        ('C','major')).to(equal(0))

  with it('has 3 flats for Eb major'):
    expect(sharps('Eb','major')).to(equal(-3))

  with it('has 4 sharps for E major'):
    expect(sharps('E','major')).to(equal(4))

  with it('has 3 flats for C minor'):
    expect(sharps('C','minor')).to(equal(-3))

  with it('has 0 sharps for D dorian'):
    expect(sharps('D','dorian')).to(equal(0))

  with it('has 2 sharps for A mixolydian'):
    expect(sharps('A','mixolydian')).to(equal(2))

  with it('has 2 sharps for A mixolydian'):
    expect(sharps('A','mixolydian')).to(equal(2))

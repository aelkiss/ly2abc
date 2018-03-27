from mamba import description, context, it
from expects import expect, equal, contain
from fractions import Fraction

from ly2abc import Note, NoteContext, Key
from spec.ly2abc_spec_helper import *

with description('ly2abc.Note') as self:
  def expect_abc_note(self,pitch,length,context,expected_abc):
    expect(Note(pitch,length,context).to_abc()).to(equal(expected_abc))

  with context('with no sharps and a unit length of 1/16'):
    def context(self):
      return NoteContext(0,Fraction(1/16))

    with it('gives a length of 4 for a quarter note'):
      self.expect_abc_note(Pitch.c,Fraction(1/4),self.context(),"C4")

    with it('gives a length of // for a 64th note'):
      self.expect_abc_note(Pitch.c,Fraction(1/64),self.context(),"C//")

  with context('with no sharps and a unit length of 1/4'):
    def context(self):
      return NoteContext(0,Fraction(1/4))

    with it('gives no length modifier for a quarter note'):
      self.expect_abc_note(Pitch.c,Fraction(1/4),self.context(),"C")

    with it('gives a length of // for a 16th note'):
      self.expect_abc_note(Pitch.c,Fraction(1/16),self.context(),"C//")

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

    with context('no pitch'):
      def expect_abc_rest(self,duration,abc):
        self.expect_abc_note(None,duration,self.context(),abc)

      with it('converts an 8th rest to ABC'):
        self.expect_abc_rest(Fraction(1/8),"z")

      with it('converts a quarter rest to ABC'):
        self.expect_abc_rest(Fraction(1/4),"z2")

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

  with context('with two flats'):
    def context(self):
      return NoteContext(-2,Fraction(1/8))

    def expect_abc_pitch(self,pitch,abc):
      self.expect_abc_note(pitch,self.context().unit_length,self.context(),abc)

    with it('does not put an accidental before Eb'):
      self.expect_abc_pitch(Pitch.ef,"E")

    with it('puts a natural before E'):
      self.expect_abc_pitch(Pitch.e,"=E")


  with description('key_alter') as self:

    def expect_alter(self,note,key,alter):
      expect(Note(getattr(Pitch,note),1,NoteContext(sharps=key.sharps())).key_alter()).to(equal(alter))

    with it("has no accidentals in C major"):
      for note in ["c","d","e","f","g","a","b"]:
        self.expect_alter(note,Key(Pitch.c,'major'),natural)

    with it("has an F sharp in G major"):
      for note in "f":
        self.expect_alter(note,Key(Pitch.g,'major'),sharp)
      for note in ["c","d","e","g","a","b"]:
        self.expect_alter(note,Key(Pitch.g,'major'),natural)

    with it("has an F,C, and G sharp in A major"):
      for note in ["f","c","g"]:
        self.expect_alter(note,Key(Pitch.a,'major'),sharp)
      for note in ["d","e","a","b"]:
        self.expect_alter(note,Key(Pitch.a,'major'),natural)

    with it("has all sharps in C# major"):
      for note in ["c","d","e","g","a","b"]:
        self.expect_alter(note,Key(Pitch.cs,'major'),sharp)

    with it("has one flat in F major"):
      for note in ["b"]:
        self.expect_alter(note,Key(Pitch.f,'major'),flat)
      for note in ["c","d","e","f","g"]:
        self.expect_alter(note,Key(Pitch.f,'major'),natural)

    with it("has three flats in C minor"):
      for note in ["b","e","a"]:
        self.expect_alter(note,Key(Pitch.c,'minor'),flat)
      for note in ["c","d","f","g"]:
        self.expect_alter(note,Key(Pitch.c,'minor'),natural)

    with it("has all flats in Ab minor"):
      for note in ["c","d","e","g","a","b"]:
        self.expect_alter(note,Key(Pitch.af,'minor'),flat)

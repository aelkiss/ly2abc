from mamba import description, context, it
from expects import expect, equal, contain
from fractions import Fraction

from ly2abc import *

import ly.document
import ly.music
import ly.music.items


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

def ly_snippet(snippet):
  return ly.music.document(ly.document.Document(snippet))[0]

class Repeat:
  def __init__(self,specifier,repeat_count,inner_music=[]):
    self.specifier = lambda: specifier
    self.repeat_count = lambda: repeat_count
    self.inner_music = inner_music

  def __iter__(self):
    return iter(self.inner_music)

class LyNote:
  def __init__(self,pitch,length):
    self.pitch = pitch
    self.length = lambda: length

class LyRest:
  def __init__(self,length):
    self.length = lambda: length

class TimeSignature:
  def __init__(self,numerator,denominator):
    self.numerator = lambda: numerator
    self.fraction = lambda: Fraction(1,denominator)

class KeySignature:
  def __init__(self,pitch,mode):
    self.pitch = lambda: pitch
    self.mode = lambda: mode

class TestOutputter:
  def __init__(self):
    self.items = []

  def output(self,stuff):
    self.items.append(stuff)

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

with description('Key') as self:
  with it('takes a pitch and a mode'):
    expect(Key(Pitch.c,'major')).not_to(equal(None))

  with description('sharps') as self:
    with it('has 0 sharps for Cmajor'):
      expect(Key(Pitch.c,'major').sharps()).to(equal(0))

    with it('has 3 flats for Eb major'):
      expect(Key(Pitch.ef,'major').sharps()).to(equal(-3))

    with it('has 4 sharps for E major'):
      expect(Key(Pitch.e,'major').sharps()).to(equal(4))

    with it('has 3 flats for C minor'):
      expect(Key(Pitch.c,'minor').sharps()).to(equal(-3))

    with it('has 0 sharps for D dorian'):
      expect(Key(Pitch.d,'dorian').sharps()).to(equal(0))

    with it('has 2 sharps for A mixolydian'):
      expect(Key(Pitch.a,'mixolydian').sharps()).to(equal(2))

    with it('has 9 sharps for D# major'):
      expect(Key(Pitch.ds,'major').sharps()).to(equal(9))

    with it('has 8 flats for Fb major'):
      expect(Key(Pitch.ff,'major').sharps()).to(equal(-8))

  with description('to_abc') as self:
    with it('handles C major'):
      expect(Key(Pitch.c,'major').to_abc()).to(equal("C major"))

    with it('handles E major'):
      expect(Key(Pitch.e,'major').to_abc()).to(equal('E major'))

    with it('handles D dorian'):
      expect(Key(Pitch.d,'dorian').to_abc()).to(equal('D dorian'))

    with it('handles Eb major'):
      expect(Key(Pitch.ef,'major').to_abc()).to(equal('Eb major'))

    with it('handles F# minor'):
      expect(Key(Pitch.fs,'minor').to_abc()).to(equal('F# minor'))

with description('BarManager') as self:
  with context('in 6/8 time'):
    def bar_manager(self):
      return BarManager(6,8)

    with it('can be constructed'):
      expect(self.bar_manager()).not_to(equal(None))

    with it('can pass time'):
      expect(self.bar_manager().pass_time(Fraction(1/8))).to(equal(None))

    with description('line_break'):

      with it('does not put a line break after 5 measures have passed'):
        bar_manager = self.bar_manager()
        bar_manager.pass_time(Fraction(5*6,8))
        expect(bar_manager.line_break()).to(equal(False))

      with it('does not put a line break after 6 measures and one beat have passed'):
        bar_manager = self.bar_manager()
        bar_manager.pass_time(Fraction(6*6+1,8))
        expect(bar_manager.line_break()).to(equal(False))

      with it('does not put a line break after 6 measures and half a beat have passed'):
        bar_manager = self.bar_manager()
        bar_manager.pass_time(Fraction(6*12+1,16))
        expect(bar_manager.line_break()).to(equal(False))

      with it('puts line break after 6 measures have passed'):
        bar_manager = self.bar_manager()
        bar_manager.pass_time(Fraction(6*6,8))
        expect(bar_manager.line_break()).to(equal(True))

      with it('puts a line break after 18 measures have passed'):
        bar_manager = self.bar_manager()
        bar_manager.pass_time(Fraction(18*6,8))
        expect(bar_manager.line_break()).to(equal(True))

    with description('bar_line'):
      with it('puts a bar line after one measure has passed'):
        bar_manager = self.bar_manager()
        bar_manager.pass_time(Fraction(6,8))
        expect(bar_manager.bar_line()).to(equal(True))

      with it('does not put a bar line after one beat has passed'):
        bar_manager = self.bar_manager()
        bar_manager.pass_time(Fraction(1,8))
        expect(bar_manager.bar_line()).to(equal(False))

      with it('puts a bar line after five measures have passed'):
        bar_manager = self.bar_manager()
        bar_manager.pass_time(Fraction(5*6,8))
        expect(bar_manager.bar_line()).to(equal(True))

      with it('does not put a bar line after one measure and one beat have passed'):
        bar_manager = self.bar_manager()
        bar_manager.pass_time(Fraction(7,8))
        expect(bar_manager.bar_line()).to(equal(False))

    with description('beam_break'):
      with it('puts a beam break after three beats have passed'):
        bar_manager = self.bar_manager()
        bar_manager.pass_time(Fraction(3,8))
        expect(bar_manager.beam_break()).to(equal(True))

      with it('does not put a beam break after five beats have passed'):
        bar_manager = self.bar_manager()
        bar_manager.pass_time(Fraction(5,8))
        expect(bar_manager.beam_break()).to(equal(False))

      with it('puts a beam break after nine beats have passed'):
        bar_manager = self.bar_manager()
        bar_manager.pass_time(Fraction(9,8))
        expect(bar_manager.beam_break()).to(equal(True))

      with it('puts a beam break after six beats have passed'):
        bar_manager = self.bar_manager()
        bar_manager.pass_time(Fraction(6,8))
        expect(bar_manager.beam_break()).to(equal(True))


  with context('in 4/4 time'):
    def bar_manager(self):
      return BarManager(4,4)

    with it('puts a beam break after 2 beats have passed'):
      bar_manager = self.bar_manager()
      bar_manager.pass_time(Fraction(2,4))
      expect(bar_manager.beam_break()).to(equal(True))

    with it('does not put a beam break after 3 beats have passed'):
      bar_manager = self.bar_manager()
      bar_manager.pass_time(Fraction(3,4))
      expect(bar_manager.beam_break()).to(equal(False))

    with it('puts a line break after 12 measures have passed'):
      bar_manager = self.bar_manager()
      bar_manager.pass_time(Fraction(12*4,4))
      expect(bar_manager.line_break()).to(equal(True))

    with it('does not put a line break after 5 measures have passed'):
      bar_manager = self.bar_manager()
      bar_manager.pass_time(Fraction(5*4,4))
      expect(bar_manager.line_break()).to(equal(False))

    with it('puts a bar line after five measures have passed'):
      bar_manager = self.bar_manager()
      bar_manager.pass_time(Fraction(5*4,4))
      expect(bar_manager.bar_line()).to(equal(True))

    with it('does not put a bar line after one measure and one beat have passed'):
      bar_manager = self.bar_manager()
      bar_manager.pass_time(Fraction(5,4))
      expect(bar_manager.bar_line()).to(equal(False))

  with context('in 3/4 time'):
    def bar_manager(self):
      return BarManager(3,4)

    with it('does not put a beam break after 2 beats have passed'):
      bar_manager = self.bar_manager()
      bar_manager.pass_time(Fraction(2,4))
      expect(bar_manager.beam_break()).to(equal(False))

    with it('does not put a beam break after 1.5 beats have passed'):
      bar_manager = self.bar_manager()
      bar_manager.pass_time(Fraction(3,8))
      expect(bar_manager.beam_break()).to(equal(False))

    with it('puts a beam break after 3 beats have passed'):
      bar_manager = self.bar_manager()
      bar_manager.pass_time(Fraction(3,4))
      expect(bar_manager.beam_break()).to(equal(True))

    with it('puts a line break after 12 measures have passed'):
      bar_manager = self.bar_manager()
      bar_manager.pass_time(Fraction(12*3,4))
      expect(bar_manager.line_break()).to(equal(True))

    with it('does not put a line break after 5 measures have passed'):
      bar_manager = self.bar_manager()
      bar_manager.pass_time(Fraction(5*3,4))
      expect(bar_manager.line_break()).to(equal(False))

    with it('puts a bar line after five measures have passed'):
      bar_manager = self.bar_manager()
      bar_manager.pass_time(Fraction(5*3,4))
      expect(bar_manager.bar_line()).to(equal(True))

    with it('does not put a bar line after one measure and one beat have passed'):
      bar_manager = self.bar_manager()
      bar_manager.pass_time(Fraction(5,4))
      expect(bar_manager.bar_line()).to(equal(False))

  with description("time_signature"):
    with it('returns 6/8 for 6/8'):
      expect(BarManager(6,8).time_signature()).to(equal("6/8"))

    with it('returns 4/4 for 4/4'):
      expect(BarManager(4,4).time_signature()).to(equal("4/4"))

with description('LilypondMusic') as self:
  with before.each:
    self.output = TestOutputter()
    self.l = LilypondMusic(music=None,outputter=self.output)

  with it('can be constructed'):
    expect(LilypondMusic('foo')).not_to(equal(None))

  with description('time_signature'):
    with context('in 6/8'):
      with before.each:
        self.l.time_signature(TimeSignature(6,8))

      with it('sets the bar manager'):
        expect(self.l.bar_manager.numerator).to(equal(6))
        expect(self.l.bar_manager.denominator).to(equal(8))

      with it('sets the unit length to 1/8'):
        expect(self.l.unit_length).to(equal(Fraction(1,8)))

      with it('prints an M line'):
        expect(self.output.items).to(contain('M: 6/8\n'))

      with it('prints an L line'):
        expect(self.output.items).to(contain('L: 1/8\n'))

    with context('in 2/2'):
      with before.each:
        self.l.time_signature(TimeSignature(2,2))

      with it('sets the bar manager'):
        expect(self.l.bar_manager.numerator).to(equal(2))
        expect(self.l.bar_manager.denominator).to(equal(2))

      with it('sets the unit length to 1/4'):
        expect(self.l.unit_length).to(equal(Fraction(1,4)))

      with it('prints an M line'):
        expect(self.output.items).to(contain('M: 2/2\n'))

      with it('prints an L line'):
        expect(self.output.items).to(contain('L: 1/4\n'))

    with context('in 2/4'):
      with before.each:
        self.l.time_signature(TimeSignature(2,4))

      with it('sets the bar manager'):
        expect(self.l.bar_manager.numerator).to(equal(2))
        expect(self.l.bar_manager.denominator).to(equal(4))

      with it('sets the unit length to 1/16'):
        expect(self.l.unit_length).to(equal(Fraction(1,16)))

      with it('prints an M line'):
        expect(self.output.items).to(contain('M: 2/4\n'))

      with it('prints an L line'):
        expect(self.output.items).to(contain('L: 1/16\n'))

    with context('a change in time signature from 6/8 to 2/2'):
      with before.each:
        self.l.time_signature(TimeSignature(6,8))
        self.l.time_signature(TimeSignature(2,2))

      with it('sets the bar manager'):
        expect(self.l.bar_manager.numerator).to(equal(2))
        expect(self.l.bar_manager.denominator).to(equal(2))

      with it('does not change the unit length'):
        expect(self.l.unit_length).to(equal(Fraction(1,8)))

      with it('prints an M for the changed time signature'):
        expect(self.output.items).to(contain("M: 2/2\n"))

      with it('does not print an L line for the changed time signature'):
        expect(self.output.items).not_to(contain('L: 1/4\n'))

  with description('key_signature'):
    with context('in C major'):
      with before.each:
        self.l.key_signature(KeySignature(Pitch.c,'major'))

      with it('sets the key in the note context'):
        expect(self.l.note_context.sharps).to(equal(0))

      with it('outputs the key'):
        expect(self.output.items).to(contain('K: C major\n'))

    with context('in F# minor'):
      with before.each:
        self.l.key_signature(KeySignature(Pitch.fs,'minor'))

      with it('sets the key in the note context'):
        expect(self.l.note_context.sharps).to(equal(3))

      with it('outputs the key'):
        expect(self.output.items).to(contain('K: F# minor\n'))

  with context('with a piece in 4/4 in C major'):
    with before.each:
      self.l.time_signature(TimeSignature(4,4))
      self.l.key_signature(KeySignature(Pitch.c,'major'))
      self.base_pitch = Pitch.c
      self.l.last_pitch = self.base_pitch

    with context('music_list'):
      with it('outputs a continuation marker before a key change'):
        self.l.music_list(ly_snippet("{ c1 \\time 6/8 }"))
        expect(self.output.items).to(contain('\\\n','M: 6/8\n'))

      with it('outputs a continuation marker before a tempo change'):
        self.l.music_list(ly_snippet("{ c1 \\key ees\\dorian }"))
        expect(self.output.items).to(contain('\\\n','K: Eb dorian\n'))

      with it('outputs notes inside it'):
        self.l.music_list(ly_snippet("{ c8 d e }"))
        expect(self.output.items).to(contain('C','D','E'))
    
      with it('handles relative octave'):
        self.l.music_list(ly_snippet("{ c8 c' d}"))
        expect(self.output.items).to(contain('C','c','d'))

    with description('note'):
      with context('with a quarter note E above middle C'):
        with before.each:
          self.ly_note = LyNote(Pitch.e,Fraction(1/4))
          self.l.note(self.ly_note)

        with it('passes time equaling the length of the note'):
          expect(self.l.bar_manager.elapsed_time).to(equal(Fraction(1/4)))

        with it('makes it absolute with respect to the previous pitch'):
          expect(self.ly_note.pitch.absolute).to(equal(self.base_pitch))

        with it('prints the note'):
          expect(self.output.items).to(contain('E2'))

        with it('updates the last pitch'):
          expect(self.l.last_pitch).to(equal(self.l.last_pitch))

                    
      with description('rest'):
        with context('with a 8th rest'):
          with before.each:
            self.l.rest(LyRest(Fraction(1/8)))

          with it('outputs the rest'):
            expect(self.output.items).to(contain('z'))

          with it('passes time equaling the length of the rest'):
            expect(self.l.bar_manager.elapsed_time).to(equal(Fraction(1/8)))

      with description('repeat'):
        with context('with a volta repeat'):
          with before.each:
            handlers = { str: lambda x,_: self.l.output(x) }
            self.l.repeat(Repeat('volta',2,["some","thing"]),handlers)

          with it('first outputs an opening repeat'):
            expect(self.output.items).to(contain('|: '))

          with it('traverses inner music with the given handlers'):
            expect(self.output.items).to(contain('some'))
            expect(self.output.items).to(contain('thing'))

          with it('outputs a closing repeat'):
            expect(self.output.items).to(contain(':| '))

        with context('with an unfolded repeat'):
          with before.each:
            handlers = { str: lambda x,_: self.l.output(x) }
            self.l.repeat(Repeat('unfold',3,["some","thing"]),handlers)

          with it('does not output a repeat bar'):
            expect(self.output.items).not_to(contain('|: '))

          with it('duplicates the inner music the specified number of times'):
            expect(self.output.items).to(contain('some','thing','some','thing','some','thing'))

  with context('traverse'):
    with it('calls the specified handler for each item in the node'):
      self.l.traverse([1,2,3],{ int: lambda x,_: self.l.output(x) })
      expect(self.output.items).to(equal([1,2,3]))

    with it('iterates on children for classes without a handler'):
      self.l.traverse([1,2,[3,4],5],{ int: lambda x,_: self.l.output(x) })
      expect(self.output.items).to(equal([1,2,3,4,5]))

  with context('to_abc'):
    with it('outputs abc for a snippet with time signature and key signature'):
      snippet = ly_snippet("{ \\key c \\major \\time 3/4 \\relative c' { c4 d e | c' d e | c,2 e4 | d2. } }")
      LilypondMusic(music=snippet,outputter=self.output).output_abc()
      expect(str.join("",self.output.items)).to(equal("""K: C major
M: 3/4
L: 1/8
C2D2E2 | c2d2e2 | C4E2 | D6 | """))

    with it('breaks beams in the middle of 4/4 measure and breaks lines every 6 measures'):
      snippet = ly_snippet("{ \\key c \\major \\time 4/4 \\relative c' { \\repeat unfold 16 { c8 d e f f e d c } }")
      LilypondMusic(music=snippet,outputter=self.output).output_abc()
      expect(str.join("",self.output.items)).to(equal("""K: C major
M: 4/4
L: 1/8
CDEF FEDC | CDEF FEDC | CDEF FEDC | CDEF FEDC | CDEF FEDC | CDEF FEDC | 
CDEF FEDC | CDEF FEDC | CDEF FEDC | CDEF FEDC | CDEF FEDC | CDEF FEDC | 
CDEF FEDC | CDEF FEDC | CDEF FEDC | CDEF FEDC | """))


from mamba import description, context, it
from expects import expect, equal, contain, end_with
from fractions import Fraction

from ly2abc.lilypond_music import LilypondMusic
from ly2abc.output_buffer import OutputBuffer
from spec.ly2abc_spec_helper import *


class LyCommand:
  def __init__(self,text,siblings=[]):
    self.token = text
    self.next_sibling = lambda: siblings[0]
    
class LyString:
  def __init__(self,text):
    self.plaintext = lambda: text

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

class Partial:
  def __init__(self,duration):
    self.partial_length = lambda: duration


with description('LilypondMusic') as self:
  with before.each:
    self.output = OutputBuffer(TestOutputter())
    self.l = LilypondMusic(music=None,outputter=self.output)

  with it('can be constructed'):
    expect(LilypondMusic('foo')).not_to(equal(None))

  with description('time_signature'):
    with context('in 6/8'):
      with before.each:
        self.l.time_signature(TimeSignature(6,8))
        self.l.outputter.print_buffer()

      with it('sets the bar manager'):
        expect(self.l.bar_manager.numerator).to(equal(6))
        expect(self.l.bar_manager.denominator).to(equal(8))

      with it('sets the unit length to 1/8'):
        expect(self.l.unit_length).to(equal(Fraction(1,8)))

      with it('prints an M line'):
        expect(self.output.all_output()).to(contain('M: 6/8\n'))

      with it('prints an L line'):
        expect(self.output.all_output()).to(contain('L: 1/8\n'))

    with context('in 2/2'):
      with before.each:
        self.l.time_signature(TimeSignature(2,2))
        self.l.outputter.print_buffer()

      with it('sets the bar manager'):
        expect(self.l.bar_manager.numerator).to(equal(2))
        expect(self.l.bar_manager.denominator).to(equal(2))

      with it('sets the unit length to 1/4'):
        expect(self.l.unit_length).to(equal(Fraction(1,4)))

      with it('prints an M line'):
        expect(self.output.all_output()).to(contain('M: 2/2\n'))

      with it('prints an L line'):
        expect(self.output.all_output()).to(contain('L: 1/4\n'))

    with context('in 2/4'):
      with before.each:
        self.l.time_signature(TimeSignature(2,4))
        self.l.outputter.print_buffer()

      with it('sets the bar manager'):
        expect(self.l.bar_manager.numerator).to(equal(2))
        expect(self.l.bar_manager.denominator).to(equal(4))

      with it('sets the unit length to 1/16'):
        expect(self.l.unit_length).to(equal(Fraction(1,16)))

      with it('prints an M line'):
        expect(self.output.all_output()).to(contain('M: 2/4\n'))

      with it('prints an L line'):
        expect(self.output.all_output()).to(contain('L: 1/16\n'))

    with context('a change in time signature from 6/8 to 2/2'):
      with before.each:
        self.l.time_signature(TimeSignature(6,8))
        self.l.ouputter = self.l.bar_manager.pass_time(Fraction(6,8))
        self.l.time_signature(TimeSignature(2,2))
        self.l.ouputter = self.l.bar_manager.pass_time(Fraction(2,2))

      with it('sets the bar manager'):
        expect(self.l.bar_manager.numerator).to(equal(2))
        expect(self.l.bar_manager.denominator).to(equal(2))

      with it('does not change the unit length'):
        expect(self.l.unit_length).to(equal(Fraction(1,8)))

      with it('prints an M for the changed time signature'):
        expect(self.output.all_output()).to(contain("M: 2/2\n"))

      with it('does not print an L line for the changed time signature'):
        expect(self.output.all_output()).not_to(contain('L: 1/4\n'))

  with description('key_signature'):
    with context('in C major'):
      with before.each:
        self.l.key_signature(KeySignature(Pitch.c,'major'))
        self.l.outputter.print_buffer()

      with it('sets the key in the note context'):
        expect(self.l.note_context.sharps).to(equal(0))

      with it('outputs the key'):
        expect(self.output.all_output()).to(contain('K: C major\n'))

    with context('in F# minor'):
      with before.each:
        self.l.key_signature(KeySignature(Pitch.fs,'minor'))
        self.l.outputter.print_buffer()

      with it('sets the key in the note context'):
        expect(self.l.note_context.sharps).to(equal(3))

      with it('outputs the key'):
        expect(self.output.all_output()).to(contain('K: F# minor\n'))

  with context('with a piece in 4/4 in C major'):
    with before.each:
      self.l.time_signature(TimeSignature(4,4))
      self.l.key_signature(KeySignature(Pitch.c,'major'))
      self.base_pitch = Pitch.c
      self.l.last_pitch = self.base_pitch

      with it('outputs a barline before a meter change'):
        self.l.music_list(ly_snippet("{ c1 \\time 6/8 c4. c4. }"))
        self.l.pass_time()
        expect(self.output.all_output()).to(contain("| \nM: 6/8\n"))

      with it('outputs a barline marker before a key change'):
        self.l.music_list(ly_snippet("{ c1 \\key ees\\dorian c1 }"))
        self.l.pass_time()
        expect(self.output.all_output()).to(contain('C8 | \nK: Eb dorian\n'))

      with it('outputs notes inside it'):
        self.l.music_list(ly_snippet("{ c8 d e }"))
        self.l.pass_time()
        expect(self.output.all_output()).to(contain('CDE'))
    
      with it('handles relative octave'):
        self.l.music_list(ly_snippet("{ c8 c' d}"))
        self.l.pass_time()
        expect(self.output.all_output()).to(contain('Ccd'))

    with context('partial'):
      with it('rewinds the elapsed time by the length of the partial'):
        self.l.partial(Partial(Fraction(1,4)))
        expect(self.l.bar_manager.elapsed_time).to(equal(Fraction(-1,4)))

    with description('note'):
      with context('with a quarter note E above middle C'):
        with before.each:
          self.l.relative_mode = True
          self.ly_note = LyNote(Pitch.e,Fraction(1/4))
          self.l.note(self.ly_note)
          self.l.pass_time()
          self.output.reify()

        with it('passes time equaling the length of the note'):
          expect(self.l.bar_manager.elapsed_time).to(equal(Fraction(1/4)))

        with it('makes it absolute with respect to the previous pitch'):
          expect(self.ly_note.pitch.absolute).to(equal(self.base_pitch))

        with it('prints the note'):
          expect(self.output.outputter.items).to(contain('E2'))

        with it('updates the last pitch'):
          expect(self.l.last_pitch).to(equal(self.l.last_pitch))

      with description('barline'):
        def barline(self,lilypond_music,text):
          lilypond_music.command(LyCommand("\\bar",siblings=[LyString(text)]))
          lilypond_music.outputter.print_buffer()

        with it('outputs the bar immediately'):
          self.barline(self.l,'||')
          expect(self.output.all_output()).to(end_with(' || '))

        with it('outputs a normal barline if requested'):
          self.barline(self.l,'|')
          expect(self.output.all_output()).to(end_with(' | '))

        with it('translates a thick-thin double bar to ABC'):
          self.barline(self.l,'.|')
          expect(self.output.all_output()).to(end_with(' [| '))

        with it('translates a thick-thin double bar to ABC'):
          self.barline(self.l,'|.')
          expect(self.output.outputter.items[-1]).to(equal(' |] '))

        with it('prints unhandled barlines as a regular barline'):
          self.barline(self.l,'foo')
          expect(self.output.outputter.items[-1]).to(equal(' | '))

        with it('prevents double-printing barlines'):
          self.l.ouputter = self.l.bar_manager.pass_time(1)
          self.l.command(LyCommand("\\bar",siblings=[LyString('||')]))
          self.l.pass_time()
          expect(self.output.outputter.all_output()).to(end_with(" || "))

        with it('prints barlines in the middle of a measure'):
          self.l.ouputter = self.l.bar_manager.pass_time(1/4)
          self.l.command(LyCommand("\\bar",siblings=[LyString('||')]))
          self.l.ouputter = self.l.bar_manager.pass_time(3/4)
          self.l.pass_time()
          expect(self.output.all_output()).to(contain("||  | "))

        with it('handles repeat barlines'):
          self.l.command(LyCommand("\\bar",siblings=[LyString('.|:')]))
          self.l.ouputter = self.l.bar_manager.pass_time(1)
          self.l.command(LyCommand("\\bar",siblings=[LyString(':|.')]))
          self.l.pass_time()
          expect(self.output.all_output()).to(contain("|:  :|"))

                    
      with description('rest'):
        with context('with a 8th rest'):
          with before.each:
            self.l.rest(LyRest(Fraction(1/8)))
            self.l.pass_time()
            self.output.reify()

          with it('outputs the rest'):
            expect(self.output.outputter.items).to(contain('z'))

          with it('passes time equaling the length of the rest'):
            expect(self.l.bar_manager.elapsed_time).to(equal(Fraction(1/8)))

      with description('repeat'):

        def handlers(self):
          return { str: lambda x,_: self.str_handler(self,x,None) }

        with context('with a volta repeat'):
          with before.each:
            def str_handler(string,_):
              self.l.ouputter = self.l.bar_manager.pass_time(Fraction(1,2))
              self.l.outputter.output_test(string)
            handlers = { str: lambda x,_: str_handler(x,None) }

            self.l.repeat(Repeat('volta',2,["some","thing"]), handlers)
            self.l.pass_time()
            self.output.reify()

          with it('first outputs an opening repeat'):
            expect(self.output.outputter.all_output()).to(contain(' |: '))

          with it('traverses inner music with the given handlers'):
            expect(self.output.outputter.items).to(contain('some'))
            expect(self.output.outputter.items).to(contain('thing'))

          with it('outputs a closing repeat'):
            expect(self.output.outputter.all_output()).to(contain(' :| '))

        with context('with an unfolded repeat'):
          with before.each:
            handlers = { str: lambda x,_: self.l.outputter.output_test(x) }
            self.l.repeat(Repeat('unfold',3,["some","thing"]),handlers)

          with it('does not output a repeat bar'):
            expect(self.output.outputter.items).not_to(contain('|: '))

          with it('duplicates the inner music the specified number of times'):
            expect(self.output.outputter.items).to(contain('some','thing','some','thing','some','thing'))

        with it('combines :| and |: if needed'):
          def str_handler(string,_):
            self.l.ouputter = self.l.bar_manager.pass_time(Fraction(1,2))
            self.l.outputter.output_test(string)
          handlers = { str: lambda x,_: str_handler(x,None) }

          self.l.relative_mode = True
          self.l.music_list(ly_snippet("{ \\repeat volta 2 { c2 c } \\repeat volta 2 { c2 c } }"))
          self.l.pass_time()
          expect(self.output.all_output()).to(contain('|: C4 C4 :: C4 C4 :|'))

  with context('traverse'):
    with it('calls the specified handler for each item in the node'):
      self.l.traverse([1,2,3],{ int: lambda x,_: self.l.outputter.output_test(x) })
      expect(self.output.outputter.items).to(equal([1,2,3]))

    with it('iterates on children for classes without a handler'):
      self.l.traverse([1,2,[3,4],5],{ int: lambda x,_: self.l.outputter.output_test(x) })
      expect(self.output.outputter.items).to(equal([1,2,3,4,5]))

from mamba import description, context, it
from expects import expect, equal, contain
from fractions import Fraction

from ly2abc.lilypond_music import LilypondMusic
from ly2abc.output_buffer import OutputBuffer
from spec.ly2abc_spec_helper import ly_snippet, TestOutputter

import ly.music

def output_snippet(time,music,outputter):
  snippet = ly_snippet("{ \\key c \\major \\time %s \\relative c' { %s } }" % (time,music))
  LilypondMusic(music=snippet,outputter=outputter).output_abc()

def output_chord_snippet(time,music,chords,outputter):
  snippet = ly_snippet("{ \\key c \\major \\time %s \\relative c' { %s } \\chordmode { %s }}" % (time,music,chords))
  LilypondMusic(music=snippet,outputter=outputter).output_abc()

with description('LilypondMusic') as self:
  with before.each:
    self.output = OutputBuffer(TestOutputter())

  with context('to_abc'):
    with it('outputs abc for a snippet with time signature and key signature'):
      output_snippet("3/4","c4 d e | c' d e | c,2 e4 | d2.",self.output)
      expect(self.output.all_output()).to(equal("""K: C major
M: 3/4
L: 1/8
C2D2E2 | c2d2e2 | C4E2 | D6 | """))

    with it('breaks beams in the middle of 4/4 measure and breaks lines every 6 measures'):
      output_snippet("4/4","\\repeat unfold 16 { c8 d e f f e d c }",self.output)
      expect(self.output.all_output()).to(equal("""K: C major
M: 4/4
L: 1/8
CDEF FEDC | CDEF FEDC | CDEF FEDC | CDEF FEDC | CDEF FEDC | CDEF FEDC | 
CDEF FEDC | CDEF FEDC | CDEF FEDC | CDEF FEDC | CDEF FEDC | CDEF FEDC | 
CDEF FEDC | CDEF FEDC | CDEF FEDC | CDEF FEDC | """))

    with it('prints only one barline where there is a repeat'):
      output_snippet("4/4","\\repeat volta 2 { c4 d e f c d e f }",self.output)
      expect(self.output.all_output()).to(contain("|: C2D2 E2F2 | C2D2 E2F2 :|"))

    with it('handles manually-specified barlines'):
      output_snippet("2/2","c4 d \\bar \"||\" e f \\bar \"|.\" }",self.output)
      expect(self.output.all_output()).to(contain("CD || EF |]"))

    with it('handles \\partial'):
      output_snippet("4/4","\\partial 4 d4 | c d e f",self.output)
      expect(self.output.all_output()).to(contain("D2 | C2D2 E2F2 |"))

    with it('handles \\ppMark'):
      output_snippet("2/2","\\ppMark c4 d e f  \\ppMark g e d c",self.output)
      expect(self.output.all_output()).to(contain("\"^A\"CD EF | \"^B\"GE DC |"))

    with it('handles \\ppMark correctly before a repeat'):
      output_snippet("2/2","\\ppMark { c4 d e f f1 \\ppMark \\repeat volta 2 { g4 e d c  f e d c }",self.output)
      expect(self.output.all_output()).to(contain("\"^A\"CD EF | F4 \"^B\"|: GE DC | FE DC :|"))

    with it('handles \\ppMarkA by outputting the mark before the note'):
      output_snippet("2/2","c4^\\ppMarkA d e f  g^\\ppMarkB e d c",self.output)
      expect(self.output.all_output()).to(contain("\"^A\"CD EF | \"^B\"GE DC |"))

    with it('outputs a repeat marker before a time change'):
      output_snippet("4/4","c4 d e f \\time 6/8 \\repeat volta 2 { c8 d e f g a }",self.output)
      expect(self.output.all_output()).to(contain("""
C2D2 E2F2 |: 
M: 6/8
CDE FGA :| """))

    with it('outputs a repeat marker before a part change'):
      output_snippet("4/4","c4^\ppMarkA d e f \\repeat volta 2 { c4^\ppMarkB d e f }",self.output)
      expect(self.output.all_output()).to(contain("\"^A\"C2D2 E2F2 |: \"^B\"C2D2 E2F2 :|"))

    with it('outputs a repeat marker at the end of the bar'):
      output_snippet("6/8","\\repeat volta 2 { c8 d e e d c c2. }",self.output)
      expect(self.output.all_output()).to(contain("|: CDE EDC | C6 :|"))

    with it('outputs time signature immediately after a manual bar'):
      output_snippet("4/4","c4 d e f \\bar \"||\" \\time 6/4 c d e f g a \\time 6/8 a8 g f f g a \\bar \"|.\"",self.output)
      expect(self.output.all_output()).to(contain("""
C2D2 E2F2 || 
M: 6/4
C2D2E2 F2G2A2 | 
M: 6/8
AGF FGA |] """))

    with it('outputs all assigns if none are specified'):
      snippet = ly.music.document(ly.document.Document("global = { \\key c \\major \\time 4/4 } \nfoo = \\relative c' { c1 } \nbar = \\relative c' { d1 }"))
      LilypondMusic(music=snippet,outputter=self.output).output_abc()
      expect(self.output.all_output()).to(contain("C8 | D8 |"))

    with it('outputs only the given assigns if some are specified'):
      snippet = ly.music.document(ly.document.Document("global = { \\key c \\major \\time 4/4 } \nfoo = \\relative c' { c1 } \nbar = \\relative c' { d1 }\nbaz = \\relative c' { e1 }"))
      LilypondMusic(music=snippet,outputter=self.output,output_assigns=['global','foo','baz']).output_abc()
      expect(self.output.all_output()).to(contain("C8 | E8 |"))

    with it('handles transposition'):
      snippet = ly.music.document(ly.document.Document("\\key c \\major \\time 4/4 \\transpose c d \\relative c' { c4 d e f } \\relative c' { f e d c }"))
      LilypondMusic(music=snippet,outputter=self.output,output_assigns=['global','foo','baz']).output_abc()
      expect(self.output.all_output()).to(contain("D2E2 ^F2G2 | F2E2 D2C2 |"))

    with it('handles transposition with octave changes in the music'):
      snippet = ly.music.document(ly.document.Document("\\key c \\major \\time 4/4 \\transpose c d \\relative c' { f4 c' }"))
      LilypondMusic(music=snippet,outputter=self.output,output_assigns=['global','foo','baz']).output_abc()
      expect(self.output.all_output()).to(contain("G2d2"))

    with it('handles tied notes'):
      output_snippet("6/8","c4.~ c4 c8",self.output)
      expect(self.output.all_output()).to(contain("C3- C2C"))

    with it('handles \mark'):
      output_snippet("6/8","\\mark c4. c \\mark c4. c",self.output)
      expect(self.output.all_output()).to(contain("\"^A\"C3 C3 | \"^B\"C3 C3"))

    with it('handles \mark with argument'):
      output_snippet("6/8","\\mark \"X\" c4. c",self.output)
      expect(self.output.all_output()).to(contain("\"^X\"C3 C3"))

    with it('handles \mark with argument before end repeat'):
      output_snippet("6/8","\\repeat volta 2 { c4. c \\mark \"(3)\" } c c",self.output)
      expect(self.output.all_output()).to(contain("|: C3 C3 \"^(3)\":| C3 C3"))

    with it('handles \mark with argument before open/close repeat'):
      output_snippet("6/8","\\repeat volta 2 { c4. c \\mark \"(3)\" } \\repeat volta 2 { c c }",self.output)
      expect(self.output.all_output()).to(contain("|: C3 C3 \"^(3)\":: C3 C3 :|"))

    with it('handles repeats in a row'):
      output_snippet("4/4","\\repeat volta 2 { c2 c } \\repeat volta 2 { c c }",self.output)
      expect(self.output.all_output()).to(contain("|: C4 C4 :: C4 C4 :|"))

    with it('outputs a final barline'):
      output_snippet("4/4","c2 c",self.output)
      expect(self.output.all_output()).to(contain("C4 C4 |"))

    with it('handles postfix markup'):
      output_snippet("4/4","c2^\\markup{some text} c2",self.output)
      expect(self.output.all_output()).to(contain("\"^some text\"C4 C4 | "))

    with it('handles chord mode'):
      output_chord_snippet("4/4","c2 d2 e2 f2","c1 g1",self.output)
      expect(self.output.all_output()).to(contain("\"C\"C4 D4 | \"G\"E4 F4"))

    with it('handles chord modifiers'):
      output_chord_snippet("4/4","c2 d2 e2 f2 g2 a2","c1:m g1:7 d1:sus4",self.output)
      expect(self.output.all_output()).to(contain("\"Cm\"C4 D4 | \"G7\"E4 F4 | \"Dsus4\"G4 A4"))

    with it('handles chord mode with sharps/flats'):
      output_chord_snippet("4/4","c2 d2 e2 f2","fis1:m bes1",self.output)
      expect(self.output.all_output()).to(contain("\"F#m\"C4 D4 | \"Bb\"E4 F4"))

    with it('handles transposed chord mode'):
      snippet = ly.music.document(ly.document.Document("\\key c \\major \\time 4/4 \\transpose c d \\relative c' { c2 d e f } \\transpose c d \\chordmode { c1 g1 }"))
      LilypondMusic(music=snippet,outputter=self.output,output_assigns=['global','foo','baz']).output_abc()
      expect(self.output.all_output()).to(contain("\"D\"D4 E4 | \"A\"^F4 G4"))


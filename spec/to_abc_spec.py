from mamba import description, context, it
from expects import expect, equal, contain
from fractions import Fraction

from ly2abc import LilypondMusic
from spec.ly2abc_spec_helper import ly_snippet, TestOutputter

with description('LilypondMusic') as self:
  with before.each:
    self.output = TestOutputter()
    self.l = LilypondMusic(music=None,outputter=self.output)
  with context('to_abc'):
    with it('outputs abc for a snippet with time signature and key signature'):
      snippet = ly_snippet("{ \\key c \\major \\time 3/4 \\relative c' { c4 d e | c' d e | c,2 e4 | d2. } }")
      LilypondMusic(music=snippet,outputter=self.output).output_abc()
      expect(self.output.all_output()).to(equal("""K: C major
M: 3/4
L: 1/8
C2D2E2 | c2d2e2 | C4E2 | D6 | """))

    with it('breaks beams in the middle of 4/4 measure and breaks lines every 6 measures'):
      snippet = ly_snippet("{ \\key c \\major \\time 4/4 \\relative c' { \\repeat unfold 16 { c8 d e f f e d c } }")
      LilypondMusic(music=snippet,outputter=self.output).output_abc()
      expect(self.output.all_output()).to(equal("""K: C major
M: 4/4
L: 1/8
CDEF FEDC | CDEF FEDC | CDEF FEDC | CDEF FEDC | CDEF FEDC | CDEF FEDC | 
CDEF FEDC | CDEF FEDC | CDEF FEDC | CDEF FEDC | CDEF FEDC | CDEF FEDC | 
CDEF FEDC | CDEF FEDC | CDEF FEDC | CDEF FEDC | """))

    with it('prints only one barline where there is a repeat'):
      snippet = ly_snippet("{ \\key c \\major \\time 4/4 \\relative c' { \\repeat volta 2 { c4 d e f c d e f } } }")
      LilypondMusic(music=snippet,outputter=self.output).output_abc()
      expect(self.output.all_output()).to(equal("""K: C major
M: 4/4
L: 1/8
 |: C2D2 E2F2 | C2D2 E2F2 :| """))

    with it('handles manually-specified barlines'):
      snippet = ly_snippet("{ \\key c \major \\time 2/2 \\relative c' { c4 d \\bar \"||\" e f \\bar \"|.\" }")
      LilypondMusic(music=snippet,outputter=self.output).output_abc()
      expect(self.output.all_output()).to(equal("""K: C major
M: 2/2
L: 1/4
CD || EF |] """))



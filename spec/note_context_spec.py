from mamba import description, context, it
from expects import expect, equal, contain
from fractions import Fraction

from ly2abc.note import NoteContext

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


from mamba import description, context, it
from expects import expect, equal, contain
from fractions import Fraction

from ly2abc.note import Key
from spec.ly2abc_spec_helper import *

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

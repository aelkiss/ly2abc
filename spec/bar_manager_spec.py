from mamba import description, context, it
from expects import expect, equal, contain
from fractions import Fraction

from ly2abc import BarManager

from spec.ly2abc_spec_helper import TestOutputter

with description('BarManager') as self:
  with context('in 6/8 time'):
    def bar_manager(self):
      return BarManager(6,8,outputter=TestOutputter())

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

    with description('bar_type'):
      with it('can set the kind of barline to output'):
        bar_manager = self.bar_manager()
        bar_manager.bar_type = ":|"
        expect(bar_manager.bar_type).to(equal(":|"))

      with it('outputs the current barline if one is set'):
        bar_manager = self.bar_manager()
        bar_manager.pass_time(Fraction(6,8))
        bar_manager.bar_type = ":|"
        bar_manager.pass_time(Fraction(6,8))
        expect(bar_manager.outputter.items).to(contain(' :| '))

      with it('outputs | if no barline overrode it'):
        bar_manager = self.bar_manager()
        bar_manager.pass_time(Fraction(6,8))
        bar_manager.pass_time(Fraction(6,8))
        expect(bar_manager.outputter.items).to(contain(' | '))

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

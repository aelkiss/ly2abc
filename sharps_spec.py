
from mamba import description, context, it
from expects import expect, equal
from fractions import Fraction

circle = ['Cb', 'Gb', 'Db', 'Ab', 'Eb', 'Bb', 'F', 'C', 'G', 'D', 'A', 'E', 'B', 'F#', 'C#']
modes = { 'major': 0,
          'mixolydian': -1,
          'dorian': -2,
          'minor': -3 }

def sharps(note,mode):
  return circle.index(note) - 7 + modes[mode]

def accidental(note,key_sharps):
  sharp_order = circle.index(note) - 5
  flat_order = sharp_order - 8
  if(key_sharps > 0 and sharp_order <= key_sharps):
    return Fraction(1/2)
  elif(key_sharps < 0 and flat_order >= key_sharps):
    return Fraction(-1/2)
  else:
    return 0

with description('sharps') as self:
  with it('has 0 sharps for Cmajor'):
    expect(sharps('C','major')).to(equal(0))

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

with description('accidental') as self:
  with it("has no accidentals in C major"):
    for pitch in ['C','D','E','F','G','A','B']:
      expect(accidental(pitch,sharps('C','major'))).to(equal(0))

  with it("has an F sharp in G major"):
    for pitch in ['F']:
      expect(accidental(pitch,sharps('G','major'))).to(equal(Fraction(1/2)))
    for pitch in ['C','D','E','G','A','B']:
      expect(accidental(pitch,sharps('G','major'))).to(equal(0))

  with it("has an F,C, and G sharp in A major"):
    for pitch in ['F','C','G']:
      expect(accidental(pitch,sharps('A','major'))).to(equal(Fraction(1/2)))
    for pitch in ['D','E','A','B']:
      expect(accidental(pitch,sharps('A','major'))).to(equal(0))

  with it("has all sharps in C# major"):
    for pitch in ['C','D','E','F','G','A','B']:
      expect(accidental(pitch,sharps('C#','major'))).to(equal(Fraction(1/2)))

  with it("has one flat in F major"):
    for pitch in ['B']:
      expect(accidental(pitch,sharps('F','major'))).to(equal(Fraction(-1/2)))
    for pitch in ['C','D','E','G','A']:
      expect(accidental(pitch,sharps('F','major'))).to(equal(0))

  with it("has three flats in C minor"):
    for pitch in ['B','E','A']:
      expect(accidental(pitch,sharps('C','minor'))).to(equal(Fraction(-1/2)))
    for pitch in ['C','D','G']:
      expect(accidental(pitch,sharps('C','minor'))).to(equal(0))

  with it("has all flats in Ab minor"):
    for pitch in ['C','D','E','F','G','A','B']:
      expect(accidental(pitch,sharps('Ab','minor'))).to(equal(Fraction(-1/2)))

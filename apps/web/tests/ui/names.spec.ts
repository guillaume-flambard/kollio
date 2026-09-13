import { describe, expect, it } from 'vitest'
import { personInitials } from '../../app/utils/names'

describe('personInitials', () => {
  it('takes the first letters of the first two words', () => {
    expect(personInitials('Ada Lovelace')).toBe('AL')
  })

  it('handles a single name', () => {
    expect(personInitials('Plato')).toBe('P')
  })

  it('ignores extra words and whitespace', () => {
    expect(personInitials('  Grace   Brewster   Murray  Hopper ')).toBe('GB')
  })
})

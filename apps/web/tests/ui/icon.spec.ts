import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import KollioIcon from '../../app/components/kollio/Icon.vue'

const names = [
  'plus',
  'menu',
  'close',
  'chevron-up',
  'chevron-down',
  'chevron-right',
  'arrow-right',
  'message',
  'ellipsis',
  'search',
] as const

describe('KollioIcon', () => {
  it.each(names)('renders the %s glyph as vector paths', (name) => {
    const wrapper = mount(KollioIcon, { props: { name } })
    const svg = wrapper.find('svg')
    expect(svg.exists()).toBe(true)
    expect(svg.attributes('viewBox')).toBe('0 0 24 24')
    expect(wrapper.findAll('path, circle').length).toBeGreaterThan(0)
  })
})

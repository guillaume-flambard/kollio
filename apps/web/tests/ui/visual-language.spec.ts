import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import FeltMark from '../../app/components/kollio/FeltMark.vue'
import HandDrawnArrow from '../../app/components/kollio/HandDrawnArrow.vue'
import Artwork from '../../app/components/kollio/Artwork.vue'
import RelationshipConnector from '../../app/components/kollio/RelationshipConnector.vue'

describe('Kollio visual language', () => {
  it('renders a reusable felt mark with a separate grain pass', () => {
    const wrapper = mount(FeltMark, {
      props: { size: 'hero' },
      slots: { default: 'without losing the thread' },
    })

    expect(wrapper.text()).toBe('without losing the thread')
    expect(wrapper.get('.felt-mark').classes()).toContain('felt-mark--hero')
    expect(wrapper.findAll('svg path')).toHaveLength(2)
  })

  it('uses a dedicated downward curve for the left-facing annotation arrow', () => {
    const wrapper = mount(HandDrawnArrow, {
      props: { direction: 'down-left' },
    })

    expect(wrapper.get('.hand-arrow__main').attributes('d')).toBe('M60 6C74 28 71 52 51 72')
    expect(wrapper.findAll('path')).toHaveLength(3)
  })

  it('keeps connector endpoints explicit and independently configurable', () => {
    const wrapper = mount(RelationshipConnector, {
      props: {
        path: 'M10 20 C30 20 40 50 60 50',
        startX: 10,
        startY: 20,
        endX: 60,
        endY: 50,
        showEnd: false,
      },
    })

    expect(wrapper.get('path').attributes('d')).toBe('M10 20 C30 20 40 50 60 50')
    expect(wrapper.findAll('circle')).toHaveLength(1)
  })

  it('renders generated outcome artwork as decorative content', () => {
    const wrapper = mount(Artwork, {
      props: { name: 'explainable-decisions' },
    })

    const image = wrapper.get('img')
    expect(image.attributes('src')).toBe('/images/landing/explainable-decisions.svg')
    expect(image.attributes('alt')).toBe('')
    expect(image.attributes('aria-hidden')).toBe('true')
  })

  it('exposes narrative artwork through the same typed component', () => {
    const wrapper = mount(Artwork, {
      props: { name: 'decision-memory' },
    })

    expect(wrapper.get('img').attributes('src')).toBe('/images/landing/decision-memory.svg')
  })
})

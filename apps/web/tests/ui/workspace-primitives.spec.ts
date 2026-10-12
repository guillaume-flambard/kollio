import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import FeedbackState from '../../app/components/kollio/FeedbackState.vue'
import PageHeader from '../../app/components/kollio/PageHeader.vue'
import ReasoningBlock from '../../app/components/kollio/ReasoningBlock.vue'
import StatusMark from '../../app/components/kollio/StatusMark.vue'

describe('workspace primitives', () => {
  it('keeps an empty state actionable and keyboard-reachable', () => {
    const wrapper = mount(FeedbackState, {
      props: { title: 'Nothing needs attention', actionLabel: 'Open a decision' },
    })

    expect(wrapper.get('button').attributes('type')).toBe('button')
    expect(wrapper.text()).toContain('Nothing needs attention')
  })

  it('distinguishes an open question from settled reasoning', () => {
    const wrapper = mount(ReasoningBlock, {
      props: { title: 'A question remains', tone: 'question' },
      slots: { default: 'Do we have enough evidence?' },
    })

    expect(wrapper.classes()).toContain('reasoning-block--question')
    expect(wrapper.text()).toContain('Do we have enough evidence?')
  })

  it('keeps the page action adjacent to its decision context', () => {
    const wrapper = mount(PageHeader, {
      props: { eyebrow: 'Frame the decision', title: 'Where should we focus?' },
      slots: { action: '<button type="button">Continue</button>' },
    })

    expect(wrapper.get('h1').text()).toBe('Where should we focus?')
    expect(wrapper.get('.page-header__action button').text()).toBe('Continue')
  })

  it('uses semantic state rather than a decorative badge', () => {
    const wrapper = mount(StatusMark, { props: { label: 'Exploring', tone: 'active' } })

    expect(wrapper.attributes('aria-label')).toBe('Exploring')
    expect(wrapper.classes()).toContain('status-mark--active')
  })
})

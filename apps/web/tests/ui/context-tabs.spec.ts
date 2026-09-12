import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import ContextTabs from '../../app/components/kollio/ContextTabs.vue'

const items = [
  { id: 'team', label: 'Team' },
  { id: 'questions', label: 'Questions (0)' },
  { id: 'evidence', label: 'Evidence (0)' },
]

describe('ContextTabs', () => {
  it('exposes one selected tab and its controlled panel', async () => {
    const wrapper = mount(ContextTabs, {
      props: {
        items,
        label: 'Idea context',
        modelValue: 'team',
        idPrefix: 'idea-context',
      },
    })

    const tabs = wrapper.findAll('[role="tab"]')
    expect(tabs.map(tab => tab.attributes('aria-selected'))).toEqual(['true', 'false', 'false'])
    expect(tabs[0]?.attributes('aria-controls')).toBe('idea-context-panel')
    expect(tabs[0]?.attributes('tabindex')).toBe('0')
    expect(tabs[1]?.attributes('tabindex')).toBe('-1')
  })

  it('moves selection and focus with arrow keys', async () => {
    const wrapper = mount(ContextTabs, {
      attachTo: document.body,
      props: {
        items,
        label: 'Idea context',
        modelValue: 'team',
        idPrefix: 'idea-context',
        'onUpdate:modelValue': value => wrapper.setProps({ modelValue: value }),
      },
    })

    const firstTab = wrapper.findAll('[role="tab"]')[0]
    await firstTab?.trigger('keydown', { key: 'ArrowRight' })
    await nextTick()

    const tabs = wrapper.findAll('[role="tab"]')
    expect(tabs[1]?.attributes('aria-selected')).toBe('true')
    expect(document.activeElement).toBe(tabs[1]?.element)
    wrapper.unmount()
  })
})

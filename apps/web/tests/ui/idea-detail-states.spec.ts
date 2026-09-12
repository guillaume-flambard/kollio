import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'
import IdeaDetailError from '../../app/components/kollio/IdeaDetailError.vue'
import IdeaDetailSkeleton from '../../app/components/kollio/IdeaDetailSkeleton.vue'

describe('Idea detail states', () => {
  it('announces loading while keeping both layout surfaces present', async () => {
    const wrapper = mount(IdeaDetailSkeleton, {
      props: { label: 'Loading idea' },
    })

    expect(wrapper.get('[role="status"]').text()).toContain('Loading idea')
    expect(wrapper.findAll('.kollio-surface')).toHaveLength(2)
  })

  it('keeps the error recovery actions available', async () => {
    const wrapper = mount(IdeaDetailError, {
      props: {
        title: 'Idea unavailable',
        description: 'Try again later.',
        retryLabel: 'Try again',
        backLabel: 'Explore ideas',
        backTo: '/workspace',
      },
      global: {
        stubs: {
          NuxtLink: {
            props: ['to'],
            template: '<a :href="to"><slot /></a>',
          },
        },
      },
    })

    expect(wrapper.get('[role="alert"]').text()).toContain('Idea unavailable')
    await wrapper.get('button').trigger('click')
    expect(wrapper.emitted('retry')).toHaveLength(1)
    expect(wrapper.get('a').attributes('href')).toBe('/workspace')
  })

  it('does not depend on animation completion when reduced motion is requested', async () => {
    vi.stubGlobal('matchMedia', vi.fn().mockReturnValue({
      matches: true,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
    }))

    const wrapper = mount(IdeaDetailSkeleton, {
      props: { label: 'Loading idea' },
    })

    expect(wrapper.get('[role="status"]').attributes('style')).toBeUndefined()
    expect(wrapper.get('[role="status"]').isVisible()).toBe(true)
    vi.unstubAllGlobals()
  })
})

import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'
import IdeaDetailError from '../../app/components/kollio/IdeaDetailError.vue'
import IdeaDetailSkeleton from '../../app/components/kollio/IdeaDetailSkeleton.vue'
import EmptyState from '../../app/components/kollio/EmptyState.vue'
import Disclosure from '../../app/components/kollio/Disclosure.vue'

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
        reassurance: 'Your work is still safe.',
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
    expect(wrapper.get('img').attributes('src')).toBe('/images/states/idea-load-error.png')
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

  it('renders an optional decorative illustration and action', async () => {
    const wrapper = mount(EmptyState, {
      props: {
        description: 'No collaborators yet.',
        imageSrc: '/images/empty-states/team.png',
        actionLabel: 'Invite a collaborator',
      },
    })

    expect(wrapper.get('img').attributes()).toMatchObject({
      alt: '',
      src: '/images/empty-states/team.png',
    })
    await wrapper.get('button').trigger('click')
    expect(wrapper.emitted('action')).toHaveLength(1)
  })

  it('exposes and toggles the full description', async () => {
    const wrapper = mount(Disclosure, {
      props: {
        modelValue: false,
        contentId: 'description-content',
        expandLabel: 'Read the full description',
        collapseLabel: 'Collapse the description',
        'onUpdate:modelValue': (expanded: boolean) => wrapper.setProps({ modelValue: expanded }),
      },
      slots: { default: '<p>Full description</p>' },
    })

    const toggle = wrapper.get('button')
    expect(toggle.attributes('aria-expanded')).toBe('false')
    expect(toggle.attributes('aria-controls')).toBe('description-content')
    await toggle.trigger('click')
    expect(toggle.attributes('aria-expanded')).toBe('true')
    expect(toggle.text()).toContain('Collapse the description')
  })
})

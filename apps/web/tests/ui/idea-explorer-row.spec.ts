import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import IdeaExplorerRow from '../../app/components/kollio/IdeaExplorerRow.vue'

describe('Idea explorer row', () => {
  it('keeps the idea narrative visible and links directly to its detail page', () => {
    const wrapper = mount(IdeaExplorerRow, {
      props: {
        number: '07',
        to: '/workspace/ideas/idea-7',
        stageLabel: 'Iterating',
        dateLabel: '12 Sep 2026',
        idea: {
          id: 'idea-7',
          workspace_id: 'workspace-1',
          title: 'A calm idea index',
          pitch: 'A short narrative helps members decide whether an idea deserves attention.',
          stage: 'iterating',
          lang: 'en',
          domain: 'Product design',
          created_at: '2026-09-12T10:00:00Z',
        },
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

    expect(wrapper.get('a').attributes('href')).toBe('/workspace/ideas/idea-7')
    expect(wrapper.get('.explorer-row-number').text()).toBe('07')
    expect(wrapper.get('.explorer-row-pitch').text()).toContain('short narrative')
    expect(wrapper.get('.explorer-row-meta').text()).toContain('Iterating')
  })
})

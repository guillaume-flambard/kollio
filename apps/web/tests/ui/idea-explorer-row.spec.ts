import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import IdeaExplorerRow from '../../app/components/kollio/IdeaExplorerRow.vue'

describe('Idea explorer row', () => {
  it('keeps the narrative and collaboration signal visible while selecting the preview', async () => {
    const wrapper = mount(IdeaExplorerRow, {
      props: {
        selected: true,
        stageLabel: 'Iterating',
        dateLabel: '2 hours ago',
        contributorLabel: '1 contributor',
        avatarLabel: 'Contributors',
        expertiseLabel: 'Design and research',
        domainLabel: 'Product design',
        idea: {
          id: 'idea-7',
          title: 'A calm idea explorer',
          slug: 'a-calm-idea-explorer',
          pitch: 'A short narrative helps members decide whether an idea deserves attention.',
          stage: 'iterating',
          lang: 'en',
          domain: 'Product design',
          created_at: '2026-09-12T10:00:00Z',
          collaborators: [{
            id: 'person-1',
            display_name: 'Amelia Martin',
            handle: 'amelia',
            role: 'contributor',
            roles: ['design'],
            avatar_key: 'rose',
          }],
        },
      },
      global: {
        stubs: {
          KollioAvatarStack: { template: '<span class="avatar-stub" />' },
        },
      },
    })

    expect(wrapper.get('button').attributes('aria-pressed')).toBe('true')
    expect(wrapper.get('.explorer-row-pitch').text()).toContain('short narrative')
    expect(wrapper.get('.explorer-row-activity').text()).toContain('1 contributor')
    await wrapper.get('button').trigger('click')
    expect(wrapper.emitted('select')).toHaveLength(1)
  })
})

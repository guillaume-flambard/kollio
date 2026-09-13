import { mount } from '@vue/test-utils'
import { mockNuxtImport } from '@nuxt/test-utils/runtime'
import { describe, expect, it } from 'vitest'
import LandingInitiativeFlow from '../../app/components/kollio/LandingInitiativeFlow.vue'
import PrimaryAction from '../../app/components/kollio/PrimaryAction.vue'
import RelationshipConnector from '../../app/components/kollio/RelationshipConnector.vue'

mockNuxtImport('useI18n', () => () => ({
  t: (key: string) => key,
}))

describe('Landing initiative flow', () => {
  it('keeps the B2B decision journey understandable without decorative connectors', () => {
    const wrapper = mount(LandingInitiativeFlow)
    const stages = wrapper.findAll('.initiative-stage h2')

    expect(stages.map(stage => stage.text())).toEqual([
      'landing.preview.signal.title',
      'landing.preview.validation.title',
      'landing.preview.decision.title',
    ])
    expect(wrapper.text()).toContain('landing.preview.validation.evidence')
    expect(wrapper.text()).toContain('landing.preview.validation.question')
    expect(wrapper.text()).toContain('landing.preview.decision.documented')
    const connectors = wrapper.findAllComponents(RelationshipConnector)
    expect(connectors).toHaveLength(5)
    expect(connectors[0]?.props()).toMatchObject({
      path: 'M357 106 C430 106 444 123 539 123',
      startX: 357,
      startY: 106,
      endX: 539,
      endY: 123,
    })
    expect(connectors[4]?.props()).toMatchObject({
      path: 'M900 244 C970 244 957 139 1023 139',
      muted: true,
      showEnd: false,
    })
  })

  it('uses a document navigation for the server-owned authentication route', () => {
    const wrapper = mount(PrimaryAction, {
      props: { label: 'Request a demo', href: '/sign-in' },
    })

    expect(wrapper.get('a').attributes('href')).toBe('/sign-in')
    expect(wrapper.findComponent({ name: 'NuxtLink' }).exists()).toBe(false)
  })
})

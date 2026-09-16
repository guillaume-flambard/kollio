import { expect, test } from '@playwright/test'
import type { IdeaPageResponse, IdeaResponse } from '@kollio/api-client'
import { appendFileSync, mkdirSync } from 'node:fs'

const EVIDENCE = '.agents/skills/ux-flow-auditor/evidence/a11y-raw.json'

function log(entry: unknown) {
  mkdirSync('.agents/skills/ux-flow-auditor/evidence', { recursive: true })
  appendFileSync(EVIDENCE, `${JSON.stringify(entry)}\n`)
}

const workspaces = [{ id: 'workspace-one', name: 'Team', role: 'member' }]

function summary(id: string, title: string, overrides = {}) {
  return {
    id, slug: id, title, pitch: 'Une flotte cooperative pour les trajets quotidiens.',
    stage: 'seed', lang: 'fr', created_at: '2026-09-01T10:00:00Z',
    sought_roles: ['engineering'], realism_score: 72, last_activity_at: null,
    collaborators: [{ id: 'member-two', display_name: 'Camille Dupont', participation: 'contributor', business_function: 'engineering', roles: ['engineering'], bio: null, avatar_key: 'sage' }],
    ...overrides,
  }
}

const ideaDetail: IdeaResponse = {
  id: 'idea-one', slug: 'une-idee', title: 'Une idee a explorer',
  pitch: 'Un contenu original conserve dans les deux langues. Deuxieme phrase du detail.',
  stage: 'seed', lang: 'fr', created_at: '2026-09-01T10:00:00Z',
  owner_id: 'owner-one', workspace_id: 'workspace-one', visibility: 'workspace',
  collaborators: [{ id: 'member-two', display_name: 'Camille Dupont', participation: 'contributor', business_function: 'engineering', roles: ['engineering'], bio: null, avatar_key: 'sage' }],
  sought_roles: ['engineering'], join_requests: [],
}

function emptyContext() {
  return {
    profile: { name: null, description: null, business_model: null, products_services: null, customer_segments: null, markets: null, structure: null },
    objectives: [], constraints: [], principles: [], metrics: [],
  }
}

async function mockAll(page: import('@playwright/test').Page) {
  await page.route(/\/api\/session$/, route => route.fulfill({ json: { signedIn: true, subject: 'member-two' } }))
  await page.route(/\/api\/workspaces$/, route => route.fulfill({ json: workspaces }))
  await page.route(/\/api\/workspaces\/workspace-one\/ideas\??.*$/, route => route.fulfill({
    json: { items: [summary('idea-one', 'Ancree'), summary('idea-two', 'En attente', { realism_score: null })], total: 2, limit: 5, offset: 0 } satisfies IdeaPageResponse,
  }))
  await page.route(/\/api\/ideas\/idea-one$/, route => route.fulfill({ json: ideaDetail }))
  await page.route(/\/api\/users\/owner-one$/, route => route.fulfill({ json: { id: 'owner-one', display_name: 'Proprietaire', handle: 'owner', roles: [], bio: null, avatar_key: null, owned_ideas: [], memberships: [], contributions: [] } }))
  await page.route(/\/api\/ideas\/idea-one\/iterations$/, route => route.fulfill({ json: [] }))
  await page.route(/\/api\/ideas\/idea-one\/experiments$/, route => route.fulfill({ json: [] }))
  await page.route(/\/api\/workspaces\/workspace-one\/members$/, route => route.fulfill({ json: [] }))
  await page.route(/\/api\/workspaces\/workspace-one\/company-context.*$/, route => route.fulfill({ json: emptyContext() }))
}

// Contrast helpers run in the browser: composite translucent layers over white.
const CONTRAST_FN = `() => {
  function parse(s) {
    const m = s.match(/rgba?\\(\\s*([\\d.]+)[,\\s]+([\\d.]+)[,\\s]+([\\d.]+)(?:[,\\/\\s]+([\\d.]+))?\\s*\\)/);
    if (!m) return null;
    return [Number(m[1]), Number(m[2]), Number(m[3]), m[4] === undefined ? 1 : Number(m[4])];
  }
  function over(fg, bg) {
    const a = fg[3] + bg[3] * (1 - fg[3]);
    if (a === 0) return [0, 0, 0, 0];
    return [
      (fg[0] * fg[3] + bg[0] * bg[3] * (1 - fg[3])) / a,
      (fg[1] * fg[3] + bg[1] * bg[3] * (1 - fg[3])) / a,
      (fg[2] * fg[3] + bg[2] * bg[3] * (1 - fg[3])) / a, a,
    ];
  }
  function lum(c) {
    const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
    return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2]);
  }
  return function measure(selector) {
    const el = document.querySelector(selector);
    if (!el) return { selector, missing: true };
    const cs = getComputedStyle(el);
    const fg = parse(cs.color);
    const chain = [];
    let n = el;
    while (n && n instanceof Element) { chain.unshift(n); n = n.parentElement; }
    let bg = [255, 255, 255, 1];
    for (const node of chain) {
      const b = parse(getComputedStyle(node).backgroundColor);
      if (b) bg = over(b, bg);
    }
    if (!fg) return { selector, fg: cs.color, unparsed: true };
    const l1 = lum([fg[0], fg[1], fg[2]]);
    const l2 = lum([bg[0], bg[1], bg[2]]);
    const ratio = (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
    return { selector, fg: cs.color, bg: 'rgb(' + Math.round(bg[0]) + ', ' + Math.round(bg[1]) + ', ' + Math.round(bg[2]) + ')', ratio: Math.round(ratio * 100) / 100, fontSize: cs.fontSize, fontWeight: cs.fontWeight };
  };
}`;

async function measure(page: import('@playwright/test').Page, selectors: string[]) {
  return page.evaluate(
    `(${CONTRAST_FN})()(selectors)`.replace('selectors', JSON.stringify(selectors)) as never,
  ) as unknown as Array<Record<string, unknown>>
}

test.describe('A11Y-TMP landing', () => {
  for (const locale of ['fr', 'en'] as const) {
    test(`landmarks, names and contrast (${locale})`, async ({ page }) => {
      await mockAll(page)
      const prefix = locale === 'fr' ? '' : '/en'
      await page.goto(`${prefix}/`)
      await expect(page.getByRole('heading', { level: 1 })).toBeVisible()
      const data = await page.evaluate(() => {
        const labelled = (el: Element | null) => {
          if (!el) return null
          if (el.getAttribute('aria-label')) return el.getAttribute('aria-label')
          if (el.getAttribute('aria-labelledby')) {
            return el.getAttribute('aria-labelledby')!.split(' ').map(id => document.getElementById(id)?.textContent?.trim()).join(' ')
          }
          return (el as HTMLElement).innerText?.trim().slice(0, 80) ?? null
        }
        return {
          h1: document.querySelectorAll('h1').length,
          mains: document.querySelectorAll('main').length,
          sectionsNoName: [...document.querySelectorAll('section')].filter(s => !s.getAttribute('aria-label') && !s.getAttribute('aria-labelledby') && !s.querySelector('h1,h2,h3')).length,
          navs: [...document.querySelectorAll('nav')].map(n => labelled(n)),
          emptyButtons: [...document.querySelectorAll('button')].filter(b => !(b as HTMLElement).innerText?.trim() && !b.getAttribute('aria-label') && !b.getAttribute('aria-labelledby')).length,
          emptyLinks: [...document.querySelectorAll('a')].filter(a => !(a as HTMLElement).innerText?.trim() && !a.getAttribute('aria-label') && !a.getAttribute('aria-labelledby')).length,
          imagesNoAlt: [...document.querySelectorAll('img')].filter(i => i.getAttribute('alt') === null).length,
          htmlLang: document.documentElement.getAttribute('lang'),
        }
      })
      const contrast = await measure(page, [
        '.landing-hero h1', '.landing-hero__description', '.landing-hero__eyebrow',
        '.landing-nav__language', '.landing-outcomes p', '.landing-final-cta h2',
        '.landing-final-cta > p', '.landing-secondary-action',
      ])
      log({ test: `landing-${locale}`, ...data, contrast })
      expect(data.h1).toBe(1)
    })
  }
})

test.describe('A11Y-TMP explorer', () => {
  for (const locale of ['fr', 'en'] as const) {
    test(`search label, rail and contrast (${locale})`, async ({ page }) => {
      await mockAll(page)
      const prefix = locale === 'fr' ? '' : '/en'
      const listResponse = page.waitForResponse(r => r.url().includes('/api/workspaces/workspace-one/ideas'))
      await page.goto(`${prefix}/workspace`)
      await listResponse
      const data = await page.evaluate(() => {
        const search = document.querySelector('.ideas-search input') as HTMLInputElement | null
        const labelledBy = search?.getAttribute('aria-labelledby') ?? search?.getAttribute('aria-label')
        const wrappingLabel = search?.closest('label')?.innerText?.trim() ?? null
        const accName = labelledBy ?? wrappingLabel ?? null
        return {
          searchType: search?.type ?? null,
          searchPlaceholderOnly: Boolean(search?.placeholder) && !labelledBy && !(wrappingLabel && wrappingLabel !== search.placeholder),
          searchAccName: accName,
          searchPlaceholder: search?.placeholder ?? null,
          createActionTag: document.querySelector('.ideas-create-action')?.tagName ?? null,
          createActionTypeAttr: document.querySelector('.ideas-create-action')?.getAttribute('type'),
          railPressed: [...document.querySelectorAll('.ideas-filter-rail button')].map(b => b.getAttribute('aria-pressed')),
          railButtons: [...document.querySelectorAll('.ideas-filter-rail button')].map(b => (b as HTMLElement).innerText?.trim().slice(0, 40)),
          navDisabled: [...document.querySelectorAll('.workspace-nav button[disabled]')].map(b => ({ ariaDisabled: b.getAttribute('aria-disabled'), text: (b as HTMLElement).innerText?.trim().slice(0, 30) })),
          rowRole: document.querySelector('.explorer-row')?.tagName ?? null,
          nestedLinksInRow: document.querySelector('.explorer-row')?.querySelectorAll('a').length ?? -1,
          paginationLabel: document.querySelector('.ideas-results-pagination')?.getAttribute('aria-label') ?? null,
          previewAsideLabel: document.querySelector('.idea-preview')?.getAttribute('aria-label') ?? null,
          headingsInPreview: [...document.querySelectorAll('.idea-preview h2, .idea-preview h3')].map(h => h.tagName),
          mainCount: document.querySelectorAll('main').length,
          h1: [...document.querySelectorAll('h1')].map(h => (h as HTMLElement).innerText?.trim().slice(0, 40)),
          duplicateButtonNames: (() => {
            const names = [...document.querySelectorAll('.ideas-filter-rail button')].map(b => (b as HTMLElement).innerText?.trim())
            return names.filter((n, i) => names.indexOf(n) !== i)
          })(),
        }
      })
      const contrast = await measure(page, [
        '.ideas-explorer-header p', '.explorer-row-pitch', '.explorer-row-topics',
        '.explorer-row-realism', '.ideas-filter-rail button', '.ideas-create-action',
        '.ideas-results-pagination a', '.ideas-results-header',
        '.idea-preview-content > p', '.idea-preview-roles small',
      ])
      const boxes = await page.evaluate(() => {
        const out: Record<string, unknown> = {}
        for (const [key, sel] of [
          ['paginationLink', '.ideas-results-pagination a'],
          ['railButton', '.ideas-filter-rail button'],
          ['createAction', '.ideas-create-action'],
          ['previewClose', '.idea-preview-close'],
          ['searchInput', '.ideas-search'],
        ] as const) {
          const el = document.querySelector(sel) as HTMLElement | null
          if (!el) { out[key] = null; continue }
          const r = el.getBoundingClientRect()
          const cs = getComputedStyle(el)
          out[key] = { w: Math.round(r.width), h: Math.round(r.height), visible: cs.display !== 'none' && cs.visibility !== 'hidden' && r.width > 0 }
        }
        return out
      })
      // Keyboard: tab to search, check focus visibility
      await page.keyboard.press('Tab')
      const focus1 = await page.evaluate(() => {
        const el = document.activeElement as HTMLElement | null
        if (!el) return null
        const cs = getComputedStyle(el)
        return { tag: el.tagName, text: (el.innerText ?? el.getAttribute('aria-label') ?? '').slice(0, 60), focusVisible: el.matches(':focus-visible'), outline: cs.outlineWidth, outlineColor: cs.outlineColor }
      })
      log({ test: `explorer-${locale}`, ...data, contrast, boxes, focus1 })
      expect(data.mainCount).toBeGreaterThanOrEqual(1)
    })
  }

  test('mobile drawer focus trap and escape', async ({ page }) => {
    await mockAll(page)
    await page.setViewportSize({ width: 390, height: 844 })
    const listResponse = page.waitForResponse(r => r.url().includes('/api/workspaces/workspace-one/ideas'))
    await page.goto('/workspace')
    await listResponse
    const toggle = page.getByRole('button', { name: /menu|ouvrir/i }).first()
    await toggle.click()
    const drawer = page.locator('#workspace-mobile-nav')
    await expect(drawer).toBeVisible()
    const trap = await page.evaluate(() => {
      const drawerEl = document.getElementById('workspace-mobile-nav')
      return {
        role: drawerEl?.getAttribute('role'),
        ariaModal: drawerEl?.getAttribute('aria-modal'),
        ariaLabel: drawerEl?.getAttribute('aria-label'),
        toggleExpanded: document.querySelector('[aria-controls="workspace-mobile-nav"]')?.getAttribute('aria-expanded'),
        focusedInDrawer: drawerEl?.contains(document.activeElement),
      }
    })
    await page.keyboard.press('Escape')
    const afterEscape = await page.evaluate(() => ({
      drawerPresent: Boolean(document.getElementById('workspace-mobile-nav')),
      focusOnToggle: document.activeElement?.getAttribute('aria-controls') === 'workspace-mobile-nav',
    }))
    log({ test: 'drawer-mobile', trap, afterEscape })
    expect(trap.role).toBe('dialog')
  })
})

test.describe('A11Y-TMP deposit', () => {
  test('form labels, live regions and contrast (fr)', async ({ page }) => {
    await mockAll(page)
    await page.goto('/workspace/deposit')
    await expect(page.getByRole('heading', { level: 1 })).toBeVisible()
    const data = await page.evaluate(() => ({
      inputsWithoutLabel: [...document.querySelectorAll('.deposit-form input, .deposit-form textarea, .deposit-form select')].map(el => ({
        name: el.getAttribute('name'),
        labelled: Boolean(el.getAttribute('aria-label') || el.getAttribute('aria-labelledby') || el.closest('label')?.innerText?.trim()),
      })),
      submitDisabledInitially: (document.querySelector('.deposit-submit') as HTMLButtonElement)?.disabled,
      requiredAttrs: [...document.querySelectorAll('.deposit-form [required]')].map(el => el.getAttribute('name')),
    }))
    // Fill and submit to reach the resolved verdict; poll the mocked idea endpoint.
    await page.route(/\/api\/workspaces\/workspace-one\/ideas$/, route => route.fulfill({ status: 201, json: { ...ideaDetail, id: 'idea-deposit-1', analysis: undefined } }), { times: 1 } as never)
    await page.route(/\/api\/ideas\/idea-deposit-1$/, route => route.fulfill({
      json: { ...ideaDetail, id: 'idea-deposit-1', analysis: { state: 'resolved', realism_score: 62, constraints: {}, contradictions: [] } },
    }))
    await page.getByLabel(/titre|title/i).first().fill('Velos en libre-service')
    await page.getByLabel(/pitch|resume/i).first().fill('Une flotte cooperative.')
    await page.getByRole('button', { name: /d|soumettre|poser/i }).first().click()
    await expect(page.getByText('62', { exact: true })).toBeVisible({ timeout: 15000 }).catch(() => null)
    const verdict = await page.evaluate(() => {
      const score = document.querySelector('.deposit-score')
      const section = document.querySelector('.deposit-verdict')
      return {
        scoreText: score?.textContent?.trim() ?? null,
        scoreLabelled: Boolean(score?.getAttribute('aria-label') || score?.closest('[aria-label]')),
        liveRegion: section?.getAttribute('aria-live') ?? null,
        verdictHeading: [...document.querySelectorAll('.deposit-verdict h2')].map(h => (h as HTMLElement).innerText?.trim().slice(0, 60)),
        errorAlert: document.querySelector('.deposit-error')?.getAttribute('role') ?? null,
      }
    }).catch(() => ({ skipped: true }))
    const contrast = await measure(page, [
      '.deposit-header p', '.deposit-field', '.deposit-submit', '.deposit-score', '.deposit-basis',
    ])
    log({ test: 'deposit-fr', ...data, verdict, contrast })
    expect(data.submitDisabledInitially).toBe(true)
  })
})

test.describe('A11Y-TMP idea detail', () => {
  test('controls, tabs keyboard and contrast (fr)', async ({ page }) => {
    await mockAll(page)
    const iterResponse = page.waitForResponse(r => /\/api\/ideas\/idea-one\/iterations$/.test(r.url()))
    await page.goto('/workspace/ideas/idea-one')
    await iterResponse
    await expect(page.getByRole('heading', { level: 1 })).toBeVisible()
    const data = await page.evaluate(() => ({
      moreActions: (() => {
        const btns = [...document.querySelectorAll('button')].filter(b => (b.getAttribute('aria-label') ?? '').length > 0 && !(b as HTMLElement).innerText?.trim())
        return btns.map(b => ({ label: b.getAttribute('aria-label'), cls: b.className.toString().slice(0, 60) }))
      })(),
      tablistLabel: document.querySelector('[role="tablist"]')?.getAttribute('aria-label') ?? null,
      tabs: [...document.querySelectorAll('[role="tab"]')].map(t => ({
        selected: t.getAttribute('aria-selected'), tabIndex: t.getAttribute('tabindex'),
        controls: t.getAttribute('aria-controls'), labelled: (t as HTMLElement).innerText?.trim().slice(0, 40),
      })),
      tabpanelLabelledBy: document.querySelector('[role="tabpanel"]')?.getAttribute('aria-labelledby') ?? null,
      rejectInputs: [...document.querySelectorAll('input[placeholder]')].map(i => ({
        placeholder: i.getAttribute('placeholder')?.slice(0, 40),
        labelled: Boolean(i.getAttribute('aria-label') || i.getAttribute('aria-labelledby') || i.closest('label') || (i as HTMLInputElement).id && document.querySelector(`label[for="${(i as HTMLInputElement).id}"]`)),
      })),
      experimentRows: [...document.querySelectorAll('.experiment-row')].map(r => ({ expanded: r.getAttribute('aria-expanded'), controls: r.getAttribute('aria-controls') })),
      onlineDots: document.querySelectorAll('.person-row-online').length,
      skeletonsLive: document.querySelector('.idea-detail-skeleton')?.getAttribute('aria-live') ?? null,
      teamListRole: document.querySelector('.idea-team ul')?.getAttribute('role') ?? null,
      avatarImgAlts: [...document.querySelectorAll('.person-row-avatar img')].map(i => i.getAttribute('alt')),
      breadcrumbNav: document.querySelector('.idea-breadcrumb')?.tagName ?? null,
    }))
    // Keyboard through tabs with arrow keys
    const firstTab = page.getByRole('tab').first()
    await firstTab.focus()
    await page.keyboard.press('ArrowRight')
    const tabFocus = await page.evaluate(() => ({
      active: (document.activeElement as HTMLElement)?.innerText?.trim().slice(0, 40) ?? null,
      role: document.activeElement?.getAttribute('role') ?? null,
    }))
    const contrast = await measure(page, [
      '.idea-summary', '.idea-stats', '.iteration-entry-meta', '.iteration-analysis',
      '.idea-topic-add', '.team-request', '.experiment-status',
    ])
    log({ test: 'idea-detail-fr', ...data, tabFocus, contrast })
    expect(data.tablistLabel).toBeTruthy()
  })
})

test.describe('A11Y-TMP settings', () => {
  test('wizard labels, toggle and contrast (fr)', async ({ page }) => {
    await mockAll(page)
    const ctxResponse = page.waitForResponse(r => r.url().includes('/company-context'))
    await page.goto('/workspace/settings')
    await ctxResponse
    await expect(page.getByRole('heading', { level: 1 })).toBeVisible()
    const data = await page.evaluate(() => ({
      inputsWithoutLabel: [...document.querySelectorAll('.settings-shell input, .settings-shell textarea, .settings-shell select')].map(el => ({
        type: el.tagName,
        labelled: Boolean(el.getAttribute('aria-label') || el.getAttribute('aria-labelledby') || el.closest('label')?.innerText?.trim() || ((el as HTMLInputElement).id && document.querySelector(`label[for="${(el as HTMLInputElement).id}"]`))),
        placeholder: el.getAttribute('placeholder')?.slice(0, 40) ?? null,
      })),
      toggleExpanded: document.querySelector('.settings-advanced-toggle')?.getAttribute('aria-expanded'),
      toggleControls: document.querySelector('.settings-advanced-toggle')?.getAttribute('aria-controls'),
      savedNoteLive: (() => {
        const n = document.querySelector('.settings-note')
        return n ? { text: n.textContent?.trim().slice(0, 40), live: n.closest('[aria-live]')?.getAttribute('aria-live') ?? null } : null
      })(),
      errorRoles: [...document.querySelectorAll('.settings-error')].map(e => e.getAttribute('role')),
      fieldsets: document.querySelectorAll('.settings-step').length,
    }))
    const contrast = await measure(page, [
      '.settings-header p', '.settings-note', '.settings-pending', '.settings-state', '.settings-primary',
    ])
    log({ test: 'settings-fr', ...data, contrast })
    expect(data.fieldsets).toBeGreaterThan(0)
  })
})

test.describe('A11Y-TMP touch targets', () => {
  const screens: Array<[string, string, string | null]> = [
    ['deposit', '/workspace/deposit', null],
    ['settings', '/workspace/settings', '/company-context'],
  ]

  for (const [name, path, waitFor] of screens) {
    test(`${name} meets the 44px control floor (fr)`, async ({ page }) => {
      await mockAll(page)
      const pending = waitFor ? page.waitForResponse(r => r.url().includes(waitFor)) : null
      await page.goto(path)
      if (pending) await pending
      await expect(page.getByRole('heading', { level: 1 })).toBeVisible()
      const under = await page.evaluate(() =>
        [...document.querySelectorAll('a[href], button:not([disabled]), input:not([type="hidden"]), select, textarea')]
          .map(el => {
            const r = el.getBoundingClientRect()
            return { tag: el.tagName.toLowerCase(), cls: String(el.className).slice(0, 48), h: Math.round(r.height), w: Math.round(r.width), html: el.outerHTML.slice(0, 140) }
          })
          .filter(t => t.w > 0 && t.h > 0 && t.h < 44),
      )
      log({ test: `touch-${name}`, under })
      expect(under, `${name}: ${under.length} control(s) below the 44px floor`).toEqual([])
    })
  }
})

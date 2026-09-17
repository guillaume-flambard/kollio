import { expect, test } from '@playwright/test'

import type {
  ClusterResponse,
  DecisionSpaceDetailResponse,
  MapContributionResponse,
  MapResponse,
  RelationResponse,
  WorkspaceMemberResponse,
  WorkspaceResponse,
} from '@kollio/api-client'

import fr from '../../i18n/locales/fr.json' with { type: 'json' }
import en from '../../i18n/locales/en.json' with { type: 'json' }

const workspaces: WorkspaceResponse[] = [{ id: 'workspace-one', name: 'Team', role: 'member' }]

const members: WorkspaceMemberResponse[] = [
  { id: 'owner-one', display_name: 'Camille', role: 'member' },
  { id: 'participant-one', display_name: 'Sam', role: 'member' },
]

function makeDetail(): DecisionSpaceDetailResponse {
  return {
    id: 'space-one',
    workspace_id: 'workspace-one',
    question: 'Which pricing should we pick?',
    description: null,
    owner_id: 'owner-one',
    status: 'CONVERGING',
    deadline: '2026-10-01',
    lang: 'en',
    created_at: '2026-09-17T09:00:00Z',
    updated_at: '2026-09-17T09:00:00Z',
    participants: [
      { user_id: 'owner-one', created_at: '2026-09-17T09:00:00Z' },
      { user_id: 'participant-one', created_at: '2026-09-17T09:00:00Z' },
    ],
    history: [],
  }
}

function makeContribution(
  overrides: Partial<MapContributionResponse> = {},
): MapContributionResponse {
  return {
    id: 'contribution-one',
    branch_id: 'branch-one',
    kind: 'claim',
    title: 'Churn does not follow price',
    status: 'confirmed',
    author_id: 'owner-one',
    cluster_id: null,
    ...overrides,
  }
}

function makeCluster(overrides: Partial<ClusterResponse> = {}): ClusterResponse {
  return {
    id: 'cluster-one',
    space_id: 'space-one',
    title: 'Pricing evidence',
    created_by: 'owner-one',
    created_at: '2026-09-17T09:00:00Z',
    member_ids: [],
    ...overrides,
  }
}

function makeRelation(overrides: Partial<RelationResponse> = {}): RelationResponse {
  return {
    id: 'relation-one',
    space_id: 'space-one',
    from_contribution_id: 'contribution-one',
    to_contribution_id: 'contribution-two',
    relation_type: 'CONTRADICTS',
    created_by: 'owner-one',
    created_at: '2026-09-17T09:00:00Z',
    ...overrides,
  }
}

const mapPath = '**/api/workspaces/workspace-one/decision-spaces/space-one/converge/map'
const relationsPath = '**/api/workspaces/workspace-one/decision-spaces/space-one/relations'
const relationPath = '**/api/workspaces/workspace-one/decision-spaces/space-one/relations/*'
const clustersPath = '**/api/workspaces/workspace-one/decision-spaces/space-one/clusters'
const clusterPath = '**/api/workspaces/workspace-one/decision-spaces/space-one/clusters/*'
const clusterMemberPath =
  '**/api/workspaces/workspace-one/decision-spaces/space-one/clusters/*/members'
const clusterMemberOnePath =
  '**/api/workspaces/workspace-one/decision-spaces/space-one/clusters/*/members/*'

for (const [locale, messages] of [
  ['fr', fr],
  ['en', en],
] as const) {
  test.describe(locale, () => {
    const prefix = locale === 'fr' ? '' : '/en'
    const converge = messages.decisionSpaces.converge
    const section = messages.decisionSpaces.section.converge

    let states: MapResponse

    test.beforeEach(async ({ page }) => {
      states = {
        contributions: [makeContribution()],
        relations: [],
        clusters: [],
      }

      await page.route('**/api/session', route =>
        route.fulfill({ json: { signedIn: true, subject: 'member-two' } }),
      )
      await page.route('**/api/workspaces', route => route.fulfill({ json: workspaces }))
      await page.route('**/api/workspaces/workspace-one/members', route =>
        route.fulfill({ json: members }),
      )
      await page.route('**/api/workspaces/workspace-one/decision-spaces/*', route =>
        route.fulfill({ json: makeDetail() }),
      )
      await page.route(mapPath, route => route.fulfill({ json: states }))

      await page.route(relationsPath, async (route) => {
        const body = route.request().postDataJSON() as {
          from_contribution_id: string
          to_contribution_id: string
          relation_type: RelationResponse['relation_type']
        }
        states.relations.push(
          makeRelation({
            id: 'relation-new',
            from_contribution_id: body.from_contribution_id,
            to_contribution_id: body.to_contribution_id,
            relation_type: body.relation_type,
          }),
        )
        await route.fulfill({ status: 201, json: states.relations.at(-1) })
      })
      await page.route(relationPath, async (route) => {
        if (route.request().method() !== 'DELETE') return route.fallback()
        states.relations = []
        await route.fulfill({ status: 204, body: '' })
      })
      await page.route(clustersPath, async (route) => {
        const body = route.request().postDataJSON() as { title: string }
        states.clusters.push(makeCluster({ id: 'cluster-new', title: body.title }))
        await route.fulfill({ status: 201, json: states.clusters.at(-1) })
      })
      await page.route(clusterPath, async (route) => {
        if (route.request().method() !== 'DELETE') return route.fallback()
        states.clusters = []
        states.contributions = states.contributions.map(entry => ({
          ...entry,
          cluster_id: null,
        }))
        await route.fulfill({ status: 204, body: '' })
      })
      await page.route(clusterMemberPath, async (route) => {
        const body = route.request().postDataJSON() as { contribution_id: string }
        const [, clusterId] = route.request().url().match(/clusters\/([^/]+)\/members/) ?? []
        states.clusters = states.clusters.map(cluster =>
          cluster.id === clusterId
            ? { ...cluster, member_ids: [...(cluster.member_ids ?? []), body.contribution_id] }
            : cluster,
        )
        states.contributions = states.contributions.map(entry =>
          entry.id === body.contribution_id ? { ...entry, cluster_id: clusterId } : entry,
        )
        await route.fulfill({ json: states.clusters.find(cluster => cluster.id === clusterId) })
      })
      await page.route(clusterMemberOnePath, async (route) => {
        if (route.request().method() !== 'DELETE') return route.fallback()
        const [, clusterId, contributionId] =
          route.request().url().match(/clusters\/([^/]+)\/members\/([^/]+)$/) ?? []
        states.clusters = states.clusters.map(cluster =>
          cluster.id === clusterId
            ? {
                ...cluster,
                member_ids: (cluster.member_ids ?? []).filter(id => id !== contributionId),
              }
            : cluster,
        )
        states.contributions = states.contributions.map(entry =>
          entry.id === contributionId ? { ...entry, cluster_id: null } : entry,
        )
        await route.fulfill({ json: states.clusters.find(cluster => cluster.id === clusterId) })
      })
    })

    async function openConverge(page: import('@playwright/test').Page) {
      await page.goto(`${prefix}/workspace/decision-spaces/space-one/converge`)
      await expect(page.getByRole('heading', { name: section.title })).toBeVisible()
    }

    test('CONVERGE-01 says the Space has no shared reasoning yet', async ({ page }) => {
      states = { contributions: [], relations: [], clusters: [] }

      await openConverge(page)

      await expect(page.getByText(converge.empty.title)).toBeVisible()
      await expect(page.getByText(converge.empty.body)).toBeVisible()
      await expect(page.getByRole('link', { name: converge.empty.action })).toBeVisible()
    })

    test('CONVERGE-02 reads the map with the kinds and the groups', async ({ page }) => {
      states = {
        contributions: [
          makeContribution(),
          makeContribution({
            id: 'contribution-two',
            kind: 'evidence',
            title: 'Two years of invoices say so',
            cluster_id: 'cluster-one',
          }),
        ],
        relations: [],
        clusters: [makeCluster({ member_ids: ['contribution-two'] })],
      }

      await openConverge(page)

      const listed = page.locator('.contribution-list .contribution')
      await expect(listed).toHaveCount(2)
      await expect(listed.first()).toContainText('Churn does not follow price')
      await expect(listed.first()).toContainText(converge.kinds.claim)
      await expect(listed.nth(1)).toContainText(converge.kinds.evidence)
      await expect(listed.nth(1)).toContainText('Pricing evidence')
    })

    test('CONVERGE-03 says a Contribution is not grouped', async ({ page }) => {
      await openConverge(page)

      await expect(page.locator('.contribution-list .contribution').first()).toContainText(
        converge.map.ungrouped,
      )
    })

    test('CONVERGE-04 asserts a Relation between two Contributions', async ({ page }) => {
      const posted: string[] = []
      page.on('request', (request) => {
        if (request.method() === 'POST') posted.push(request.url())
      })
      states.contributions = [
        makeContribution(),
        makeContribution({ id: 'contribution-two', title: 'Two years of invoices say so' }),
      ]

      await openConverge(page)
      await page.getByRole('button', { name: converge.relations.create, exact: true }).click()
      const relationFields = page.locator('.converge-form select')
      await relationFields.nth(0).selectOption('contribution-one')
      await relationFields.nth(1).selectOption('contribution-two')
      await relationFields.nth(2).selectOption('EVIDENCE_AGAINST')
      await page
        .getByRole('button', { name: converge.relations.form.submit, exact: true })
        .click()

      await expect(page.locator('.relation-list .relation')).toHaveCount(1)
      await expect(page.locator('.relation-list .relation').first()).toContainText(
        converge.relations.types.EVIDENCE_AGAINST,
      )
      expect(posted.filter(url => url.includes('/relations'))).toHaveLength(1)
    })

    test('CONVERGE-05 refuses a Relation that links a Contribution to itself', async ({ page }) => {
      const posted: string[] = []
      page.on('request', (request) => {
        if (request.method() === 'POST') posted.push(request.url())
      })
      states.contributions = [
        makeContribution(),
        makeContribution({ id: 'contribution-two', title: 'Two years of invoices say so' }),
      ]

      await openConverge(page)
      await page.getByRole('button', { name: converge.relations.create, exact: true }).click()
      const relationFields = page.locator('.converge-form select')
      await relationFields.nth(0).selectOption('contribution-one')
      await relationFields.nth(1).selectOption('contribution-one')
      await page
        .getByRole('button', { name: converge.relations.form.submit, exact: true })
        .click()

      await expect(page.getByText(converge.relations.form.sameEnds)).toBeVisible()
      expect(posted.filter(url => url.includes('/relations'))).toEqual([])
    })

    test('CONVERGE-06 removes a Relation', async ({ page }) => {
      states.relations = [makeRelation()]
      states.contributions = [
        makeContribution(),
        makeContribution({ id: 'contribution-two', title: 'Two years of invoices say so' }),
      ]

      await openConverge(page)
      await expect(page.locator('.relation-list .relation')).toHaveCount(1)
      await page
        .getByRole('button', { name: converge.relations.remove, exact: true })
        .click()

      await expect(page.locator('.relation-list .relation')).toHaveCount(0)
      await expect(page.getByText(converge.relations.empty)).toBeVisible()
    })

    test('CONVERGE-07 creates a Cluster', async ({ page }) => {
      const posted: string[] = []
      page.on('request', (request) => {
        if (request.method() === 'POST') posted.push(request.url())
      })

      await openConverge(page)
      await page.getByRole('button', { name: converge.clusters.create, exact: true }).click()
      await page.getByLabel(converge.clusters.form.name).fill('Pricing evidence')
      await page
        .getByRole('button', { name: converge.clusters.form.submit, exact: true })
        .click()

      await expect(page.locator('.cluster-list .cluster')).toHaveCount(1)
      await expect(page.locator('.cluster-list .cluster').first()).toContainText(
        'Pricing evidence',
      )
      expect(posted.filter(url => url.includes('/clusters'))).toHaveLength(1)
    })

    test('CONVERGE-08 refuses a Cluster without a title', async ({ page }) => {
      const posted: string[] = []
      page.on('request', (request) => {
        if (request.method() === 'POST') posted.push(request.url())
      })

      await openConverge(page)
      await page.getByRole('button', { name: converge.clusters.create, exact: true }).click()
      await page.getByLabel(converge.clusters.form.name).fill('   ')
      await page
        .getByRole('button', { name: converge.clusters.form.submit, exact: true })
        .click()

      await expect(page.getByText(converge.clusters.form.nameRequired)).toBeVisible()
      expect(posted.filter(url => url.includes('/clusters'))).toEqual([])
    })

    test('CONVERGE-09 adds a Contribution to a Cluster', async ({ page }) => {
      states.contributions = [
        makeContribution(),
        makeContribution({ id: 'contribution-two', title: 'Two years of invoices say so' }),
      ]
      states.clusters = [makeCluster()]

      await openConverge(page)
      await expect(page.getByText(converge.clusters.noMembers)).toBeVisible()
      await page.locator('.cluster-add select').selectOption('contribution-one')
      await page.getByRole('button', { name: converge.clusters.add, exact: true }).click()

      const listed = page.locator('.cluster-members li')
      await expect(listed).toHaveCount(1)
      await expect(listed.first()).toContainText('Churn does not follow price')
    })

    test('CONVERGE-10 removes a Contribution from a Cluster', async ({ page }) => {
      states.contributions = [
        makeContribution({ cluster_id: 'cluster-one' }),
        makeContribution({ id: 'contribution-two', title: 'Two years of invoices say so' }),
      ]
      states.clusters = [makeCluster({ member_ids: ['contribution-one'] })]

      await openConverge(page)
      await expect(page.locator('.cluster-members li')).toHaveCount(1)
      await page
        .getByRole('button', { name: converge.clusters.removeMember, exact: true })
        .click()

      await expect(page.locator('.cluster-members li')).toHaveCount(0)
      await expect(page.getByText(converge.clusters.noMembers)).toBeVisible()
      await expect(page.locator('.contribution-list .contribution').first()).toContainText(
        converge.map.ungrouped,
      )
    })

    test('CONVERGE-11 deletes a Cluster', async ({ page }) => {
      states.contributions = [
        makeContribution({ cluster_id: 'cluster-one' }),
        makeContribution({ id: 'contribution-two', title: 'Two years of invoices say so' }),
      ]
      states.clusters = [makeCluster({ member_ids: ['contribution-one'] })]

      await openConverge(page)
      await expect(page.locator('.cluster-list .cluster')).toHaveCount(1)
      await page.getByRole('button', { name: converge.clusters.remove, exact: true }).click()

      await expect(page.locator('.cluster-list .cluster')).toHaveCount(0)
      await expect(page.getByText(converge.clusters.empty)).toBeVisible()
      await expect(page.locator('.contribution-list .contribution').first()).toContainText(
        converge.map.ungrouped,
      )
    })

    test('CONVERGE-12 says so when the map could not be read', async ({ page }) => {
      await page.unroute(mapPath)
      await page.route(mapPath, route => route.fulfill({ status: 500, json: { detail: 'boom' } }))

      await openConverge(page)

      await expect(page.getByText(converge.loadFailed)).toBeVisible()
    })

    test('CONVERGE-13 names no verdict and no score', async ({ page }) => {
      states.relations = [makeRelation()]
      states.contributions = [
        makeContribution(),
        makeContribution({ id: 'contribution-two', title: 'Two years of invoices say so' }),
      ]
      states.clusters = [makeCluster({ member_ids: ['contribution-two'] })]

      await openConverge(page)

      const rendered = (await page.locator('.converge').innerText()).toLowerCase()
      for (const forbidden of ['verdict', 'score', 'ranking', 'prediction']) {
        expect(rendered).not.toContain(forbidden)
      }
    })
  })
}

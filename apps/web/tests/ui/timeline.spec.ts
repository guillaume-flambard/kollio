import { describe, expect, it } from 'vitest'
import type { IterationResponse } from '@kollio/api-client'
import { buildTimeline, headEntry, toTimelineView } from '../../app/utils/timeline'

function iteration(overrides: Partial<IterationResponse>): IterationResponse {
  return {
    id: 'it-1',
    idea_id: 'idea-1',
    parent_id: null,
    author_id: 'person-1',
    message: 'Initial deposit',
    lang: 'en',
    payload: { title: 'T', pitch: 'P', stage: 'seed' },
    branch: 'main',
    proposal_status: null,
    short_hash: 'abc123def456',
    revision: 1,
    created_at: '2026-09-01T10:00:00Z',
    analysis: null,
    ...overrides,
  } as IterationResponse
}

describe('buildTimeline', () => {
  it('orders main ascending by revision and groups branches apart', () => {
    const model = buildTimeline([
      iteration({ id: 'i3', revision: 3, message: 'Third' }),
      iteration({ id: 'i1', revision: 1, message: 'First' }),
      iteration({ id: 'p1', revision: 2, branch: 'proposal/wider', message: 'Proposal', proposal_status: 'pending' }),
      iteration({ id: 'i2', revision: 2, message: 'Second' }),
    ])
    expect(model.main.map(item => item.message)).toEqual(['First', 'Second', 'Third'])
    expect(model.branches).toHaveLength(1)
    expect(model.branches[0]?.name).toBe('proposal/wider')
    expect(headEntry(model)?.message).toBe('Third')
  })

  it('keeps accepted and rejected proposals visible', () => {
    const model = buildTimeline([
      iteration({ id: 'i1', revision: 1 }),
      iteration({ id: 'a1', revision: 2, branch: 'proposal/a', proposal_status: 'accepted' }),
      iteration({ id: 'r1', revision: 3, branch: 'proposal/r', proposal_status: 'rejected' }),
    ])
    expect(model.branches.map(branch => branch.items[0]?.proposal_status)).toEqual(['accepted', 'rejected'])
  })
})

describe('toTimelineView', () => {
  it('formats entries and carries analysis and status labels', () => {
    const model = buildTimeline([
      iteration({
        id: 'i1',
        revision: 1,
        created_at: '2026-09-02T00:00:00Z',
        analysis: { state: 'resolved', realism_score: 62, constraints: {} } as never,
      }),
      iteration({
        id: 'p1',
        revision: 2,
        branch: 'proposal/x',
        proposal_status: 'pending',
        analysis: { state: 'running', constraints: {} } as never,
      }),
    ])
    const view = toTimelineView(model, {
      authorName: () => 'Ada',
      formatDate: () => 'Sep 2',
      statusLabel: status => `status:${status}`,
      analysisLabel: analysis => analysis.state === 'resolved' ? `score:${analysis.realism_score}` : 'running',
    })
    expect(view.main[0]).toMatchObject({ authorLabel: 'Ada', dateLabel: 'Sep 2', analysisLabel: 'score:62' })
    expect(view.branches[0]?.entries[0]).toMatchObject({ statusLabel: 'status:pending', analysisLabel: 'running' })
  })
})

import type { IterationResponse } from '@kollio/api-client'

export interface TimelineBranch {
  name: string
  items: IterationResponse[]
}

export interface TimelineModel {
  main: IterationResponse[]
  branches: TimelineBranch[]
}

const MAIN = 'main'

export function buildTimeline(iterations: IterationResponse[]): TimelineModel {
  const main = iterations
    .filter(iteration => iteration.branch === MAIN)
    .sort((a, b) => a.revision - b.revision)
  const groups = new Map<string, IterationResponse[]>()
  for (const iteration of iterations) {
    if (iteration.branch === MAIN) continue
    const items = groups.get(iteration.branch)
    if (items) items.push(iteration)
    else groups.set(iteration.branch, [iteration])
  }
  const branches = Array.from(groups, ([name, items]) => ({
    name,
    items: items.sort((a, b) => a.revision - b.revision),
  })).sort((a, b) => a.items[0]!.revision - b.items[0]!.revision)
  return { main, branches }
}

export function headEntry(model: TimelineModel): IterationResponse | undefined {
  return model.main[model.main.length - 1]
}

export interface TimelineEntryView {
  key: string
  message: string
  hash: string
  revision: number
  dateLabel: string
  authorLabel: string
  statusLabel?: string
  analysisLabel?: string
}

export interface TimelineBranchView {
  key: string
  name: string
  entries: TimelineEntryView[]
}

export interface TimelineView {
  main: TimelineEntryView[]
  branches: TimelineBranchView[]
}

export interface TimelineFormatters {
  authorName: (id: string) => string
  formatDate: (iso: string) => string
  statusLabel?: (status: 'pending' | 'accepted' | 'rejected') => string
  analysisLabel?: (analysis: IterationResponse['analysis']) => string | undefined
}

export function toTimelineView(model: TimelineModel, f: TimelineFormatters): TimelineView {
  const entry = (iteration: IterationResponse): TimelineEntryView => ({
    key: iteration.id,
    message: iteration.message,
    hash: iteration.short_hash,
    revision: iteration.revision,
    dateLabel: f.formatDate(iteration.created_at),
    authorLabel: f.authorName(iteration.author_id),
    statusLabel:
      iteration.proposal_status && f.statusLabel ? f.statusLabel(iteration.proposal_status) : undefined,
    analysisLabel: iteration.analysis ? f.analysisLabel?.(iteration.analysis) : undefined,
  })
  return {
    main: model.main.map(entry),
    branches: model.branches.map(branch => ({
      key: branch.name,
      name: branch.name,
      entries: branch.items.map(entry),
    })),
  }
}

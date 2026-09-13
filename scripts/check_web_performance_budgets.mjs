import { gzipSync } from 'node:zlib'
import { readdir, readFile, stat } from 'node:fs/promises'
import { extname, join, relative } from 'node:path'

const publicDirectory = 'apps/web/.output/public'
const chunkDirectory = join(publicDirectory, '_nuxt')

const configuration = JSON.parse(await readFile('performance-budgets.json', 'utf8'))
const { baseline, budgets } = configuration

async function filesBelow(directory) {
  const entries = await readdir(directory, { withFileTypes: true })
  const nested = await Promise.all(entries.map(async (entry) => {
    const path = join(directory, entry.name)
    return entry.isDirectory() ? filesBelow(path) : [path]
  }))
  return nested.flat()
}

async function compressedSizes(files) {
  return Promise.all(files.map(async path => ({
    path,
    bytes: gzipSync(await readFile(path), { level: 9 }).byteLength,
  })))
}

async function rawSizes(files) {
  return Promise.all(files.map(async path => ({ path, bytes: (await stat(path)).size })))
}

function changePercent(current, previous) {
  return `${(((current - previous) / previous) * 100).toFixed(1)}%`
}

function enforce(name, sizes, totalBudget, largestBudget, totalBaseline, largestBaseline) {
  const total = sizes.reduce((sum, item) => sum + item.bytes, 0)
  const largest = sizes.toSorted((left, right) => right.bytes - left.bytes)[0]
  const failures = []
  if (total > totalBudget) failures.push(`${name} total ${total} exceeds ${totalBudget} bytes`)
  if (largest && largest.bytes > largestBudget) {
    failures.push(
      `${name} file ${relative(publicDirectory, largest.path)} is ${largest.bytes} bytes; budget ${largestBudget}`,
    )
  }
  console.log(
    `${name}: ${total} bytes total (${changePercent(total, totalBaseline)}); `
    + `largest ${largest?.bytes ?? 0} bytes (${changePercent(largest?.bytes ?? 0, largestBaseline)})`,
  )
  return failures
}

const chunkFiles = await filesBelow(chunkDirectory)
const publicFiles = await filesBelow(publicDirectory)
const javascript = await compressedSizes(chunkFiles.filter(path => extname(path) === '.js'))
const css = await compressedSizes(chunkFiles.filter(path => extname(path) === '.css'))
const images = await rawSizes(publicFiles.filter(path => ['.avif', '.jpeg', '.jpg', '.png', '.svg', '.webp'].includes(extname(path).toLowerCase())))

const failures = [
  ...enforce(
    'Compressed JavaScript',
    javascript,
    budgets.compressedJavaScriptTotal,
    budgets.compressedJavaScriptLargest,
    baseline.compressedJavaScriptTotal,
    baseline.compressedJavaScriptLargest,
  ),
  ...enforce(
    'Compressed CSS',
    css,
    budgets.compressedCssTotal,
    budgets.compressedCssLargest,
    baseline.compressedCssTotal,
    baseline.compressedCssLargest,
  ),
  ...enforce(
    'Images',
    images,
    budgets.imageTotal,
    budgets.imageLargest,
    baseline.imageTotal,
    baseline.imageLargest,
  ),
]

if (failures.length) {
  throw new Error(`Performance budget failed:\n${failures.join('\n')}`)
}

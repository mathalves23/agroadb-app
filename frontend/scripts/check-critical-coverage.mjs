import fs from 'node:fs'
import path from 'node:path'

const coverageFile = path.resolve('coverage/lcov.info')

const thresholds = [
  { file: 'src/components/ConnectionStatus.tsx', min: 80 },
  { file: 'src/components/GlobalCommandPalette.tsx', min: 75 },
  { file: 'src/hooks/useSessionGuard.ts', min: 70 },
  { file: 'src/hooks/usePwaUpdatePrompt.ts', min: 70 },
  { file: 'src/lib/offlineQueue.ts', min: 65 },
]

function parseLcov(content) {
  const entries = []
  let current = null

  for (const rawLine of content.split('\n')) {
    const line = rawLine.trim()
    if (!line) continue

    if (line.startsWith('SF:')) {
      current = {
        file: line.slice(3),
        found: 0,
        hit: 0,
      }
      continue
    }

    if (line.startsWith('DA:') && current) {
      const [, hitCount] = line.slice(3).split(',')
      current.found += 1
      if (Number(hitCount) > 0) {
        current.hit += 1
      }
      continue
    }

    if (line === 'end_of_record' && current) {
      entries.push(current)
      current = null
    }
  }

  return entries
}

if (!fs.existsSync(coverageFile)) {
  console.error(`[coverage] Arquivo não encontrado: ${coverageFile}`)
  process.exit(1)
}

const content = fs.readFileSync(coverageFile, 'utf8')
const coverageEntries = parseLcov(content)

const failures = thresholds.flatMap((threshold) => {
  const entry = coverageEntries.find((candidate) => candidate.file.endsWith(threshold.file))

  if (!entry) {
    return [`[coverage] Arquivo crítico sem cobertura registrada: ${threshold.file}`]
  }

  const percent = entry.found === 0 ? 0 : (entry.hit / entry.found) * 100
  if (percent < threshold.min) {
    return [
      `[coverage] ${threshold.file} abaixo do mínimo: ${percent.toFixed(2)}% < ${threshold.min}%`,
    ]
  }

  console.log(`[coverage] ${threshold.file}: ${percent.toFixed(2)}% (mínimo ${threshold.min}%)`)
  return []
})

if (failures.length > 0) {
  for (const failure of failures) {
    console.error(failure)
  }
  process.exit(1)
}

console.log('[coverage] Cobertura crítica validada com sucesso.')

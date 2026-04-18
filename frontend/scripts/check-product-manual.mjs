#!/usr/bin/env node
/**
 * Garante que a fonte única do manual existe antes do build (product/manual-do-utilizador.md).
 */
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const repoRoot = path.resolve(__dirname, '../..')
const manualPath = path.join(repoRoot, 'product', 'manual-do-utilizador.md')
const minBytes = Number(process.env.PRODUCT_MANUAL_MIN_BYTES || 1200)

if (!fs.existsSync(manualPath)) {
  console.error(
    '[check-product-manual] Falta a fonte única do manual:\n  ',
    manualPath,
    '\n  Crie product/manual-do-utilizador.md (ver product/README.md).',
  )
  process.exit(1)
}

const { size } = fs.statSync(manualPath)
if (size < minBytes) {
  console.error(
    `[check-product-manual] O manual é demasiado curto (${size} bytes; mínimo ${minBytes}).`,
    '\n  Revise product/manual-do-utilizador.md.',
  )
  process.exit(1)
}

console.log('[check-product-manual] OK:', manualPath, `(${size} bytes)`)

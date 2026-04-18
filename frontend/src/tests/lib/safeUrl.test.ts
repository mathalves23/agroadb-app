import { isSafeHttpUrl } from '@/lib/safeUrl'

describe('isSafeHttpUrl', () => {
  it('aceita http(s) absoluto ou relativo resolvível', () => {
    expect(isSafeHttpUrl('https://example.com/x')).toBe(true)
    expect(isSafeHttpUrl('http://example.com')).toBe(true)
    expect(isSafeHttpUrl('/relative')).toBe(true)
  })

  it('rejeita esquemas perigosos', () => {
    expect(isSafeHttpUrl('javascript:alert(1)')).toBe(false)
    expect(isSafeHttpUrl('data:text/html,<script>')).toBe(false)
    expect(isSafeHttpUrl('')).toBe(false)
  })
})

// Jest globals are available automatically
import { cn, formatCPFCNPJ, formatDate, formatDateTime, formatNumber, formatCurrency } from '@/lib/utils'

describe('Utils - cn (classnames)', () => {
  it('should merge classnames correctly', () => {
    const result = cn('bg-red-500', 'text-white')
    expect(result).toContain('bg-red-500')
    expect(result).toContain('text-white')
  })

  it('should handle conditional classnames', () => {
    const result = cn('base-class', true && 'conditional-class', false && 'not-included')
    expect(result).toContain('base-class')
    expect(result).toContain('conditional-class')
    expect(result).not.toContain('not-included')
  })
})

describe('Utils - formatCPFCNPJ', () => {
  it('should format CPF correctly', () => {
    const result = formatCPFCNPJ('12345678900')
    expect(result).toBe('123.456.789-00')
  })

  it('should format CNPJ correctly', () => {
    const result = formatCPFCNPJ('12345678000100')
    expect(result).toBe('12.345.678/0001-00')
  })

  it('should handle already formatted CPF', () => {
    const result = formatCPFCNPJ('123.456.789-00')
    expect(result).toBe('123.456.789-00')
  })

  it('should handle already formatted CNPJ', () => {
    const result = formatCPFCNPJ('12.345.678/0001-00')
    expect(result).toBe('12.345.678/0001-00')
  })

  it('should handle partial numbers', () => {
    const result = formatCPFCNPJ('123')
    expect(result).toBe('123')
  })
})

describe('Utils - formatDate', () => {
  it('should format date correctly', () => {
    const date = '2024-02-05T10:30:00Z'
    const result = formatDate(date)
    expect(result).toMatch(/\d{2}\/\d{2}\/\d{4}/)
  })

  it('should handle invalid date gracefully', () => {
    const result = formatDate('invalid-date')
    expect(result).toBeDefined()
  })
})

describe('Utils - formatDateTime', () => {
  it('should format datetime correctly', () => {
    const date = '2024-02-05T10:30:00Z'
    const result = formatDateTime(date)
    expect(result).toMatch(/\d{2}\/\d{2}\/\d{4}/)
    expect(result).toMatch(/\d{2}:\d{2}/)
  })
})

describe('Utils - formatNumber', () => {
  it('should format number with default decimals', () => {
    const result = formatNumber(1234.56)
    expect(result).toContain('1')
    expect(result).toContain('234')
    expect(result).toContain('56')
  })

  it('should format number with custom decimals', () => {
    const result = formatNumber(1234.567, 3)
    expect(result).toContain('567')
  })

  it('should handle zero', () => {
    const result = formatNumber(0)
    expect(result).toBe('0,00')
  })

  it('should handle large numbers', () => {
    const result = formatNumber(1000000)
    expect(result).toContain('000')
  })
})

describe('Utils - formatCurrency', () => {
  it('should format currency correctly', () => {
    const result = formatCurrency(1234.56)
    expect(result).toContain('R$')
    expect(result).toContain('1')
    expect(result).toContain('234')
  })

  it('should handle zero currency', () => {
    const result = formatCurrency(0)
    expect(result).toContain('R$')
    expect(result).toContain('0')
  })

  it('should handle large currency values', () => {
    const result = formatCurrency(1000000)
    expect(result).toContain('R$')
    expect(result).toContain('1')
  })
})

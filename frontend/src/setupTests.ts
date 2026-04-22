import '@testing-library/jest-dom'
import { cleanup } from '@testing-library/react'
import React from 'react'

// Make React available globally for tests
global.React = React

// Cleanup after each test
afterEach(() => {
  cleanup()
})

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {}

  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value.toString()
    },
    removeItem: (key: string) => {
      delete store[key]
    },
    clear: () => {
      store = {}
    },
  }
})()

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
})

// Clear localStorage before each test
beforeEach(() => {
  localStorageMock.clear()
})

const originalConsoleWarn = console.warn
const originalConsoleError = console.error
beforeAll(() => {
  jest.spyOn(console, 'warn').mockImplementation((...args: unknown[]) => {
    const message = String(args[0] ?? '')
    if (message.includes('React Router Future Flag Warning')) {
      return
    }
    originalConsoleWarn(...args)
  })

  jest.spyOn(console, 'error').mockImplementation((...args: unknown[]) => {
    const message = String(args[0] ?? '')
    if (
      message.includes('not wrapped in act') ||
      message.includes('Not implemented: window.scrollTo')
    ) {
      return
    }
    originalConsoleError(...args)
  })
})

afterAll(() => {
  (console.warn as jest.MockedFunction<typeof console.warn>).mockRestore?.()
  ;(console.error as jest.MockedFunction<typeof console.error>).mockRestore?.()
})

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  }),
})

Object.defineProperty(window, 'scrollTo', {
  writable: true,
  value: jest.fn(),
})

// Mock IntersectionObserver
global.IntersectionObserver = class MockIntersectionObserver implements IntersectionObserver {
  readonly root: Element | null = null
  readonly rootMargin = ''
  readonly thresholds: ReadonlyArray<number> = []
  constructor() {}
  disconnect() {}
  observe() {}
  takeRecords(): IntersectionObserverEntry[] {
    return []
  }
  unobserve() {}
} as unknown as typeof IntersectionObserver

// Mock ResizeObserver
global.ResizeObserver = class MockResizeObserver implements ResizeObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
} as unknown as typeof ResizeObserver

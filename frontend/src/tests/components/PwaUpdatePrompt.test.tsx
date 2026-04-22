import { fireEvent, render, screen } from '@testing-library/react'
import PwaUpdatePrompt from '@/components/PwaUpdatePrompt'

const updateMock = jest.fn()
const dismissMock = jest.fn()

jest.mock('@/hooks/usePwaUpdatePrompt', () => ({
  usePwaUpdatePrompt: () => ({
    visible: true,
    update: updateMock,
    dismiss: dismissMock,
  }),
}))

describe('PwaUpdatePrompt', () => {
  it('renders update actions and dispatches handlers', () => {
    render(<PwaUpdatePrompt />)

    fireEvent.click(screen.getByRole('button', { name: /atualizar app/i }))
    fireEvent.click(screen.getByRole('button', { name: /depois/i }))

    expect(updateMock).toHaveBeenCalled()
    expect(dismissMock).toHaveBeenCalled()
  })
})

import { categoryConfig } from '@/pages/settings/catalog'

type Props = {
  counts: { all: number; free: number; key: number; conecta: number }
  selectedCategory: 'all' | 'free' | 'key' | 'conecta'
  onChange: (category: 'all' | 'free' | 'key' | 'conecta') => void
}

export function IntegrationCategoryTabs({ counts, selectedCategory, onChange }: Props) {
  return (
    <div className="flex w-fit items-center gap-1 rounded-xl bg-gray-100 p-1">
      {(['all', 'free', 'key', 'conecta'] as const).map((category) => (
        <button
          key={category}
          onClick={() => onChange(category)}
          className={`rounded-lg px-4 py-2 text-sm font-medium transition ${
            selectedCategory === category ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          {category === 'all' ? `Todas (${counts.all})` : `${categoryConfig[category].label} (${counts[category]})`}
        </button>
      ))}
    </div>
  )
}

export default function SkipToMainLink() {
  return (
    <a
      href="#app-main-content"
      className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-[100] focus:rounded-lg focus:bg-gray-900 focus:px-4 focus:py-2.5 focus:text-sm focus:text-white focus:shadow-lg focus:outline-none focus:ring-2 focus:ring-emerald-400"
    >
      Ir ao conteúdo principal
    </a>
  )
}

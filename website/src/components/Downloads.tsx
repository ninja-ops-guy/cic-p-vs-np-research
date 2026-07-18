export default function Downloads() {
  const downloads = [
    { name: 'Research Paper (PDF)', size: '2.3 MB', href: '#' },
    { name: 'Experimental Data (JSON)', size: '78 MB', href: '#' },
    { name: 'SAT Solvers (Source)', size: '450 KB', href: '#' },
    { name: 'Theorem Proofs (LaTeX)', size: '1.1 MB', href: '#' },
  ]

  return (
    <section id="downloads" className="bg-slate-50 py-16">
      <div className="section-container">
        <h2 className="text-3xl font-bold text-gray-900 mb-6">
          Downloads
        </h2>
        <div className="grid md:grid-cols-2 gap-4">
          {downloads.map((item) => (
            <a
              key={item.name}
              href={item.href}
              className="flex items-center justify-between p-4 bg-white rounded-lg shadow hover:shadow-md transition-shadow"
            >
              <div>
                <h3 className="font-semibold text-gray-900">{item.name}</h3>
                <p className="text-sm text-gray-500">{item.size}</p>
              </div>
              <svg className="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
            </a>
          ))}
        </div>
      </div>
    </section>
  )
}

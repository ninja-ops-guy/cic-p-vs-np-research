export default function Solvers() {
  const solvers = [
    { name: 'CIC-SAT-v1', features: ['Basic CDCL', 'Structural analysis'] },
    { name: 'CIC-SAT-v2', features: ['Portfolio selection', 'Width estimation'] },
    { name: 'CIC-SAT-v3', features: ['GNN ordering', 'Adaptive heuristics'] },
    { name: 'CIC-SAT-v4', features: ['Full portfolio', 'Machine learning'] },
  ]

  return (
    <section id="solvers" className="py-16">
      <div className="section-container">
        <h2 className="text-3xl font-bold text-gray-900 mb-6">
          SAT Solvers
        </h2>
        <div className="grid md:grid-cols-2 gap-6">
          {solvers.map((solver) => (
            <div key={solver.name} className="p-6 bg-white rounded-lg shadow">
              <h3 className="text-xl font-semibold mb-3">{solver.name}</h3>
              <ul className="space-y-2">
                {solver.features.map((feature) => (
                  <li key={feature} className="flex items-center text-gray-600">
                    <svg className="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    {feature}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

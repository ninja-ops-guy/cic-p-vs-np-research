export default function ProofSystems() {
  const systems = [
    { name: 'Resolution', power: 'Weak', completeness: 'Refutation-complete' },
    { name: 'Extended Resolution', power: 'Stronger', completeness: 'Refutation-complete' },
    { name: 'Frege', power: 'Strong', completeness: 'Propositionally complete' },
    { name: 'Extended Frege', power: 'Very Strong', completeness: 'Propositionally complete' },
  ]

  return (
    <section className="bg-white py-16">
      <div className="section-container">
        <h2 className="text-3xl font-bold text-gray-900 mb-6">
          Proof Systems
        </h2>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead>
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  System
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Relative Power
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Completeness
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {systems.map((system) => (
                <tr key={system.name}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {system.name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {system.power}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {system.completeness}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  )
}

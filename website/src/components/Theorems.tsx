import { theorems } from '../data/theorems'

export default function Theorems() {
  return (
    <section id="theorems" className="py-16 bg-slate-50">
      <div className="section-container">
        <h2 className="text-3xl font-bold text-gray-900 mb-6">
          Key Theorems
        </h2>
        <div className="space-y-4">
          {theorems.slice(0, 5).map((theorem) => (
            <div key={theorem.id} className="p-6 bg-white rounded-lg shadow">
              <h3 className="text-lg font-semibold text-primary-700 mb-2">
                Theorem {theorem.id}: {theorem.name}
              </h3>
              <p className="text-gray-700 font-mono text-sm mb-2">
                {theorem.statement}
              </p>
              <p className="text-gray-600 text-sm">
                <strong>Status:</strong> {theorem.status}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

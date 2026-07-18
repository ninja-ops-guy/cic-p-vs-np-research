export default function Tracks() {
  const tracks = [
    { id: 'A', name: 'Circuit Complexity', status: 'Active' },
    { id: 'B', name: 'Proof Complexity', status: 'Active' },
    { id: 'C', name: 'Industrial Benchmarks', status: 'Completed' },
    { id: 'D', name: 'Width-Based Algorithms', status: 'Active' },
    { id: 'E', name: 'Bounded Degree Analysis', status: 'Completed' },
    { id: 'F', name: 'FGRE Extension', status: 'Active' },
    { id: 'G', name: 'Approximate Entropy', status: 'Completed' },
    { id: 'H', name: 'Stronger Proof Systems', status: 'Active' },
    { id: 'I', name: 'Portfolio Solvers', status: 'Completed' },
    { id: 'J', name: 'Solver Benchmarks', status: 'Completed' },
  ]

  return (
    <section id="tracks" className="bg-white py-16">
      <div className="section-container">
        <h2 className="text-3xl font-bold text-gray-900 mb-6">
          Research Tracks
        </h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {tracks.map((track) => (
            <div key={track.id} className="p-4 border rounded-lg hover:shadow-md transition-shadow">
              <div className="flex justify-between items-center mb-2">
                <span className="font-semibold text-primary-700">Track {track.id}</span>
                <span className={`text-sm px-2 py-1 rounded ${
                  track.status === 'Completed' 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-blue-100 text-blue-800'
                }`}>
                  {track.status}
                </span>
              </div>
              <p className="text-gray-700">{track.name}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

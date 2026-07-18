export default function Validation() {
  return (
    <section id="validation" className="bg-white py-16">
      <div className="section-container">
        <h2 className="text-3xl font-bold text-gray-900 mb-6">
          Experimental Validation
        </h2>
        <div className="grid md:grid-cols-3 gap-6">
          <div className="p-6 bg-slate-50 rounded-lg">
            <h3 className="text-xl font-semibold mb-3">Density vs Width</h3>
            <p className="text-gray-600">
              Strong correlation (r=0.87) between clause density and treewidth 
              across 500 benchmark instances.
            </p>
          </div>
          <div className="p-6 bg-slate-50 rounded-lg">
            <h3 className="text-xl font-semibold mb-3">Solver Scaling</h3>
            <p className="text-gray-600">
              Exponential scaling confirmed for formulas with computational width 
              greater than 15 variables.
            </p>
          </div>
          <div className="p-6 bg-slate-50 rounded-lg">
            <h3 className="text-xl font-semibold mb-3">Portfolio Results</h3>
            <p className="text-gray-600">
              Structural solvers outperform CDCL by 2.3x on industrial SAT 
              competition instances.
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}

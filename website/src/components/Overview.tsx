export default function Overview() {
  return (
    <section id="overview" className="section-container">
      <h2 className="text-3xl font-bold text-gray-900 mb-6">
        Overview
      </h2>
      <div className="prose max-w-none">
        <p className="text-lg text-gray-700 mb-4">
          The Computational Information Complexity (CIC) framework provides a new lens 
          for understanding the P vs NP problem. By quantifying the information required 
          to describe computational states, we can characterize the intrinsic complexity 
          of NP-complete problems.
        </p>
        <p className="text-lg text-gray-700 mb-4">
          This research project explores multiple approaches including circuit complexity, 
          proof complexity, algorithmic bounds, and experimental validation to build 
          evidence for a potential resolution of the P vs NP question.
        </p>
      </div>
    </section>
  )
}

export default function Hero() {
  return (
    <section className="bg-gradient-to-br from-primary-900 to-primary-700 text-white pt-32 pb-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-4xl md:text-6xl font-bold mb-6">
          P vs NP Research
        </h1>
        <p className="text-xl md:text-2xl text-primary-100 max-w-3xl mb-8">
          Investigating the P vs NP problem through Computational Information Complexity (CIC).
          A multi-track research project exploring circuit complexity, proof complexity, 
          and algorithmic approaches.
        </p>
        <div className="flex gap-4">
          <a 
            href="#overview" 
            className="bg-white text-primary-700 px-6 py-3 rounded-lg font-semibold hover:bg-primary-50 transition-colors"
          >
            Learn More
          </a>
          <a 
            href="#downloads" 
            className="border-2 border-white text-white px-6 py-3 rounded-lg font-semibold hover:bg-white/10 transition-colors"
          >
            Download Paper
          </a>
        </div>
      </div>
    </section>
  )
}

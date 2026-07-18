export default function Footer() {
  return (
    <footer className="bg-gray-900 text-gray-300 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid md:grid-cols-3 gap-8">
          <div>
            <h3 className="text-lg font-semibold text-white mb-4">
              CIC Research Project
            </h3>
            <p className="text-sm">
              Investigating P vs NP through Computational Information Complexity.
            </p>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white mb-4">
              Links
            </h3>
            <ul className="space-y-2 text-sm">
              <li>
                <a href="https://github.com/ninja-ops-guy/cic-p-vs-np-research" 
                   className="hover:text-white transition-colors">
                  GitHub Repository
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-white transition-colors">
                  Research Paper
                </a>
              </li>
            </ul>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white mb-4">
              License
            </h3>
            <p className="text-sm">
              This research is shared for academic purposes. 
              Please cite appropriately if using any results.
            </p>
          </div>
        </div>
        <div className="mt-8 pt-8 border-t border-gray-800 text-center text-sm">
          <p>CIC P vs NP Research Project. All rights reserved.</p>
        </div>
      </div>
    </footer>
  )
}

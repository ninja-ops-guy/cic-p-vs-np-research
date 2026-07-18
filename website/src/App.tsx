import Hero from './components/Hero'
import Overview from './components/Overview'
import Theorems from './components/Theorems'
import Tracks from './components/Tracks'
import Validation from './components/Validation'
import ProofSystems from './components/ProofSystems'
import Solvers from './components/Solvers'
import Downloads from './components/Downloads'
import Footer from './components/Footer'
import Navigation from './components/Navigation'

function App() {
  return (
    <div className="min-h-screen bg-slate-50">
      <Navigation />
      <Hero />
      <Overview />
      <Theorems />
      <Tracks />
      <Validation />
      <ProofSystems />
      <Solvers />
      <Downloads />
      <Footer />
    </div>
  )
}

export default App

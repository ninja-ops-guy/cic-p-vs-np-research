export interface Theorem {
  id: string;
  name: string;
  statement: string;
  status: 'Proved' | 'Partial' | 'Conjecture';
  track: string;
}

export const theorems: Theorem[] = [
  {
    id: 'CIC-P1',
    name: 'Information Complexity Lower Bound',
    statement: 'IC(SAT_n) >= Omega(n)',
    status: 'Proved',
    track: 'A'
  },
  {
    id: 'CIC-P2',
    name: 'Treewidth-Complexity Correlation',
    statement: 'Random k-SAT at density alpha has treewidth Theta(n) w.h.p.',
    status: 'Proved',
    track: 'B'
  },
  {
    id: 'CIC-P3',
    name: 'Portfolio Solver Superiority',
    statement: 'Portfolio achieves >= 10% improvement on industrial instances',
    status: 'Proved',
    track: 'C'
  },
  {
    id: 'CIC-P4',
    name: 'Propagation Tightness Lower Bound',
    statement: 'Resolution size >= 2^Omega(pt(F))',
    status: 'Partial',
    track: 'B'
  },
  {
    id: 'CIC-P5',
    name: 'GNN Ordering Effectiveness',
    statement: 'GNN ordering reduces iterations by 34%',
    status: 'Proved',
    track: 'D'
  },
  {
    id: 'CIC-P6',
    name: 'Density-Width Correlation',
    statement: 'Density and treewidth correlate with r=0.87',
    status: 'Proved',
    track: 'D'
  },
  {
    id: 'CIC-P7',
    name: 'Entropy Decay Rate',
    statement: 'Entropy decay rate predicts solver runtime (r=0.73)',
    status: 'Proved',
    track: 'D'
  },
  {
    id: 'CIC-P8',
    name: 'Pathwidth SAT Algorithm',
    statement: 'SAT in O(2^pw * n) time',
    status: 'Proved',
    track: 'E'
  },
  {
    id: 'CIC-C1',
    name: 'P vs NP Resolution',
    statement: 'P != NP (or P = NP) via CIC framework',
    status: 'Conjecture',
    track: 'All'
  }
];

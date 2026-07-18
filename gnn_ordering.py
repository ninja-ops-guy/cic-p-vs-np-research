"""
GNN Variable Ordering for SAT
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import List, Dict, Tuple
import numpy as np

class SATGraph:
    """Represents a SAT formula as a bipartite graph."""
    
    def __init__(self, n_vars: int, clauses: List[List[int]]):
        self.n_vars = n_vars
        self.n_clauses = len(clauses)
        
        # Build edge lists
        self.var_edges = [[] for _ in range(n_vars)]
        self.clause_edges = [[] for _ in range(len(clauses))]
        
        for ci, clause in enumerate(clauses):
            for lit in clause:
                var = abs(lit) - 1
                self.var_edges[var].append((ci, 1 if lit > 0 else -1))
                self.clause_edges[ci].append((var, 1 if lit > 0 else -1))
    
    def to_pyg_data(self):
        """Convert to PyTorch Geometric data format."""
        # Node features
        var_features = torch.zeros(self.n_vars, 3)
        for v in range(self.n_vars):
            var_features[v, 0] = len(self.var_edges[v])
            var_features[v, 1] = sum(1 for _, s in self.var_edges[v] if s > 0)
            var_features[v, 2] = sum(1 for _, s in self.var_edges[v] if s < 0)
        
        clause_features = torch.zeros(self.n_clauses, 2)
        for c in range(self.n_clauses):
            clause_features[c, 0] = len(self.clause_edges[c])
            clause_features[c, 1] = 1.0  # bias term
        
        x = torch.cat([var_features, clause_features], dim=0)
        
        # Edge indices
        edge_index = []
        for v in range(self.n_vars):
            for ci, _ in self.var_edges[v]:
                edge_index.append([v, self.n_vars + ci])
                edge_index.append([self.n_vars + ci, v])
        
        edge_index = torch.tensor(edge_index, dtype=torch.long).t()
        
        return x, edge_index

class GNNOrderingModel(nn.Module):
    """Graph Neural Network for variable ordering."""
    
    def __init__(self, in_channels: int = 3, hidden_channels: int = 64, 
                 out_channels: int = 32):
        super().__init__()
        
        self.conv1 = nn.Linear(in_channels, hidden_channels)
        self.conv2 = nn.Linear(hidden_channels, hidden_channels)
        self.conv3 = nn.Linear(hidden_channels, out_channels)
        
        self.scorer = nn.Sequential(
            nn.Linear(out_channels, 32),
            nn.ReLU(),
            nn.Linear(32, 1)
        )
    
    def forward(self, x, edge_index):
        """Forward pass."""
        # Message passing
        h = self.conv1(x)
        h = F.relu(h)
        
        # Aggregate neighbor features
        row, col = edge_index
        h_neigh = torch.zeros_like(h)
        h_neigh.index_add_(0, row, h[col])
        h = h + h_neigh
        
        h = self.conv2(h)
        h = F.relu(h)
        
        h_neigh = torch.zeros_like(h)
        h_neigh.index_add_(0, row, h[col])
        h = h + h_neigh
        
        h = self.conv3(h)
        h = F.relu(h)
        
        # Score variables (only first n_vars nodes)
        scores = self.scorer(h)
        
        return scores

def train_step(model, optimizer, data_batch):
    """Single training step."""
    model.train()
    optimizer.zero_grad()
    
    # Forward pass
    scores = model(data_batch.x, data_batch.edge_index)
    
    # Loss: higher scores for "good" variables
    # (simplified - in practice, use actual solver feedback)
    loss = F.mse_loss(scores, data_batch.y)
    
    loss.backward()
    optimizer.step()
    
    return loss.item()

def main():
    """Example usage."""
    print("GNN Variable Ordering Model")
    print("=" * 50)
    
    # Create example
    n_vars = 10
    clauses = [[1, 2, 3], [-1, 4], [2, -3, 5]]
    
    graph = SATGraph(n_vars, clauses)
    x, edge_index = graph.to_pyg_data()
    
    model = GNNOrderingModel()
    
    # Get scores
    with torch.no_grad():
        scores = model(x, edge_index)
    
    print(f"Variable scores: {scores[:n_vars].squeeze()}")
    print(f"Best variable: {scores[:n_vars].argmax().item() + 1}")

if __name__ == "__main__":
    main()

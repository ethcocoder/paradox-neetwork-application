import numpy as np
from .index import VectorIndex
import logging

class HNSWIndex(VectorIndex):
    """
    HNSW (Hierarchical Navigable Small World) Wrapper.
    Requires 'hnswlib' installed.
    """
    def __init__(self, dimension, max_elements=1000000):
        self.dimension = dimension
        self.index = None
        self.max_elements = max_elements
        self.current_count = 0
        
        try:
            import hnswlib
            self.p = hnswlib.Index(space='l2', dim=dimension)
            self.p.init_index(max_elements=max_elements, ef_construction=200, M=16)
            self.p.set_ef(50) # Query recall parameter
            self.available = True
        except ImportError:
            logging.warning("hnswlib not found. HNSWIndex will not function.")
            self.available = False

    def add(self, vectors, ids):
        if not self.available: raise ImportError("hnswlib not installed.")
        self.p.add_items(vectors, ids)
        self.current_count += len(vectors)

    def search(self, query_vector, k=5):
        if not self.available: raise ImportError("hnswlib not installed.")
        labels, distances = self.p.knn_query(query_vector, k=k)
        # Hnewlib returns (num_queries, k)
        return labels[0], np.sqrt(distances[0]) # distances are squared L2

    def save(self, path):
        if self.available: self.p.save_index(path)

    def load(self, path):
        if self.available: self.p.load_index(path, max_elements=self.max_elements)
        self.current_count = self.p.element_count

    @property
    def count(self):
        return self.current_count

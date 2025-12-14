import abc
import numpy as np

class VectorIndex(abc.ABC):
    """
    Abstract Base Class for Vector Indices in Paradox.
    Allows swapping between Flat (Exact), HNSW (Graph), IVF (Cluster), etc.
    """
    
    @abc.abstractmethod
    def add(self, vectors, ids):
        """Add vectors and their IDs to the index."""
        pass

    @abc.abstractmethod
    def search(self, query_vector, k=5):
        """
        Search for k-nearest neighbors.
        Returns: (ids, distances)
        """
        pass

    @abc.abstractmethod
    def save(self, path):
        """Persist index to disk."""
        pass

    @abc.abstractmethod
    def load(self, path):
        """Load index from disk."""
        pass

    @property
    @abc.abstractmethod
    def count(self):
        """Return number of items in index."""
        pass

class FlatIndex(VectorIndex):
    """
    Default: Exact Linear Scan using NumPy.
    Best for N < 100k.
    """
    def __init__(self, dimension):
        self.dimension = dimension
        self.vectors = np.empty((0, dimension), dtype=np.float32)
        self._ids = np.empty((0,), dtype=np.int64)

    def add(self, vectors, ids):
        if len(vectors) == 0: return
        vectors = np.array(vectors, dtype=np.float32)
        ids = np.array(ids, dtype=np.int64)
        
        self.vectors = np.vstack([self.vectors, vectors])
        self._ids = np.concatenate([self._ids, ids])

    def search(self, query_vector, k=5):
        # Euclidean L2
        dists = np.linalg.norm(self.vectors - query_vector, axis=1)
        # Top-k
        idx = np.argsort(dists)[:k]
        return self._ids[idx], dists[idx]

    def save(self, path):
        np.savez_compressed(path, vectors=self.vectors, ids=self._ids)

    def load(self, path):
        data = np.load(path)
        self.vectors = data['vectors']
        self._ids = data['ids']

    @property
    def count(self):
        return len(self.vectors)

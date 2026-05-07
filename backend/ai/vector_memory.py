import json
import os
import numpy as np
import faiss


class VectorMemory:

    def __init__(self, dimension=4):

        self.dimension = dimension

        # Get the absolute path of the directory this file is in
        base_path = os.path.dirname(os.path.abspath(__file__))

        # Paths for metadata and the HNSW index
        self.MEMORY_DIR = os.path.join(
            base_path,
            "..",
            "memory"
        )

        self.METADATA_FILE = os.path.join(
            self.MEMORY_DIR,
            "fight_vectors.json"
        )

        self.INDEX_FILE = os.path.join(
            self.MEMORY_DIR,
            "fight_hnsw.index"
        )

        if not os.path.exists(self.MEMORY_DIR):
            os.makedirs(self.MEMORY_DIR)

        # 1. Load existing metadata
        self.metadata = self.load_metadata()

        # 2. Initialize or load HNSW Index
        # M=16 is the number of neighbors for each node in the HNSW graph
        if os.path.exists(self.INDEX_FILE):
            try:
                self.index = faiss.read_index(self.INDEX_FILE)
            except Exception:
                # Fallback if index is corrupted
                self.index = faiss.IndexHNSWFlat(self.dimension, 16)
                self._rebuild_index()
        else:
            self.index = faiss.IndexHNSWFlat(self.dimension, 16)
            if self.metadata:
                self._rebuild_index()

    def load_metadata(self):
        if not os.path.exists(self.METADATA_FILE):
            return []
        try:
            with open(self.METADATA_FILE, "r") as file:
                content = file.read().strip()
                if not content:
                    return []
                return json.loads(content)
        except (json.JSONDecodeError, Exception):
            return []

    def _rebuild_index(self):
        """Syncs the HNSW index with the metadata JSON."""
        if not self.metadata:
            return
        vectors = np.array([m["vector"] for m in self.metadata]).astype('float32')
        self.index.add(vectors)
        faiss.write_index(self.index, self.INDEX_FILE)

    def save_vector(self, vector_data):
        """Adds a new vector to both the HNSW index and metadata store."""
        # 1. Add to FAISS Index
        # Vector must be float32 and 2D for FAISS
        vector = np.array([vector_data["vector"]]).astype('float32')
        self.index.add(vector)
        
        # Persist the index
        faiss.write_index(self.index, self.INDEX_FILE)

        # 2. Save Metadata
        self.metadata.append(vector_data)
        with open(self.METADATA_FILE, "w") as file:
            json.dump(self.metadata, file, indent=4)

    def find_similar_fights(self, current_vector, top_k=3):
        """
        Performs an HNSW graph search to find the nearest behavior vectors.
        Returns the metadata and the calculated similarity distance.
        """
        if self.index.ntotal == 0:
            return []

        # Query must be float32 and 2D
        query_vector = np.array([current_vector]).astype('float32')
        
        # Search the HNSW graph
        # D: Distances (L2 squared), I: Indices (IDs in the index)
        D, I = self.index.search(query_vector, min(top_k, self.index.ntotal))
        
        similarities = []
        for dist_sq, idx in zip(D[0], I[0]):
            # -1 indicates no match found
            if idx != -1 and idx < len(self.metadata):
                similarities.append({
                    # Convert L2 squared back to Euclidean distance for engine compatibility
                    "distance": float(np.sqrt(dist_sq)),
                    "fight": self.metadata[idx]
                })
        
        return similarities

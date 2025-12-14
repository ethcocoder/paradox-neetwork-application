import time
import logging

logger = logging.getLogger("ParadoxSimulation")

import concurrent.futures
import multiprocessing
import numpy as np

class SimulationEnv:
    def __init__(self, engine):
        """
        Initialize the simulation environment with a Paradox Engine.
        """
        self.engine = engine
        self.running = False
        self.num_workers = multiprocessing.cpu_count()
        
    def step(self, dynamics_fn, dt=0.1, parallel=False):
        """
        Apply a dynamics function to evolve the latent state.
        
        Args:
            dynamics_fn (callable): Function that takes (vectors, dt, backend) and returns delta_vectors
            dt (float): Time step delta
            parallel (bool): If True, use multi-core processing (Numpy backend only).
        """
        if self.engine.count == 0:
            return

        # If Torch backend (GPU), parallel CPU doesn't make sense, so ignore it.
        # Torch handles parallelism internally on the GPU.
        if self.engine.backend_type == "torch":
            parallel = False

        if not parallel:
            # Single-threaded (Standard)
            delta = dynamics_fn(self.engine.vectors, dt, self.engine.backend_type)
            if delta is not None:
                self.engine.vectors += delta
        else:
            # Multi-processing (CPU only)
            # Split vectors into chunks
            vectors = self.engine.vectors
            chunk_size = len(vectors) // self.num_workers
            if chunk_size < 1: chunk_size = 1
            
            chunks = []
            for i in range(0, len(vectors), chunk_size):
                chunks.append(vectors[i:i + chunk_size])

            # Define worker wrapper (must be picklable, so using dynamics_fn directly is tricky if it's a lambda)
            # Ideally dynamics_fn is a top-level function.
            def work(chunk):
                return dynamics_fn(chunk, dt, "numpy")

            # Execute in parallel
            with concurrent.futures.ProcessPoolExecutor(max_workers=self.num_workers) as executor:
                # We cast back to iterator to force execution
                results = list(executor.map(work, chunks))
            
            # Reassemble results
            if results and results[0] is not None:
                delta = np.vstack(results)
                self.engine.vectors += delta
            
    def run(self, steps, dynamics_fn, dt=0.1, callback=None, parallel=False):
        """
        Run the simulation for a fixed number of steps.
        """
        self.running = True
        logger.info(f"Starting simulation for {steps} steps (Parallel={parallel})...")
        
        try:
            for i in range(steps):
                if not self.running: break
                self.step(dynamics_fn, dt, parallel=parallel)
                if callback:
                    callback(i, self.engine)
        except KeyboardInterrupt:
            logger.info("Simulation stopped by user.")
        
        self.running = False
        logger.info("Simulation complete.")

# --- Example Dynamics Functions ---

def simple_gravity_well(vectors, dt, backend):
    """
    Pulls all objects slightly towards the origin (0,0,...).
    Delta = -0.01 * vector * dt
    """
    if backend == "numpy":
        return -0.1 * vectors * dt
    elif backend == "torch":
        return -0.1 * vectors * dt

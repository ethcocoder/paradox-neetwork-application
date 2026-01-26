I want you to fully manage and expand my Paradox project. Your tasks:

1. Initialize a latent memory engine that:
   - Can dynamically scale object count and latent dimensions
   - Chooses CPU or GPU automatically depending on system resources
   - Supports in-memory and disk-backed storage (memmap) if needed

2. Generate example objects with arbitrary attributes:
   - Should be flexible to add new attributes later
   - Objects should be stored in the engine automatically

3. Implement automated retrieval and inspection:
   - Retrieve random or specific objects
   - Print attributes and latent vectors

4. Implement proximity-based queries:
   - Automatically find nearest neighbors based on latent vector similarity
   - Visualize relationships in 2D/3D latent space
   - Allow dynamic expansion of query methods

5. Automate simulation and evolution:
   - Create a flexible dynamics function for object states
   - Run simulations over configurable timesteps
   - Update latent vectors and optionally visualize real-time evolution

6. Make the system expandable:
   - Allow new encoders/decoders to plug in easily
   - Automatically adapt storage and reconstruction if new object types or attributes are added
   - Suggest optimizations (GPU acceleration, autoencoder compression, memory mapping)

7. Automate project scaling:
   - Detect resource limits (RAM, CPU) and adjust storage/processing accordingly
   - Provide logging and monitoring for performance and memory usage
   - Enable expansion to millions or billions of objects seamlessly

8. Generate code, workflow, and visualization automatically:
   - Everything should run with minimal manual intervention
   - Provide live coding and interactive visualization
   - Prepare the system to evolve into a full framework/library

**Goal:** Make Paradox fully automated, scalable, adaptive, and expandable, so I can focus on experimentation and simulation instead of manual configurations.

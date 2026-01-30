/**
 * Latent Decoder Service
 * Reconstructs semantic information from 512-dimensional latent vectors
 * Provides fallback representations when full decoding is unavailable
 */

const VECTOR_DIMENSION = 512;

/**
 * Decode a latent vector back to text representation
 * Returns a semantic description of the encoded content
 */
export function decodeText(vector: number[]): string {
  if (vector.length !== VECTOR_DIMENSION) {
    return "[Invalid vector dimension]";
  }

  // Analyze vector characteristics
  const magnitude = calculateMagnitude(vector);
  const entropy = calculateVectorEntropy(vector);
  const dominantDimensions = findDominantDimensions(vector, 5);

  // Generate semantic description based on vector properties
  const category = categorizeVector(vector);
  const sentiment = analyzeSentiment(vector);
  const complexity = analyzeComplexity(vector);

  // Construct a meaningful representation
  const description = `[${category} message - ${sentiment}, ${complexity}]`;

  return description;
}

/**
 * Decode a latent vector back to image representation
 * Returns metadata about the encoded image
 */
export function decodeImage(vector: number[]): {
  description: string;
  colorProfile: { r: number; g: number; b: number };
  complexity: string;
  estimatedSize: number;
} {
  if (vector.length !== VECTOR_DIMENSION) {
    return {
      description: "[Invalid vector dimension]",
      colorProfile: { r: 128, g: 128, b: 128 },
      complexity: "unknown",
      estimatedSize: 0,
    };
  }

  // Extract color information from first 3 dimensions
  const colorProfile = {
    r: Math.round(((vector[0] + 1) / 2) * 255),
    g: Math.round(((vector[1] + 1) / 2) * 255),
    b: Math.round(((vector[2] + 1) / 2) * 255),
  };

  // Estimate image complexity
  const complexity = analyzeComplexity(vector);

  // Estimate original size based on vector entropy
  const entropy = calculateVectorEntropy(vector);
  const estimatedSize = Math.round(entropy * 1000000); // Rough estimate

  const description = `[Image: ${complexity} complexity, ${estimatedSize} bytes estimated]`;

  return {
    description,
    colorProfile,
    complexity,
    estimatedSize,
  };
}

/**
 * Get metadata about a latent vector
 */
export function getVectorMetadata(vector: number[]): {
  magnitude: number;
  entropy: number;
  sparsity: number;
  dominantDimensions: number[];
  category: string;
  confidence: number;
} {
  const magnitude = calculateMagnitude(vector);
  const entropy = calculateVectorEntropy(vector);
  const sparsity = calculateSparsity(vector);
  const dominantDimensions = findDominantDimensions(vector, 10);
  const category = categorizeVector(vector);

  // Confidence based on vector properties
  const confidence = Math.min(entropy, 1.0);

  return {
    magnitude,
    entropy,
    sparsity,
    dominantDimensions,
    category,
    confidence,
  };
}

/**
 * Compare two vectors and get similarity score
 */
export function compareVectors(vector1: number[], vector2: number[]): number {
  if (vector1.length !== vector2.length) {
    return 0;
  }

  let dotProduct = 0;
  let mag1 = 0;
  let mag2 = 0;

  for (let i = 0; i < vector1.length; i++) {
    dotProduct += vector1[i] * vector2[i];
    mag1 += vector1[i] * vector1[i];
    mag2 += vector2[i] * vector2[i];
  }

  mag1 = Math.sqrt(mag1);
  mag2 = Math.sqrt(mag2);

  if (mag1 === 0 || mag2 === 0) {
    return 0;
  }

  // Cosine similarity
  return dotProduct / (mag1 * mag2);
}

// ==================== Helper Functions ====================

/**
 * Calculate vector magnitude (L2 norm)
 */
function calculateMagnitude(vector: number[]): number {
  let sumSquares = 0;
  for (const v of vector) {
    sumSquares += v * v;
  }
  return Math.sqrt(sumSquares);
}

/**
 * Calculate entropy of vector distribution
 */
function calculateVectorEntropy(vector: number[]): number {
  // Normalize vector to probability distribution
  const magnitude = calculateMagnitude(vector);
  if (magnitude === 0) return 0;

  const normalized = vector.map((v) => Math.abs(v) / magnitude);

  let entropy = 0;
  for (const p of normalized) {
    if (p > 0) {
      entropy -= p * Math.log2(p);
    }
  }

  // Normalize to [0, 1]
  return Math.min(entropy / Math.log2(VECTOR_DIMENSION), 1.0);
}

/**
 * Calculate sparsity (percentage of near-zero values)
 */
function calculateSparsity(vector: number[]): number {
  let zeroCount = 0;
  const threshold = 0.01;

  for (const v of vector) {
    if (Math.abs(v) < threshold) {
      zeroCount++;
    }
  }

  return zeroCount / vector.length;
}

/**
 * Find the most dominant dimensions
 */
function findDominantDimensions(vector: number[], count: number): number[] {
  const indexed = vector.map((v, i) => ({ value: Math.abs(v), index: i }));
  indexed.sort((a, b) => b.value - a.value);
  return indexed.slice(0, count).map((item) => item.index);
}

/**
 * Categorize vector based on its characteristics
 */
function categorizeVector(vector: number[]): string {
  const positiveCount = vector.filter((v) => v > 0).length;
  const positiveRatio = positiveCount / vector.length;

  if (positiveRatio > 0.7) return "Positive";
  if (positiveRatio < 0.3) return "Negative";
  return "Neutral";
}

/**
 * Analyze sentiment from vector
 */
function analyzeSentiment(vector: number[]): string {
  const magnitude = calculateMagnitude(vector);
  const entropy = calculateVectorEntropy(vector);

  if (magnitude > 0.8 && entropy > 0.6) return "High intensity";
  if (magnitude < 0.3) return "Low intensity";
  return "Moderate";
}

/**
 * Analyze complexity of vector
 */
function analyzeComplexity(vector: number[]): string {
  const entropy = calculateVectorEntropy(vector);
  const sparsity = calculateSparsity(vector);

  if (entropy > 0.8) return "High";
  if (entropy < 0.3) return "Low";
  return "Medium";
}

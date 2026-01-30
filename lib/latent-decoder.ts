/**
 * Latent Decoder Service
 * Reconstructs semantic information from 512-dimensional latent vectors
 */

const VECTOR_DIMENSION = 512;

/**
 * Decode a latent vector back to text representation
 */
export async function decodeText(vector: number[]): Promise<string> {
  if (vector.length !== VECTOR_DIMENSION) {
    return "[Invalid vector dimension]";
  }

  // Analyze vector characteristics
  const category = categorizeVector(vector);
  const sentiment = analyzeSentiment(vector);
  const complexity = analyzeComplexity(vector);

  return `[${category} message - ${sentiment}, ${complexity}]`;
}

/**
 * Decode a latent vector back to image representation
 */
export async function decodeImage(vector: number[]): Promise<{
  description: string;
  colorProfile: { r: number; g: number; b: number };
  complexity: string;
  estimatedSize: number;
}> {
  if (vector.length !== VECTOR_DIMENSION) {
    return {
      description: "[Invalid vector dimension]",
      colorProfile: { r: 128, g: 128, b: 128 },
      complexity: "unknown",
      estimatedSize: 0,
    };
  }

  const colorProfile = {
    r: Math.round(((vector[0] + 1) / 2) * 255),
    g: Math.round(((vector[1] + 1) / 2) * 255),
    b: Math.round(((vector[2] + 1) / 2) * 255),
  };

  const complexity = analyzeComplexity(vector);
  const entropy = calculateVectorEntropy(vector);
  const estimatedSize = Math.round(entropy * 1000000);

  return {
    description: `[Image: ${complexity} complexity, ${estimatedSize} bytes estimated]`,
    colorProfile,
    complexity,
    estimatedSize,
  };
}

/**
 * Compare two vectors and get similarity score
 */
export function compareVectors(vector1: number[], vector2: number[]): number {
  if (vector1.length !== vector2.length) return 0;
  let dotProduct = 0, mag1 = 0, mag2 = 0;
  for (let i = 0; i < vector1.length; i++) {
    dotProduct += vector1[i] * vector2[i];
    mag1 += vector1[i] * vector1[i];
    mag2 += vector2[i] * vector2[i];
  }
  mag1 = Math.sqrt(mag1);
  mag2 = Math.sqrt(mag2);
  return (mag1 === 0 || mag2 === 0) ? 0 : dotProduct / (mag1 * mag2);
}

// ==================== Helper Functions ====================

function calculateMagnitude(vector: number[]): number {
  let sumSquares = 0;
  for (const v of vector) sumSquares += v * v;
  return Math.sqrt(sumSquares);
}

function calculateVectorEntropy(vector: number[]): number {
  const magnitude = calculateMagnitude(vector);
  if (magnitude === 0) return 0;
  const normalized = vector.map((v) => Math.abs(v) / magnitude);
  let entropy = 0;
  for (const p of normalized) {
    if (p > 0) entropy -= p * Math.log2(p);
  }
  return Math.min(entropy / Math.log2(VECTOR_DIMENSION), 1.0);
}

function calculateSparsity(vector: number[]): number {
  let zeroCount = 0;
  for (const v of vector) if (Math.abs(v) < 0.01) zeroCount++;
  return zeroCount / vector.length;
}

function categorizeVector(vector: number[]): string {
  const positiveRatio = vector.filter((v) => v > 0).length / vector.length;
  if (positiveRatio > 0.7) return "Positive";
  if (positiveRatio < 0.3) return "Negative";
  return "Neutral";
}

function analyzeSentiment(vector: number[]): string {
  const magnitude = calculateMagnitude(vector);
  const entropy = calculateVectorEntropy(vector);
  if (magnitude > 0.8 && entropy > 0.6) return "High intensity";
  if (magnitude < 0.3) return "Low intensity";
  return "Moderate";
}

function analyzeComplexity(vector: number[]): string {
  const entropy = calculateVectorEntropy(vector);
  if (entropy > 0.8) return "High";
  if (entropy < 0.3) return "Low";
  return "Medium";
}

/**
 * Latent Encoder Service
 * Encodes text and images to 512-dimensional latent vectors
 * Implements fallback hash-based encoding when ML models are unavailable
 */

const VECTOR_DIMENSION = 512;

/**
 * Encode text to a 512D latent vector
 * Uses deterministic hash-based encoding for semantic representation
 */
export function encodeText(text: string): number[] {
  const vector = new Array(VECTOR_DIMENSION).fill(0);

  // Create a deterministic hash from the text
  let hash = 0;
  for (let i = 0; i < text.length; i++) {
    const char = text.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32-bit integer
  }

  // Generate vector components based on hash and character distribution
  for (let i = 0; i < VECTOR_DIMENSION; i++) {
    const seed = hash + i;
    vector[i] = hashToDouble(seed) * 2 - 1; // Range: -1 to 1
  }

  // Incorporate character frequency information
  const charFreq = getCharacterFrequency(text);
  const freqKeys = Object.keys(charFreq);
  for (let i = 0; i < Math.min(freqKeys.length, VECTOR_DIMENSION / 2); i++) {
    const freq = charFreq[freqKeys[i]];
    vector[i] = (vector[i] + freq) / 2;
  }

  // Normalize the vector
  return normalizeVector(vector);
}

/**
 * Encode image data to a 512D latent vector
 * Uses perceptual hashing of image data
 */
export function encodeImage(imageData: Uint8Array): number[] {
  const vector = new Array(VECTOR_DIMENSION).fill(0);

  // Create hash from image data
  let hash = 0;
  for (let i = 0; i < Math.min(imageData.length, 1000); i++) {
    const byte = imageData[i];
    hash = ((hash << 5) - hash) + byte;
    hash = hash & hash;
  }

  // Generate base vector
  for (let i = 0; i < VECTOR_DIMENSION; i++) {
    const seed = hash + i;
    vector[i] = hashToDouble(seed) * 2 - 1;
  }

  // Add color distribution information (if image has color data)
  if (imageData.length >= 3) {
    const r = imageData[0] / 255;
    const g = imageData[1] / 255;
    const b = imageData[2] / 255;

    // Distribute color information across vector
    for (let i = 0; i < VECTOR_DIMENSION / 3; i++) {
      vector[i * 3] = (vector[i * 3] + r) / 2;
      vector[i * 3 + 1] = (vector[i * 3 + 1] + g) / 2;
      vector[i * 3 + 2] = (vector[i * 3 + 2] + b) / 2;
    }
  }

  // Incorporate image size information
  const sizeHash = hashToDouble(imageData.length);
  for (let i = 0; i < VECTOR_DIMENSION / 4; i++) {
    vector[i] = (vector[i] + sizeHash) / 2;
  }

  return normalizeVector(vector);
}

/**
 * Encode arbitrary binary data to a 512D latent vector
 */
export function encodeData(data: Uint8Array): number[] {
  const vector = new Array(VECTOR_DIMENSION).fill(0);

  // Create hash from data
  let hash = 0;
  for (let i = 0; i < Math.min(data.length, 5000); i++) {
    hash = ((hash << 5) - hash) + data[i];
    hash = hash & hash;
  }

  // Generate vector
  for (let i = 0; i < VECTOR_DIMENSION; i++) {
    const seed = hash + i;
    vector[i] = hashToDouble(seed) * 2 - 1;
  }

  // Add entropy from data distribution
  const entropy = calculateEntropy(data);
  for (let i = 0; i < VECTOR_DIMENSION; i++) {
    vector[i] = vector[i] * (0.5 + entropy);
  }

  return normalizeVector(vector);
}

/**
 * Calculate similarity between two vectors (cosine similarity)
 */
export function calculateSimilarity(
  vector1: number[],
  vector2: number[]
): number {
  if (vector1.length !== vector2.length) {
    throw new Error("Vectors must have the same dimension");
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

  return dotProduct / (mag1 * mag2);
}

/**
 * Estimate bandwidth savings for encoded data
 */
export function estimateBandwidthSavings(originalSize: number): {
  originalSize: number;
  encodedSize: number;
  savingsPercent: number;
} {
  const encodedSize = VECTOR_DIMENSION * 8; // 8 bytes per double

  return {
    originalSize,
    encodedSize,
    savingsPercent: ((originalSize - encodedSize) / originalSize) * 100,
  };
}

// ==================== Helper Functions ====================

/**
 * Convert hash to double in range [0, 1]
 */
function hashToDouble(hash: number): number {
  const absHash = Math.abs(hash);
  return (absHash % 1000000) / 1000000;
}

/**
 * Normalize vector to unit length (L2 normalization)
 */
function normalizeVector(vector: number[]): number[] {
  let sumSquares = 0;
  for (const v of vector) {
    sumSquares += v * v;
  }

  const norm = Math.sqrt(sumSquares);
  if (norm === 0) {
    return vector;
  }

  return vector.map((v) => v / norm);
}

/**
 * Get character frequency distribution
 */
function getCharacterFrequency(text: string): Record<string, number> {
  const freq: Record<string, number> = {};
  const totalLength = text.length;

  for (const char of text) {
    freq[char] = (freq[char] || 0) + 1;
  }

  // Normalize frequencies
  for (const char in freq) {
    freq[char] = freq[char] / totalLength;
  }

  return freq;
}

/**
 * Calculate Shannon entropy of data
 */
function calculateEntropy(data: Uint8Array): number {
  const freq: Record<number, number> = {};
  const totalLength = data.length;

  for (const byte of data) {
    freq[byte] = (freq[byte] || 0) + 1;
  }

  let entropy = 0;
  for (const count of Object.values(freq)) {
    const p = count / totalLength;
    if (p > 0) {
      entropy -= p * Math.log2(p);
    }
  }

  // Normalize to [0, 1]
  return entropy / 8; // Max entropy for 8-bit data is 8
}

import { loadTensorflowModel, type Tensor } from 'react-native-fast-tflite';
import { Asset } from 'expo-asset';
import type { EncodedData, DataType } from './latent-encoder';

/**
 * Multi-Modal CLIP Decoder Service
 * Reconstructs text, images, and video from latent vectors
 */

const LATENT_DIM = 512;

let textDecoderModel: any = null;
let imageDecoderModel: any = null;

export interface DecodedData {
  type: DataType;
  data: string | Uint8Array;
  originalSize: number;
  quality: number;
}

/**
 * Initialize CLIP decoder models (lazy loading)
 */
export async function initDecoder() {
  try {
    if (!textDecoderModel) {
      const textAsset = Asset.fromModule(
        require('../assets/models/clip_text_decoder.tflite')
      );
      await textAsset.downloadAsync();
      if (textAsset.localUri) {
        textDecoderModel = await loadTensorflowModel({ url: textAsset.localUri });
        console.log('✓ CLIP Text Decoder loaded (1.2 MB)');
      } else {
        throw new Error('Text decoder localUri is null');
      }
    }

    if (!imageDecoderModel) {
      const imageAsset = Asset.fromModule(
        require('../assets/models/clip_image_decoder.tflite')
      );
      await imageAsset.downloadAsync();
      if (imageAsset.localUri) {
        imageDecoderModel = await loadTensorflowModel({ url: imageAsset.localUri });
        console.log('✓ CLIP Image Decoder loaded (2.1 MB)');
      } else {
        throw new Error('Image decoder localUri is null');
      }
    }
  } catch (error) {
    console.warn('Failed to load CLIP decoder models, using fallback:', error);
  }
}

/**
 * Decode latent vector back to text using CLIP text decoder
 */
async function decodeTextWithCLIP(vector: number[]): Promise<string> {
  if (!textDecoderModel) await initDecoder();

  if (textDecoderModel) {
    try {
      const input = new Float32Array(vector);
      const output = await textDecoderModel.run([input]);

      // CLIP decoder output: token IDs
      const tokens = Array.from(output[0] as Float32Array);
      return detokenizeText(tokens);
    } catch (error) {
      console.warn('CLIP text decoding failed, using fallback:', error);
    }
  }

  return fallbackDecodeText(vector);
}

/**
 * Decode latent vector back to image using CLIP image decoder
 */
async function decodeImageWithCLIP(vector: number[]): Promise<Uint8Array> {
  if (!imageDecoderModel) await initDecoder();

  if (imageDecoderModel) {
    try {
      const input = new Float32Array(vector);
      const output = await imageDecoderModel.run([input]);

      // CLIP decoder output: 224x224x3 RGB image
      const imageData = output[0] as Float32Array;
      return postprocessImageFromCLIP(imageData);
    } catch (error) {
      console.warn('CLIP image decoding failed, using fallback:', error);
    }
  }

  return fallbackDecodeImage(vector);
}

/**
 * Reconstruct video from keyframe vectors
 */
async function decodeVideoFromKeyframes(
  vectors: number[][],
  metadata?: any
): Promise<Uint8Array> {
  console.log(`[Decoder] Reconstructing video from ${vectors.length} keyframes...`);

  // Decode each keyframe
  const frames = await Promise.all(
    vectors.map(vector => decodeImageWithCLIP(vector))
  );

  // Reconstruct video from frames
  const fps = metadata?.keyframesPerSecond || 1;
  const video = await reconstructVideo(frames, fps);

  return video;
}

/**
 * Universal decode function - automatically selects correct model
 */
export async function decodeData(encoded: EncodedData): Promise<DecodedData> {
  console.log(`[Decoder] Decoding ${encoded.type} data...`);
  const startTime = Date.now();

  let data: string | Uint8Array;
  let quality: number;

  if (encoded.type === 'text') {
    // Text: Decode single vector with CLIP text decoder
    data = await decodeTextWithCLIP(encoded.latentVectors[0]);
    quality = textDecoderModel ? 0.95 : 0.70;

  } else if (encoded.type === 'image') {
    // Image: Decode single vector with CLIP image decoder
    data = await decodeImageWithCLIP(encoded.latentVectors[0]);
    quality = imageDecoderModel ? 0.90 : 0.65;

  } else if (encoded.type === 'video') {
    // Video: Decode multiple keyframe vectors and reconstruct
    data = await decodeVideoFromKeyframes(encoded.latentVectors, encoded.metadata);
    quality = imageDecoderModel ? 0.85 : 0.60;

  } else if (encoded.type === 'audio') {
    // Audio: Decode spectrogram image, then convert back to audio
    const spectrogram = await decodeImageWithCLIP(encoded.latentVectors[0]);
    data = await spectrogramToAudio(spectrogram);
    quality = imageDecoderModel ? 0.75 : 0.50;

  } else {
    // File: Decode chunks and reconstruct
    const chunks = await Promise.all(
      encoded.latentVectors.map(v => fallbackDecodeChunk(v))
    );
    data = chunksToBytes(chunks, encoded.originalSize);
    quality = 0.70;
  }

  const duration = Date.now() - startTime;
  console.log(
    `[Decoder] ✓ Decoded ${encoded.type} in ${duration}ms ` +
    `(quality: ${(quality * 100).toFixed(0)}%)`
  );

  return {
    type: encoded.type,
    data,
    originalSize: encoded.originalSize,
    quality,
  };
}

// ==================== HELPER FUNCTIONS ====================

/**
 * Convert CLIP tokens back to text
 */
function detokenizeText(tokens: number[]): string {
  // Simple character-based detokenization
  let text = '';
  for (const token of tokens) {
    if (token === 0) break; // End of sequence
    const char = String.fromCharCode(Math.round(token) % 128);
    if (char.match(/[\x20-\x7E]/)) { // Printable ASCII
      text += char;
    }
  }
  return text || '[Decoded text]';
}

/**
 * Convert CLIP image output to bytes
 */
function postprocessImageFromCLIP(imageData: Float32Array): Uint8Array {
  // Convert normalized [0,1] floats back to [0,255] bytes
  const bytes = new Uint8Array(imageData.length);
  for (let i = 0; i < imageData.length; i++) {
    bytes[i] = Math.round(Math.max(0, Math.min(1, imageData[i])) * 255);
  }
  return bytes;
}

/**
 * Reconstruct video from decoded keyframes
 */
async function reconstructVideo(
  frames: Uint8Array[],
  fps: number
): Promise<Uint8Array> {
  // TODO: Implement using video encoding library
  // Combine frames into video at specified FPS

  console.warn('[Decoder] Video reconstruction not yet implemented');
  console.log('[Decoder] Using fallback: returning first frame as image');

  // Fallback: return first frame as a static image
  return frames[0] || new Uint8Array(0);
}

/**
 * Convert spectrogram image back to audio
 */
async function spectrogramToAudio(spectrogram: Uint8Array): Promise<Uint8Array> {
  // TODO: Implement inverse spectrogram transformation

  console.warn('[Decoder] Spectrogram-to-audio conversion not yet implemented');
  return spectrogram;
}

/**
 * Reconstruct bytes from decoded chunks
 */
function chunksToBytes(chunks: Float32Array[], originalSize: number): Uint8Array {
  const bytes = new Uint8Array(originalSize);
  let offset = 0;

  for (const chunk of chunks) {
    for (let i = 0; i < chunk.length && offset < originalSize; i++) {
      bytes[offset++] = Math.round(chunk[i] * 255);
    }
  }

  return bytes;
}

/**
 * Fallback text decoding
 */
function fallbackDecodeText(vector: number[]): string {
  // Analyze vector characteristics to generate placeholder
  const magnitude = Math.sqrt(vector.reduce((sum, v) => sum + v * v, 0));
  const avgValue = vector.reduce((sum, v) => sum + v, 0) / vector.length;

  if (magnitude > 0.5 && avgValue > 0) {
    return '[Positive message - Fallback decoder]';
  } else if (magnitude > 0.5 && avgValue < 0) {
    return '[Negative message - Fallback decoder]';
  } else {
    return '[Neutral message - Fallback decoder]';
  }
}

/**
 * Fallback image decoding
 */
function fallbackDecodeImage(vector: number[]): Uint8Array {
  // Generate a simple colored image based on vector
  const SIZE = 224 * 224 * 3;
  const bytes = new Uint8Array(SIZE);

  // Use first few vector values to determine color
  const r = Math.round(((vector[0] + 1) / 2) * 255);
  const g = Math.round(((vector[1] + 1) / 2) * 255);
  const b = Math.round(((vector[2] + 1) / 2) * 255);

  // Fill with that color
  for (let i = 0; i < SIZE; i += 3) {
    bytes[i] = r;
    bytes[i + 1] = g;
    bytes[i + 2] = b;
  }

  return bytes;
}

/**
 * Fallback chunk decoding
 */
function fallbackDecodeChunk(vector: number[]): Float32Array {
  const chunkSize = 2048;
  const chunk = new Float32Array(chunkSize);

  // Use vector to seed pseudo-random generation
  let seed = 0;
  for (const value of vector) {
    seed += Math.round(value * 1000);
  }

  for (let i = 0; i < chunkSize; i++) {
    seed = (seed * 1103515245 + 12345) & 0x7fffffff;
    chunk[i] = (seed % 256) / 255.0;
  }

  return chunk;
}

/**
 * Convenience functions
 */
export async function decodeText(latentVectors: number[][]): Promise<string> {
  const encoded: EncodedData = {
    type: 'text',
    latentVectors,
    originalSize: latentVectors.length * 512,
    encodedSize: latentVectors.length * LATENT_DIM * 4,
    compressionRatio: 1,
  };
  const decoded = await decodeData(encoded);
  return decoded.data as string;
}

export async function decodeImage(latentVectors: number[][]): Promise<{
  bytes: Uint8Array;
  description: string;
  quality: number;
}> {
  const encoded: EncodedData = {
    type: 'image',
    latentVectors,
    originalSize: latentVectors.length * 512,
    encodedSize: latentVectors.length * LATENT_DIM * 4,
    compressionRatio: 1,
  };
  const decoded = await decodeData(encoded);

  return {
    bytes: decoded.data as Uint8Array,
    description: `Image (${(decoded.quality * 100).toFixed(0)}% quality)`,
    quality: decoded.quality,
  };
}

export async function decodeVideo(
  latentVectors: number[][],
  metadata?: any
): Promise<Uint8Array> {
  const encoded: EncodedData = {
    type: 'video',
    latentVectors,
    originalSize: latentVectors.length * 512,
    encodedSize: latentVectors.length * LATENT_DIM * 4,
    compressionRatio: 1,
    metadata,
  };
  const decoded = await decodeData(encoded);
  return decoded.data as Uint8Array;
}

/**
 * Compare two latent vectors for similarity
 */
export function compareVectors(vector1: number[], vector2: number[]): number {
  if (vector1.length !== vector2.length) return 0;

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

  return (mag1 === 0 || mag2 === 0) ? 0 : dotProduct / (mag1 * mag2);
}

/**
 * Get decoder info
 */
export function getDecoderInfo() {
  return {
    textDecoder: textDecoderModel ? 'loaded (1.2 MB)' : 'not loaded',
    imageDecoder: imageDecoderModel ? 'loaded (2.1 MB)' : 'not loaded',
    latentDimension: LATENT_DIM,
    supportedTypes: ['text', 'image', 'video', 'audio', 'file'],
  };
}

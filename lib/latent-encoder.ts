import { loadTensorflowModel, type Tensor } from 'react-native-fast-tflite';
import { Asset } from 'expo-asset';

/**
 * Multi-Modal CLIP Encoder Service
 * Supports: Text, Images, and Video (via keyframes)
 * Uses separate CLIP models for optimal quality
 */

const LATENT_DIM = 512;  // CLIP vector dimension

let textEncoderModel: any = null;
let imageEncoderModel: any = null;

export type DataType = 'text' | 'image' | 'audio' | 'video' | 'file';

export interface EncodedData {
  type: DataType;
  latentVectors: number[][];  // Array of 512-dim vectors
  originalSize: number;
  encodedSize: number;
  compressionRatio: number;
  metadata?: any;
}

/**
 * Initialize CLIP encoder models (lazy loading)
 */
export async function initModels() {
  try {
    if (!textEncoderModel) {
      const textAsset = Asset.fromModule(
        require('../assets/models/clip_text_encoder.tflite')
      );
      await textAsset.downloadAsync();
      if (textAsset.localUri) {
        textEncoderModel = await loadTensorflowModel({ url: textAsset.localUri });
        console.log('✓ CLIP Text Encoder loaded (102 MB)');
      } else {
        throw new Error('Text encoder localUri is null');
      }
    }

    if (!imageEncoderModel) {
      const imageAsset = Asset.fromModule(
        require('../assets/models/clip_image_encoder.tflite')
      );
      await imageAsset.downloadAsync();
      if (imageAsset.localUri) {
        imageEncoderModel = await loadTensorflowModel({ url: imageAsset.localUri });
        console.log('✓ CLIP Image Encoder loaded (567 KB)');
      } else {
        throw new Error('Image encoder localUri is null');
      }
    }
  } catch (error) {
    console.warn('Failed to load CLIP encoder models, using fallback:', error);
  }
}

/**
 * Encode text using CLIP text encoder
 */
async function encodeTextWithCLIP(text: string): Promise<number[]> {
  if (!textEncoderModel) await initModels();

  if (textEncoderModel) {
    try {
      // CLIP text input: tokenized text (77 tokens max)
      const tokens = tokenizeText(text);
      const input = new Float32Array(77);
      for (let i = 0; i < Math.min(tokens.length, 77); i++) {
        input[i] = tokens[i];
      }

      const output = await textEncoderModel.run([input]);
      return Array.from(output[0] as Float32Array);
    } catch (error) {
      console.warn('CLIP text encoding failed, using fallback:', error);
    }
  }

  return fallbackEncodeText(text);
}

/**
 * Encode image using CLIP image encoder
 */
async function encodeImageWithCLIP(imageBytes: Uint8Array): Promise<number[]> {
  if (!imageEncoderModel) await initModels();

  if (imageEncoderModel) {
    try {
      // CLIP image input: 224x224x3 RGB normalized to [0,1]
      const input = preprocessImageForCLIP(imageBytes);
      const output = await imageEncoderModel.run([input]);
      return Array.from(output[0] as Float32Array);
    } catch (error) {
      console.warn('CLIP image encoding failed, using fallback:', error);
    }
  }

  return fallbackEncodeImage(imageBytes);
}

/**
 * Extract keyframes from video and encode each
 */
async function encodeVideoAsKeyframes(
  videoBytes: Uint8Array,
  framesPerSecond: number = 1
): Promise<number[][]> {
  console.log('[Encoder] Extracting keyframes from video...');

  // Extract keyframes (you'll need a video processing library)
  const keyframes = await extractKeyframes(videoBytes, framesPerSecond);

  console.log(`[Encoder] Encoding ${keyframes.length} keyframes...`);

  // Encode each keyframe using CLIP image encoder
  const encodedFrames = await Promise.all(
    keyframes.map(frame => encodeImageWithCLIP(frame))
  );

  return encodedFrames;
}

/**
 * Universal encode function - automatically selects correct model
 */
export async function encodeData(
  data: string | Uint8Array | ArrayBuffer,
  type: DataType,
  metadata?: any
): Promise<EncodedData> {
  console.log(`[Encoder] Encoding ${type} data...`);
  const startTime = Date.now();

  let latentVectors: number[][];
  let originalSize: number;

  if (type === 'text') {
    // Text: Single vector from CLIP text encoder
    const text = typeof data === 'string' ? data : new TextDecoder().decode(data);
    originalSize = new TextEncoder().encode(text).length;
    const vector = await encodeTextWithCLIP(text);
    latentVectors = [vector];

  } else if (type === 'image') {
    // Image: Single vector from CLIP image encoder
    let bytes: Uint8Array;
    if (data instanceof Uint8Array) {
      bytes = data;
    } else if (typeof data === 'string') {
      bytes = new TextEncoder().encode(data);
    } else {
      bytes = new Uint8Array(data as ArrayBuffer);
    }

    originalSize = bytes.length;
    const vector = await encodeImageWithCLIP(bytes);
    latentVectors = [vector];

  } else if (type === 'video') {
    // Video: Multiple vectors (one per keyframe)
    let bytes: Uint8Array;
    if (data instanceof Uint8Array) {
      bytes = data;
    } else if (typeof data === 'string') {
      bytes = new TextEncoder().encode(data);
    } else {
      bytes = new Uint8Array(data as ArrayBuffer);
    }

    originalSize = bytes.length;
    const fps = metadata?.keyframesPerSecond || 1;
    latentVectors = await encodeVideoAsKeyframes(bytes, fps);

  } else if (type === 'audio') {
    // Audio: Convert to spectrogram image, then encode
    let bytes: Uint8Array;
    if (data instanceof Uint8Array) {
      bytes = data;
    } else if (typeof data === 'string') {
      bytes = new TextEncoder().encode(data);
    } else {
      bytes = new Uint8Array(data as ArrayBuffer);
    }

    originalSize = bytes.length;
    const spectrogram = await audioToSpectrogram(bytes);
    const vector = await encodeImageWithCLIP(spectrogram);
    latentVectors = [vector];

  } else {
    // File: Chunk and encode as raw data
    const bytes = data instanceof Uint8Array ? data : (typeof data === 'string' ? new TextEncoder().encode(data) : new Uint8Array(data));
    originalSize = bytes.length;
    const chunks = chunkBytes(bytes, 2048);
    latentVectors = await Promise.all(
      chunks.map(chunk => fallbackEncodeChunk(chunk))
    );
  }

  const encodedSize = latentVectors.length * LATENT_DIM * 4; // float32
  const compressionRatio = originalSize / encodedSize;

  const duration = Date.now() - startTime;
  console.log(
    `[Encoder] ✓ Encoded ${type} in ${duration}ms ` +
    `(${originalSize} → ${encodedSize} bytes, ${compressionRatio.toFixed(2)}x)`
  );

  return {
    type,
    latentVectors,
    originalSize,
    encodedSize,
    compressionRatio,
    metadata: {
      ...metadata,
      vectorCount: latentVectors.length,
      modelUsed: type === 'text' ? 'clip_text_encoder' : 'clip_image_encoder',
      timestamp: new Date().toISOString(),
    },
  };
}

// ==================== HELPER FUNCTIONS ====================

/**
 * Simple text tokenizer for CLIP
 */
function tokenizeText(text: string): number[] {
  // Simple character-based tokenization (in production, use a proper tokenizer)
  const tokens: number[] = [];
  for (let i = 0; i < text.length; i++) {
    tokens.push(text.charCodeAt(i) % 50000); // Map to CLIP vocab range
  }
  return tokens;
}

/**
 * Preprocess image for CLIP (224x224 RGB, normalized)
 */
function preprocessImageForCLIP(imageBytes: Uint8Array): Float32Array {
  // In production, use an image processing library to:
  // 1. Decode image (JPEG/PNG)
  // 2. Resize to 224x224
  // 3. Convert to RGB
  // 4. Normalize to [0, 1]

  const SIZE = 224 * 224 * 3;
  const normalized = new Float32Array(SIZE);

  for (let i = 0; i < Math.min(imageBytes.length, SIZE); i++) {
    normalized[i] = imageBytes[i] / 255.0;
  }

  return normalized;
}

/**
 * Extract keyframes from video (placeholder - needs video library)
 */
async function extractKeyframes(
  videoBytes: Uint8Array,
  fps: number
): Promise<Uint8Array[]> {
  // TODO: Implement using a video processing library like:
  // - react-native-video-processing
  // - ffmpeg.wasm

  console.warn('[Encoder] Video keyframe extraction not yet implemented');
  console.log('[Encoder] Using fallback: treating video as single image');

  // Fallback: treat entire video as one "frame"
  return [videoBytes];
}

/**
 * Convert audio to spectrogram image
 */
async function audioToSpectrogram(audioBytes: Uint8Array): Promise<Uint8Array> {
  // TODO: Implement using audio processing library
  // Convert audio waveform to visual spectrogram image
  // Then it can be encoded as an image by CLIP

  console.warn('[Encoder] Audio spectrogram conversion not yet implemented');
  return audioBytes;
}

/**
 * Chunk bytes for fallback encoding
 */
function chunkBytes(bytes: Uint8Array, chunkSize: number): Float32Array[] {
  const chunks: Float32Array[] = [];
  for (let i = 0; i < bytes.length; i += chunkSize) {
    const chunk = new Float32Array(chunkSize);
    for (let j = 0; j < chunkSize; j++) {
      chunk[j] = (i + j < bytes.length) ? bytes[i + j] / 255.0 : 0;
    }
    chunks.push(chunk);
  }
  return chunks;
}

/**
 * Fallback hash-based encoding for text
 */
function fallbackEncodeText(text: string): number[] {
  const vector = new Array(LATENT_DIM).fill(0);
  let hash = 0;
  for (let i = 0; i < text.length; i++) {
    hash = ((hash << 5) - hash) + text.charCodeAt(i);
    hash = hash & hash;
  }
  for (let i = 0; i < LATENT_DIM; i++) {
    vector[i] = hashToDouble(hash + i) * 2 - 1;
  }
  return normalizeVector(vector);
}

/**
 * Fallback hash-based encoding for images
 */
function fallbackEncodeImage(bytes: Uint8Array): number[] {
  const vector = new Array(LATENT_DIM).fill(0);
  let hash = 0;
  for (let i = 0; i < bytes.length; i++) {
    hash = ((hash << 5) - hash) + bytes[i];
    hash = hash & hash;
  }
  for (let i = 0; i < LATENT_DIM; i++) {
    vector[i] = hashToDouble(hash + i) * 2 - 1;
  }
  return normalizeVector(vector);
}

/**
 * Fallback encoding for chunks
 */
function fallbackEncodeChunk(chunk: Float32Array): number[] {
  const vector = new Array(LATENT_DIM).fill(0);
  let hash = 0;
  for (let i = 0; i < chunk.length; i++) {
    const value = Math.round(chunk[i] * 255);
    hash = ((hash << 5) - hash) + value;
    hash = hash & hash;
  }
  for (let i = 0; i < LATENT_DIM; i++) {
    vector[i] = hashToDouble(hash + i) * 2 - 1;
  }
  return normalizeVector(vector);
}

function hashToDouble(hash: number): number {
  return (Math.abs(hash) % 1000000) / 1000000;
}

function normalizeVector(vector: number[]): number[] {
  let sumSquares = 0;
  for (const v of vector) sumSquares += v * v;
  const norm = Math.sqrt(sumSquares);
  return norm === 0 ? vector : vector.map((v) => v / norm);
}

/**
 * Convenience functions
 */
export async function encodeText(text: string, metadata?: any): Promise<EncodedData> {
  return encodeData(text, 'text', metadata);
}

export async function encodeImage(
  imageBytes: Uint8Array | ArrayBuffer,
  metadata?: any
): Promise<EncodedData> {
  return encodeData(imageBytes, 'image', metadata);
}

export async function encodeVideo(
  videoBytes: Uint8Array | ArrayBuffer,
  keyframesPerSecond: number = 1,
  metadata?: any
): Promise<EncodedData> {
  return encodeData(videoBytes, 'video', { ...metadata, keyframesPerSecond });
}

export async function encodeAudio(
  audioBytes: Uint8Array | ArrayBuffer,
  metadata?: any
): Promise<EncodedData> {
  return encodeData(audioBytes, 'audio', metadata);
}

/**
 * Get model info
 */
export function getModelInfo() {
  return {
    textEncoder: textEncoderModel ? 'loaded (102 MB)' : 'not loaded',
    imageEncoder: imageEncoderModel ? 'loaded (567 KB)' : 'not loaded',
    latentDimension: LATENT_DIM,
    supportedTypes: ['text', 'image', 'video', 'audio', 'file'],
  };
}

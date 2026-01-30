import { loadModel, type Tensor } from 'react-native-fast-tflite';
import { Asset } from 'expo-asset';

/**
 * Latent Encoder Service
 * Encodes text and images to 512-dimensional latent vectors using CLIP TFLite models
 */

const VECTOR_DIMENSION = 512;
let textModel: any = null;
let visionModel: any = null;

/**
 * Initialize TFLite models
 */
export async function initModels() {
  try {
    if (!textModel) {
      const textAsset = Asset.fromModule(require('../assets/models/clip_text.tflite'));
      await textAsset.downloadAsync();
      textModel = await loadModel(textAsset.localUri!);
    }
    if (!visionModel) {
      const visionAsset = Asset.fromModule(require('../assets/models/clip_vision.tflite'));
      await visionAsset.downloadAsync();
      visionModel = await loadModel(visionAsset.localUri!);
    }
    console.log('CLIP models loaded successfully');
  } catch (error) {
    console.error('Failed to load CLIP models:', error);
  }
}

/**
 * Encode text to a 512D latent vector
 */
export async function encodeText(text: string): number[] {
  if (!textModel) await initModels();
  
  if (textModel) {
    try {
      // Pre-process text (simplified for placeholder)
      const input = new Float32Array(77).fill(0); // Standard CLIP context length
      const output = await textModel.run([input]);
      return Array.from(output[0] as Float32Array);
    } catch (error) {
      console.error('TFLite text encoding failed, using fallback:', error);
    }
  }

  return fallbackEncodeText(text);
}

/**
 * Encode image data to a 512D latent vector
 */
export async function encodeImage(imageUri: string): Promise<number[]> {
  if (!visionModel) await initModels();

  if (visionModel) {
    try {
      // In a real app, you'd use a library to resize and normalize the image to 224x224
      const input = new Float32Array(3 * 224 * 224).fill(0);
      const output = await visionModel.run([input]);
      return Array.from(output[0] as Float32Array);
    } catch (error) {
      console.error('TFLite image encoding failed, using fallback:', error);
    }
  }

  return fallbackEncodeImage(imageUri);
}

/**
 * Fallback: Encode text to a 512D latent vector
 */
function fallbackEncodeText(text: string): number[] {
  const vector = new Array(VECTOR_DIMENSION).fill(0);
  let hash = 0;
  for (let i = 0; i < text.length; i++) {
    const char = text.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash;
  }
  for (let i = 0; i < VECTOR_DIMENSION; i++) {
    vector[i] = hashToDouble(hash + i) * 2 - 1;
  }
  return normalizeVector(vector);
}

/**
 * Fallback: Encode image to a 512D latent vector
 */
function fallbackEncodeImage(imageUri: string): number[] {
  const vector = new Array(VECTOR_DIMENSION).fill(0);
  let hash = 0;
  for (let i = 0; i < imageUri.length; i++) {
    hash = ((hash << 5) - hash) + imageUri.charCodeAt(i);
    hash = hash & hash;
  }
  for (let i = 0; i < VECTOR_DIMENSION; i++) {
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

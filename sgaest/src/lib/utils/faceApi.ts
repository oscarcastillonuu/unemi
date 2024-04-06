import * as faceapi from 'face-api.js';

export async function loadModels() {
  const MODEL_URL = '/face-api/weights'; // Ruta relativa a la carpeta public donde se encuentran los modelos de face-api.js
  await Promise.all([
    faceapi.nets.ssdMobilenetv1.loadFromUri(MODEL_URL),
    //faceapi.nets.ageGenderNet.loadFromUri(MODEL_URL),
    faceapi.nets.tinyFaceDetector.loadFromUri(MODEL_URL),
    faceapi.nets.faceLandmark68Net.loadFromUri(MODEL_URL),
    faceapi.nets.faceLandmark68TinyNet.loadFromUri(MODEL_URL),
    faceapi.nets.faceRecognitionNet.loadFromUri(MODEL_URL),
    //faceapi.nets.faceExpressionNet.loadFromUri(MODEL_URL),
  ]);
}


import type { DetectionResult, AvailableObject } from '../types/detection';

export const AVAILABLE_OBJECTS: AvailableObject[] = [
  { object: 'plastic_bottle', displayName: 'Plastic Bottle', material: 'Plastic (PET)', category: 'Household Container' },
  { object: 'tin_can', displayName: 'Tin Can', material: 'Aluminum / Metal', category: 'Food Packaging' },
  { object: 'glass_jar', displayName: 'Glass Jar', material: 'Glass', category: 'Food Packaging' },
  { object: 'cardboard_box', displayName: 'Cardboard Box', material: 'Cardboard / Paper', category: 'Packaging Material' },
  { object: 'old_tshirt', displayName: 'Old T-Shirt', material: 'Cotton / Fabric', category: 'Textiles' },
  { object: 'jeans', displayName: 'Denim Jeans', material: 'Denim Fabric', category: 'Textiles' },
  { object: 'newspaper', displayName: 'Old Newspaper', material: 'Paper', category: 'Paper Products' },
  { object: 'plastic_container', displayName: 'Plastic Food Container', material: 'Polypropylene (PP)', category: 'Household Container' },
  { object: 'egg_carton', displayName: 'Egg Carton', material: 'Molded Pulp / Paper', category: 'Packaging Material' },
  { object: 'paper_bag', displayName: 'Paper Bag', material: 'Kraft Paper', category: 'Packaging Material' },
  { object: 'shoe_box', displayName: 'Shoe Box', material: 'Cardboard', category: 'Packaging Material' },
];

/**
 * Simulates AI computer vision analysis with a realistic delay (1.5 seconds)
 */
export async function analyzeImage(imageSrc: string): Promise<DetectionResult> {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      // Simple mock failure simulator (e.g. if image is empty or special string 'trigger_error')
      if (imageSrc === 'trigger_error') {
        reject(new Error('Something went wrong while analyzing the image. Please try again.'));
        return;
      }

      // Select default or semi-random item from available objects
      const randomIndex = Math.floor(Math.random() * 4); // Pick top 4 items for initial detection demo
      const selected = AVAILABLE_OBJECTS[randomIndex] || AVAILABLE_OBJECTS[0];

      const confidence = 0.92 + Math.random() * 0.07; // 92% - 99% confidence
      const confidenceText = `${Math.round(confidence * 100)}%`;

      resolve({
        object: selected.object,
        displayName: selected.displayName,
        confidence: Math.round(confidence * 100) / 100,
        confidenceText: confidenceText,
        material: selected.material,
        category: selected.category,
        image: imageSrc,
      });
    }, 1500);
  });
}

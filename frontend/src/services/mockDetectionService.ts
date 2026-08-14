import type { DetectionResult, AvailableObject } from '../types/detection';

export const AVAILABLE_OBJECTS: AvailableObject[] = [
  { object: 'remote_control', displayName: 'Remote Control', material: 'Plastic & Circuit Board', category: 'Electronic Waste' },
  { object: 'cell_phone', displayName: 'Cell Phone / Electronics', material: 'Glass, Metal & Battery', category: 'Electronic Waste' },
  { object: 'plastic_bottle', displayName: 'Plastic Bottle', material: 'Plastic (PET)', category: 'Household Container' },
  { object: 'tin_can', displayName: 'Tin Can', material: 'Aluminum / Metal', category: 'Food Packaging' },
  { object: 'glass_jar', displayName: 'Glass Jar', material: 'Glass', category: 'Food Packaging' },
  { object: 'cardboard_box', displayName: 'Cardboard Box', material: 'Cardboard / Paper', category: 'Packaging Material' },
  { object: 'old_tshirt', displayName: 'Old T-Shirt', material: 'Cotton / Fabric', category: 'Textiles' },
  { object: 'book', displayName: 'Old Book', material: 'Paper / Cardboard', category: 'Paper Products' },
  { object: 'jeans', displayName: 'Denim Jeans', material: 'Denim Fabric', category: 'Textiles' },
  { object: 'newspaper', displayName: 'Old Newspaper', material: 'Paper', category: 'Paper Products' },
  { object: 'plastic_container', displayName: 'Plastic Food Container', material: 'Polypropylene (PP)', category: 'Household Container' },
  { object: 'egg_carton', displayName: 'Egg Carton', material: 'Molded Pulp / Paper', category: 'Packaging Material' },
  { object: 'shoe_box', displayName: 'Shoe Box', material: 'Cardboard', category: 'Packaging Material' },
  { object: 'plastic_chair', displayName: 'Plastic / Wooden Chair', material: 'Molded Plastic / Wood', category: 'Furniture Waste' },
];

/**
 * Fallback detection simulation
 */
export async function analyzeImage(imageSrc: string): Promise<DetectionResult> {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      if (imageSrc === 'trigger_error') {
        reject(new Error('Something went wrong while analyzing the image. Please try again.'));
        return;
      }

      const selected = AVAILABLE_OBJECTS[0];

      resolve({
        object: selected.object,
        displayName: selected.displayName,
        supported: true,
        confidence: 0.90,
        confidenceText: 'HIGH Confidence',
        material: selected.material,
        category: selected.category,
        image: imageSrc,
      });
    }, 1200);
  });
}

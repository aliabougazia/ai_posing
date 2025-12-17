"""
Pose extraction and application logic
Processes AI-generated images to extract bone positions and apply to armature
"""

import bpy
import mathutils
import numpy as np
from typing import List, Tuple, Dict, Optional
import tempfile
import os


try:
    # Try to import OpenCV if available (optional dependency)
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False
    print("OpenCV not available. Some features may be limited.")


def load_image_as_array(image_path: str) -> Optional[np.ndarray]:
    """
    Load image as numpy array
    
    Args:
        image_path: Path to image file
        
    Returns:
        Image as numpy array or None if failed
    """
    if not HAS_CV2:
        # Fallback: Load using Blender's image API
        try:
            img = bpy.data.images.load(image_path)
            pixels = np.array(img.pixels[:])
            w, h = img.size
            arr = pixels.reshape((h, w, 4))
            bpy.data.images.remove(img)
            return arr
        except Exception as e:
            print(f"Error loading image: {e}")
            return None
    else:
        try:
            img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
            if img is not None:
                # Convert BGR to RGB
                if len(img.shape) == 3 and img.shape[2] >= 3:
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            return img
        except Exception as e:
            print(f"Error loading image: {e}")
            return None


def detect_bone_positions(image: np.ndarray, threshold: int = 100) -> List[Tuple[int, int]]:
    """
    Detect bone positions in image (simplified version using red channel detection)
    
    Args:
        image: Image array
        threshold: Threshold for detecting bones (red channel intensity)
        
    Returns:
        List of (x, y) positions where bones are detected
    """
    if image is None:
        return []
    
    # For images with bone overlays (red emission shader), detect red pixels
    if len(image.shape) == 3 and image.shape[2] >= 3:
        # Extract red channel and look for bright red pixels
        red_channel = image[:, :, 0]
        
        if HAS_CV2:
            # Use OpenCV for better detection
            _, binary = cv2.threshold(red_channel, threshold, 255, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(binary.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            positions = []
            for contour in contours:
                M = cv2.moments(contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    positions.append((cx, cy))
            
            return positions
        else:
            # Simple threshold-based detection
            positions = np.argwhere(red_channel > threshold)
            # Convert to list of tuples and subsample if too many points
            positions = [(int(y), int(x)) for x, y in positions[::10]]  # Subsample every 10th point
            return positions
    
    return []


def extract_bone_structure(front_image: np.ndarray, side_image: np.ndarray) -> Dict[str, Tuple[float, float, float]]:
    """
    Extract 3D bone positions from front and side views
    This is a simplified version - in production, you'd use more sophisticated computer vision
    
    Args:
        front_image: Front view image array
        side_image: Side view image array
        
    Returns:
        Dictionary mapping bone identifiers to 3D positions
    """
    # Detect bone positions in both views
    front_positions = detect_bone_positions(front_image)
    side_positions = detect_bone_positions(side_image)
    
    # This is a simplified reconstruction
    # In production, you'd use proper correspondence matching between views
    bone_structure = {}
    
    # For now, we'll create a simple mapping
    # This would need to be much more sophisticated in practice
    for i, (front_pos, side_pos) in enumerate(zip(front_positions, side_positions)):
        # Normalize to -1 to 1 range
        h, w = front_image.shape[:2]
        
        # Front view gives us X and Z
        x = (front_pos[0] / w) * 2 - 1
        z = (front_pos[1] / h) * 2 - 1
        
        # Side view gives us Y and Z (verify)
        y = (side_pos[0] / w) * 2 - 1
        
        bone_structure[f"bone_{i}"] = (x, y, z)
    
    return bone_structure


def calculate_bone_rotation(rest_head: mathutils.Vector, rest_tail: mathutils.Vector,
                           new_head: mathutils.Vector, new_tail: mathutils.Vector) -> mathutils.Quaternion:
    """
    Calculate rotation needed to transform rest pose bone to new pose
    
    Args:
        rest_head: Rest pose bone head position
        rest_tail: Rest pose bone tail position
        new_head: New pose bone head position
        new_tail: New pose bone tail position
        
    Returns:
        Rotation quaternion
    """
    # Calculate bone vectors
    rest_vector = (rest_tail - rest_head).normalized()
    new_vector = (new_tail - new_head).normalized()
    
    # Calculate rotation between vectors
    rotation = rest_vector.rotation_difference(new_vector)
    
    return rotation


def apply_pose_to_armature(armature: bpy.types.Object, 
                          rest_bone_positions: Dict[str, Tuple[mathutils.Vector, mathutils.Vector]],
                          new_bone_positions: Dict[str, Tuple[mathutils.Vector, mathutils.Vector]],
                          influence: float = 1.0):
    """
    Apply extracted pose to armature
    
    Args:
        armature: Armature object
        rest_bone_positions: Dictionary of bone names to (head, tail) in rest pose
        new_bone_positions: Dictionary of bone names to (head, tail) in new pose
        influence: Influence factor (0-1)
    """
    if armature.type != 'ARMATURE':
        return
    
    # Enter pose mode
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='POSE')
    
    # Apply rotations to bones
    for bone_name in rest_bone_positions:
        if bone_name not in new_bone_positions:
            continue
        
        pose_bone = armature.pose.bones.get(bone_name)
        if not pose_bone:
            continue
        
        rest_head, rest_tail = rest_bone_positions[bone_name]
        new_head, new_tail = new_bone_positions[bone_name]
        
        # Calculate rotation
        rotation = calculate_bone_rotation(rest_head, rest_tail, new_head, new_tail)
        
        # Apply rotation with influence
        if influence < 1.0:
            identity = mathutils.Quaternion()
            rotation = identity.slerp(rotation, influence)
        
        # Set bone rotation
        pose_bone.rotation_quaternion = rotation
    
    # Return to object mode
    bpy.ops.object.mode_set(mode='OBJECT')


def match_bones_to_structure(armature: bpy.types.Object, 
                            bone_structure: Dict[str, Tuple[float, float, float]]) -> Dict[str, Tuple[mathutils.Vector, mathutils.Vector]]:
    """
    Match detected bone structure to armature bones
    This is a simplified version - in production, you'd use more sophisticated matching
    
    Args:
        armature: Armature object
        bone_structure: Dictionary of detected bone positions
        
    Returns:
        Dictionary mapping bone names to (head, tail) positions
    """
    if armature.type != 'ARMATURE':
        return {}
    
    bone_positions = {}
    
    # Get all bones sorted by hierarchy
    bones = sorted(armature.data.bones, key=lambda b: len(b.parent_recursive))
    
    # Simple matching: assign detected positions to bones in order
    # In production, you'd use spatial matching and bone name recognition
    structure_items = list(bone_structure.items())
    
    for i, bone in enumerate(bones):
        if i * 2 + 1 < len(structure_items):
            # Get head and tail positions from structure
            head_key, head_pos = structure_items[i * 2]
            tail_key, tail_pos = structure_items[i * 2 + 1]
            
            head = mathutils.Vector(head_pos)
            tail = mathutils.Vector(tail_pos)
            
            bone_positions[bone.name] = (head, tail)
    
    return bone_positions


def process_ai_generated_images(armature: bpy.types.Object,
                                front_rest_path: str, side_rest_path: str,
                                front_posed_path: str, side_posed_path: str,
                                influence: float = 1.0) -> bool:
    """
    Main function to process AI-generated images and apply pose
    
    Args:
        armature: Armature object to pose
        front_rest_path: Path to front view rest pose image
        side_rest_path: Path to side view rest pose image
        front_posed_path: Path to front view posed image
        side_posed_path: Path to side view posed image
        influence: Pose influence factor (0-1)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Load images
        front_rest = load_image_as_array(front_rest_path)
        side_rest = load_image_as_array(side_rest_path)
        front_posed = load_image_as_array(front_posed_path)
        side_posed = load_image_as_array(side_posed_path)
        
        if any(img is None for img in [front_rest, side_rest, front_posed, side_posed]):
            print("Failed to load one or more images")
            return False
        
        # Extract bone structures
        rest_structure = extract_bone_structure(front_rest, side_rest)
        posed_structure = extract_bone_structure(front_posed, side_posed)
        
        # Match to armature bones
        rest_bone_positions = match_bones_to_structure(armature, rest_structure)
        posed_bone_positions = match_bones_to_structure(armature, posed_structure)
        
        # Apply pose
        apply_pose_to_armature(armature, rest_bone_positions, posed_bone_positions, influence)
        
        return True
        
    except Exception as e:
        print(f"Error processing images: {e}")
        import traceback
        traceback.print_exc()
        return False


def register():
    """Register module"""
    pass


def unregister():
    """Unregister module"""
    pass

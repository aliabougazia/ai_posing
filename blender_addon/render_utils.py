"""
Rendering utilities for capturing model and armature views
"""

import bpy
import mathutils
import os
import tempfile
from typing import Tuple, Optional


class RenderSetup:
    """Context manager for setting up and cleaning up render settings"""
    
    def __init__(self, resolution: int = 1024):
        self.resolution = resolution
        self.original_settings = {}
        
    def __enter__(self):
        """Store original render settings"""
        scene = bpy.context.scene
        render = scene.render
        
        self.original_settings = {
            'resolution_x': render.resolution_x,
            'resolution_y': render.resolution_y,
            'resolution_percentage': render.resolution_percentage,
            'film_transparent': render.film_transparent,
            'image_settings_file_format': render.image_settings.file_format,
            'image_settings_color_mode': render.image_settings.color_mode,
        }
        
        # Set new render settings
        render.resolution_x = self.resolution
        render.resolution_y = self.resolution
        render.resolution_percentage = 100
        render.film_transparent = True
        render.image_settings.file_format = 'PNG'
        render.image_settings.color_mode = 'RGBA'
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Restore original render settings"""
        scene = bpy.context.scene
        render = scene.render
        
        for key, value in self.original_settings.items():
            if '.' in key:
                # Handle nested attributes like image_settings.file_format
                parts = key.split('_', 2)  # Split into [image, settings, file_format]
                if parts[0] == 'image' and parts[1] == 'settings':
                    setattr(render.image_settings, '_'.join(parts[2:]), value)
            else:
                setattr(render, key, value)


def setup_camera_for_view(view_type: str = 'FRONT', distance: float = 5.0) -> bpy.types.Object:
    """
    Set up or get camera for specific view
    
    Args:
        view_type: 'FRONT' or 'SIDE'
        distance: Distance from origin
        
    Returns:
        Camera object
    """
    scene = bpy.context.scene
    
    # Create or get camera
    camera_name = f"AI_Pose_Camera_{view_type}"
    if camera_name in bpy.data.objects:
        camera = bpy.data.objects[camera_name]
    else:
        camera_data = bpy.data.cameras.new(name=camera_name)
        camera = bpy.data.objects.new(camera_name, camera_data)
        scene.collection.objects.link(camera)
    
    # Position camera
    if view_type == 'FRONT':
        camera.location = (0, -distance, 0)
        camera.rotation_euler = (1.5708, 0, 0)  # 90 degrees in radians
    elif view_type == 'SIDE':
        camera.location = (distance, 0, 0)
        camera.rotation_euler = (1.5708, 0, 1.5708)
    
    # Set as active camera
    scene.camera = camera
    
    return camera


def frame_object_in_camera(obj: bpy.types.Object, camera: bpy.types.Object, margin: float = 1.2):
    """
    Adjust camera distance to frame object properly
    
    Args:
        obj: Object to frame
        camera: Camera object
        margin: Margin multiplier for framing
    """
    # Calculate bounding box
    bbox_corners = [obj.matrix_world @ mathutils.Vector(corner) for corner in obj.bound_box]
    
    # Calculate center and size
    center = sum(bbox_corners, mathutils.Vector()) / 8
    
    # Calculate maximum dimension
    max_dim = max(
        max(corner.x for corner in bbox_corners) - min(corner.x for corner in bbox_corners),
        max(corner.y for corner in bbox_corners) - min(corner.y for corner in bbox_corners),
        max(corner.z for corner in bbox_corners) - min(corner.z for corner in bbox_corners)
    )
    
    # Calculate camera distance
    camera_data = camera.data
    sensor_fit = camera_data.sensor_fit
    
    if sensor_fit == 'AUTO':
        sensor_fit = 'HORIZONTAL' if camera_data.sensor_width > camera_data.sensor_height else 'VERTICAL'
    
    if sensor_fit == 'HORIZONTAL':
        sensor_size = camera_data.sensor_width
    else:
        sensor_size = camera_data.sensor_height
    
    fov = camera_data.angle
    distance = (max_dim * margin) / (2 * mathutils.tan(fov / 2))
    
    # Update camera position maintaining direction
    direction = (camera.location - center).normalized()
    camera.location = center + direction * distance


def setup_armature_visualization(armature: bpy.types.Object, visible: bool = True):
    """
    Configure armature to be visible in renders
    
    Args:
        armature: Armature object
        visible: Whether armature should be visible
    """
    if armature.type != 'ARMATURE':
        return
    
    armature.show_in_front = visible
    armature.data.show_names = False
    
    # Set display type
    armature.data.display_type = 'STICK' if visible else 'OCTAHEDRAL'
    
    # Make sure armature is visible to camera
    armature.hide_render = not visible


def create_bone_mesh_overlay(armature: bpy.types.Object) -> Optional[bpy.types.Object]:
    """
    Create a mesh overlay that shows bone positions clearly
    
    Args:
        armature: Armature object
        
    Returns:
        Mesh object representing bones, or None if failed
    """
    if armature.type != 'ARMATURE':
        return None
    
    # Create a new mesh
    mesh_name = f"{armature.name}_BoneOverlay"
    
    # Remove existing overlay if present
    if mesh_name in bpy.data.objects:
        old_obj = bpy.data.objects[mesh_name]
        bpy.data.objects.remove(old_obj, do_unlink=True)
    
    mesh = bpy.data.meshes.new(mesh_name)
    obj = bpy.data.objects.new(mesh_name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    
    # Build mesh from bone positions
    verts = []
    edges = []
    
    for bone in armature.data.bones:
        # Get world space positions
        head = armature.matrix_world @ bone.head_local
        tail = armature.matrix_world @ bone.tail_local
        
        start_idx = len(verts)
        verts.append(head)
        verts.append(tail)
        edges.append((start_idx, start_idx + 1))
    
    mesh.from_pydata(verts, edges, [])
    mesh.update()
    
    # Create material for bones
    mat = bpy.data.materials.new(name=f"{mesh_name}_Material")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    # Create emission shader for bright visibility
    output = nodes.new('ShaderNodeOutputMaterial')
    emission = nodes.new('ShaderNodeEmission')
    emission.inputs['Color'].default_value = (1.0, 0.0, 0.0, 1.0)  # Red
    emission.inputs['Strength'].default_value = 2.0
    
    mat.node_tree.links.new(emission.outputs['Emission'], output.inputs['Surface'])
    
    obj.data.materials.append(mat)
    
    return obj


def render_view(view_type: str, obj: bpy.types.Object, armature: bpy.types.Object, 
                resolution: int = 1024, show_bones: bool = True) -> str:
    """
    Render a view of the model with armature
    
    Args:
        view_type: 'FRONT' or 'SIDE'
        obj: Mesh object to render
        armature: Armature object
        resolution: Render resolution
        show_bones: Whether to show armature bones
        
    Returns:
        Path to rendered image file
    """
    # Setup camera
    camera = setup_camera_for_view(view_type, distance=5.0)
    frame_object_in_camera(obj, camera)
    
    # Setup armature visualization
    if show_bones:
        setup_armature_visualization(armature, visible=True)
        bone_overlay = create_bone_mesh_overlay(armature)
    else:
        setup_armature_visualization(armature, visible=False)
        bone_overlay = None
    
    # Render with settings
    with RenderSetup(resolution):
        # Create temp file
        temp_dir = tempfile.gettempdir()
        output_path = os.path.join(temp_dir, f"ai_pose_{view_type.lower()}_{bpy.context.scene.frame_current}.png")
        
        bpy.context.scene.render.filepath = output_path
        bpy.ops.render.render(write_still=True)
    
    # Cleanup bone overlay
    if bone_overlay:
        bpy.data.objects.remove(bone_overlay, do_unlink=True)
    
    return output_path


def render_both_views(obj: bpy.types.Object, armature: bpy.types.Object,
                     resolution: int = 1024, show_bones: bool = True) -> Tuple[str, str]:
    """
    Render both front and side views
    
    Args:
        obj: Mesh object to render
        armature: Armature object
        resolution: Render resolution
        show_bones: Whether to show armature bones
        
    Returns:
        Tuple of (front_view_path, side_view_path)
    """
    front_path = render_view('FRONT', obj, armature, resolution, show_bones)
    side_path = render_view('SIDE', obj, armature, resolution, show_bones)
    
    return front_path, side_path


def register():
    """Register module"""
    pass


def unregister():
    """Unregister module"""
    pass

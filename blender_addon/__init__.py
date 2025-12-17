bl_info = {
    "name": "AI Pose Generator",
    "author": "AI Posing Team",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > AI Pose",
    "description": "Generate poses for rigged models using ComfyUI and AI image editing",
    "category": "Animation",
}

import bpy
from . import (
    preferences,
    ui_panel,
    operators,
    comfyui_client,
    render_utils,
    pose_processor,
    workflow_manager,
)

modules = [
    preferences,
    ui_panel,
    operators,
    comfyui_client,
    render_utils,
    pose_processor,
    workflow_manager,
]


def register():
    """Register all add-on classes and properties"""
    for module in modules:
        if hasattr(module, "register"):
            module.register()
    
    # Scene properties
    bpy.types.Scene.ai_pose_prompt = bpy.props.StringProperty(
        name="Pose Prompt",
        description="Describe the desired pose (e.g., 'running', 'jumping', 'sitting')",
        default=""
    )
    
    bpy.types.Scene.ai_pose_target_object = bpy.props.PointerProperty(
        name="Target Model",
        description="Select the rigged model to pose",
        type=bpy.types.Object,
        poll=lambda self, obj: obj.type == 'MESH' and obj.find_armature() is not None
    )
    
    bpy.types.Scene.ai_pose_armature = bpy.props.PointerProperty(
        name="Armature",
        description="Select the armature to pose",
        type=bpy.types.Object,
        poll=lambda self, obj: obj.type == 'ARMATURE'
    )
    
    bpy.types.Scene.ai_pose_workflow_path = bpy.props.StringProperty(
        name="Workflow JSON",
        description="Path to ComfyUI workflow JSON file",
        default="",
        subtype='FILE_PATH'
    )
    
    bpy.types.Scene.ai_pose_status = bpy.props.StringProperty(
        name="Status",
        description="Current operation status",
        default="Ready"
    )
    
    bpy.types.Scene.ai_pose_render_resolution = bpy.props.IntProperty(
        name="Render Resolution",
        description="Resolution for rendering the model",
        default=1024,
        min=512,
        max=2048
    )
    
    bpy.types.Scene.ai_pose_show_bones = bpy.props.BoolProperty(
        name="Show Bones",
        description="Show armature bones in rendered images",
        default=True
    )
    
    print("AI Pose Generator add-on registered")


def unregister():
    """Unregister all add-on classes and properties"""
    # Delete scene properties
    del bpy.types.Scene.ai_pose_prompt
    del bpy.types.Scene.ai_pose_target_object
    del bpy.types.Scene.ai_pose_armature
    del bpy.types.Scene.ai_pose_workflow_path
    del bpy.types.Scene.ai_pose_status
    del bpy.types.Scene.ai_pose_render_resolution
    del bpy.types.Scene.ai_pose_show_bones
    
    for module in reversed(modules):
        if hasattr(module, "unregister"):
            module.unregister()
    
    print("AI Pose Generator add-on unregistered")


if __name__ == "__main__":
    register()

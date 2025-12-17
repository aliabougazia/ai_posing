"""
Blender add-on preferences and settings
"""

import bpy
from bpy.types import AddonPreferences
from bpy.props import StringProperty


class AIPoseAddonPreferences(AddonPreferences):
    """Add-on preferences for AI Pose Generator"""
    
    bl_idname = __package__
    
    comfyui_server: StringProperty(
        name="ComfyUI Server",
        description="URL of the ComfyUI server",
        default="http://localhost:8188",
    )
    
    default_workflow_path: StringProperty(
        name="Default Workflow",
        description="Path to default ComfyUI workflow JSON file",
        default="",
        subtype='FILE_PATH',
    )
    
    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        box.label(text="ComfyUI Connection Settings:", icon='NETWORK_DRIVE')
        box.prop(self, "comfyui_server")
        
        box = layout.box()
        box.label(text="Default Workflow:", icon='FILE')
        box.prop(self, "default_workflow_path")
        
        layout.separator()
        
        # Add link to documentation
        box = layout.box()
        box.label(text="Help & Documentation:", icon='QUESTION')
        box.label(text="Configure your ComfyUI server address above")
        box.label(text="Upload a workflow JSON file in the AI Pose panel")


def get_addon_preferences(context=None):
    """Get add-on preferences"""
    if context is None:
        context = bpy.context
    
    preferences = context.preferences.addons.get(__package__)
    if preferences:
        return preferences.preferences
    return None


def register():
    """Register preferences"""
    bpy.utils.register_class(AIPoseAddonPreferences)


def unregister():
    """Unregister preferences"""
    bpy.utils.unregister_class(AIPoseAddonPreferences)

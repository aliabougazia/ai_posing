"""
UI Panel for AI Pose Generator
"""

import bpy
from bpy.types import Panel


class AIPOSE_PT_MainPanel(Panel):
    """Main panel for AI Pose Generator"""
    bl_label = "AI Pose Generator"
    bl_idname = "AIPOSE_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'AI Pose'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # Status display
        box = layout.box()
        box.label(text="Status:", icon='INFO')
        box.label(text=scene.ai_pose_status)
        
        layout.separator()
        
        # Model selection
        box = layout.box()
        box.label(text="Model Selection:", icon='OUTLINER_OB_ARMATURE')
        box.prop(scene, "ai_pose_target_object", text="Target Model")
        box.prop(scene, "ai_pose_armature", text="Armature")
        
        layout.separator()
        
        # Workflow selection
        box = layout.box()
        box.label(text="ComfyUI Workflow:", icon='FILE')
        row = box.row(align=True)
        row.operator("aipose.load_workflow", icon='FILEBROWSER', text="Select Workflow")
        if scene.ai_pose_workflow_path:
            import os
            filename = os.path.basename(scene.ai_pose_workflow_path)
            box.label(text=f"✓ {filename}", icon='CHECKMARK')
        else:
            box.label(text="No workflow selected", icon='ERROR')
        
        layout.separator()
        
        # Pose prompt
        box = layout.box()
        box.label(text="Pose Prompt:", icon='TEXT')
        box.prop(scene, "ai_pose_prompt", text="")
        box.label(text="Example: 'running', 'jumping', 'sitting'", icon='QUESTION')
        
        layout.separator()
        
        # Render settings
        box = layout.box()
        box.label(text="Render Settings:", icon='CAMERA_DATA')
        box.prop(scene, "ai_pose_render_resolution", text="Resolution")
        box.prop(scene, "ai_pose_show_bones", text="Show Bones in Render")
        
        layout.separator()
        
        # Main action button
        box = layout.box()
        col = box.column(align=True)
        col.scale_y = 1.5
        
        # Check if ready to generate
        can_generate = (
            scene.ai_pose_target_object is not None and 
            scene.ai_pose_armature is not None and 
            bool(scene.ai_pose_prompt.strip()) and
            bool(scene.ai_pose_workflow_path.strip())
        )
        
        col.operator("aipose.generate_pose", icon='ARMATURE_DATA', text="Generate Pose")
        col.enabled = can_generate
        
        if not can_generate:
            # Show which fields are missing
            missing = []
            if not scene.ai_pose_workflow_path.strip():
                missing.append("Workflow")
            if not scene.ai_pose_target_object:
                missing.append("Target Model")
            if not scene.ai_pose_armature:
                missing.append("Armature")
            if not scene.ai_pose_prompt.strip():
                missing.append("Prompt")
            
            if missing:
                box.label(text=f"Missing: {', '.join(missing)}", icon='ERROR')
            else:
                box.label(text="Complete all fields above", icon='ERROR')
        
        layout.separator()
        
        # Reset button
        row = layout.row()
        row.operator("aipose.reset_pose", icon='LOOP_BACK', text="Reset to Rest Pose")


class AIPOSE_PT_WorkflowPanel(Panel):
    """Panel for workflow management"""
    bl_label = "ComfyUI Workflow"
    bl_idname = "AIPOSE_PT_workflow_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'AI Pose'
    bl_parent_id = "AIPOSE_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        box = layout.box()
        box.label(text="Workflow JSON File:", icon='FILE')
        
        # Display current workflow
        if scene.ai_pose_workflow_path:
            import os
            filename = os.path.basename(scene.ai_pose_workflow_path)
            box.label(text=f"Loaded: {filename}", icon='CHECKMARK')
        else:
            box.label(text="No workflow loaded", icon='ERROR')
        
        # Load workflow button
        box.operator("aipose.load_workflow", icon='FILEBROWSER', text="Load Workflow JSON")
        
        layout.separator()
        
        # Show workflow path property
        col = layout.column()
        col.prop(scene, "ai_pose_workflow_path", text="")


class AIPOSE_PT_ConnectionPanel(Panel):
    """Panel for ComfyUI connection settings"""
    bl_label = "ComfyUI Connection"
    bl_idname = "AIPOSE_PT_connection_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'AI Pose'
    bl_parent_id = "AIPOSE_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        
        from . import preferences
        prefs = preferences.get_addon_preferences(context)
        
        box = layout.box()
        box.label(text="Server Settings:", icon='NETWORK_DRIVE')
        
        if prefs:
            box.prop(prefs, "comfyui_server", text="Server URL")
        else:
            box.label(text="Default: http://localhost:8188")
        
        layout.separator()
        
        # Test connection button
        row = layout.row()
        row.scale_y = 1.2
        row.operator("aipose.test_connection", icon='PLUGIN', text="Test Connection")
        
        layout.separator()
        
        # Help text
        box = layout.box()
        box.label(text="Connection Help:", icon='QUESTION')
        col = box.column(align=True)
        col.label(text="1. Make sure ComfyUI is running")
        col.label(text="2. Default port is 8188")
        col.label(text="3. Click 'Test Connection' to verify")


class AIPOSE_PT_HelpPanel(Panel):
    """Panel with help and instructions"""
    bl_label = "Help & Instructions"
    bl_idname = "AIPOSE_PT_help_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'AI Pose'
    bl_parent_id = "AIPOSE_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        box.label(text="Quick Start Guide:", icon='HELP')
        
        col = box.column(align=True)
        col.label(text="1. Select your rigged model")
        col.label(text="2. Select the armature")
        col.label(text="3. Load ComfyUI workflow JSON")
        col.label(text="4. Test ComfyUI connection")
        col.label(text="5. Enter pose description")
        col.label(text="6. Click 'Generate Pose'")
        
        layout.separator()
        
        box = layout.box()
        box.label(text="Requirements:", icon='SETTINGS')
        col = box.column(align=True)
        col.label(text="• Blender 3.0 or higher")
        col.label(text="• ComfyUI server running")
        col.label(text="• Qwen Image Edit model")
        col.label(text="• Model with armature rig")
        
        layout.separator()
        
        box = layout.box()
        box.label(text="Tips:", icon='INFO')
        col = box.column(align=True)
        col.label(text="• Keep prompts simple and clear")
        col.label(text="• Ensure bones are visible in renders")
        col.label(text="• Processing may take 1-2 minutes")
        col.label(text="• Use 'Reset Pose' to start over")


# List of panel classes
classes = [
    AIPOSE_PT_MainPanel,
    AIPOSE_PT_WorkflowPanel,
    AIPOSE_PT_ConnectionPanel,
    AIPOSE_PT_HelpPanel,
]


def register():
    """Register UI panels"""
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    """Unregister UI panels"""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

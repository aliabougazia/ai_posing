"""
Blender operators for AI pose generation
"""

import bpy
import os
from bpy.types import Operator
from bpy.props import StringProperty

from . import comfyui_client
from . import render_utils
from . import pose_processor
from . import workflow_manager
from . import preferences


class AIPOSE_OT_TestConnection(Operator):
    """Test connection to ComfyUI server"""
    bl_idname = "aipose.test_connection"
    bl_label = "Test Connection"
    bl_description = "Test connection to ComfyUI server"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        prefs = preferences.get_addon_preferences(context)
        server_address = prefs.comfyui_server if prefs else "http://localhost:8188"
        
        # Create client and test connection
        client = comfyui_client.ComfyUIClient(server_address)
        success, message = client.test_connection()
        
        if success:
            self.report({'INFO'}, message)
            context.scene.ai_pose_status = "Connected"
        else:
            self.report({'ERROR'}, message)
            context.scene.ai_pose_status = "Connection Failed"
        
        return {'FINISHED'}


class AIPOSE_OT_LoadWorkflow(Operator):
    """Load ComfyUI workflow from JSON file"""
    bl_idname = "aipose.load_workflow"
    bl_label = "Load Workflow"
    bl_description = "Load a ComfyUI workflow JSON file"
    bl_options = {'REGISTER', 'UNDO'}
    
    filepath: StringProperty(
        name="Workflow File",
        description="Path to workflow JSON file",
        subtype='FILE_PATH'
    )
    
    filter_glob: StringProperty(
        default="*.json",
        options={'HIDDEN'}
    )
    
    def execute(self, context):
        if not self.filepath:
            self.report({'ERROR'}, "No file selected")
            return {'CANCELLED'}
        
        # Load workflow
        wm = workflow_manager.WorkflowManager()
        workflow, error = wm.load_workflow(self.filepath)
        
        if workflow is None:
            self.report({'ERROR'}, f"Failed to load workflow: {error}")
            return {'CANCELLED'}
        
        # Validate workflow
        is_valid, validation_error = wm.validate_workflow_structure(workflow)
        if not is_valid:
            self.report({'WARNING'}, f"Workflow validation warning: {validation_error}")
        
        # Store workflow path
        context.scene.ai_pose_workflow_path = self.filepath
        
        # Get workflow info
        info = wm.get_workflow_info(workflow)
        self.report({'INFO'}, f"Loaded workflow successfully\n{info}")
        context.scene.ai_pose_status = "Workflow Loaded"
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class AIPOSE_OT_GeneratePose(Operator):
    """Generate pose using AI"""
    bl_idname = "aipose.generate_pose"
    bl_label = "Generate Pose"
    bl_description = "Generate and apply pose using ComfyUI and AI"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        scene = context.scene
        
        # Validate inputs
        if not scene.ai_pose_target_object:
            self.report({'ERROR'}, "Please select a target model")
            return {'CANCELLED'}
        
        if not scene.ai_pose_armature:
            self.report({'ERROR'}, "Please select an armature")
            return {'CANCELLED'}
        
        if not scene.ai_pose_prompt:
            self.report({'ERROR'}, "Please enter a pose prompt")
            return {'CANCELLED'}
        
        if not scene.ai_pose_workflow_path or not os.path.exists(scene.ai_pose_workflow_path):
            self.report({'ERROR'}, "Please load a valid workflow JSON file")
            return {'CANCELLED'}
        
        # Get preferences
        prefs = preferences.get_addon_preferences(context)
        server_address = prefs.comfyui_server if prefs else "http://localhost:8188"
        
        try:
            # Update status
            scene.ai_pose_status = "Rendering views..."
            context.area.tag_redraw()
            
            # Render front and side views with armature
            self.report({'INFO'}, "Rendering rest pose views...")
            front_rest, side_rest = render_utils.render_both_views(
                scene.ai_pose_target_object,
                scene.ai_pose_armature,
                scene.ai_pose_render_resolution,
                scene.ai_pose_show_bones
            )
            
            # Load workflow
            scene.ai_pose_status = "Loading workflow..."
            wm = workflow_manager.WorkflowManager()
            workflow, error = wm.load_workflow(scene.ai_pose_workflow_path)
            
            if workflow is None:
                self.report({'ERROR'}, f"Failed to load workflow: {error}")
                return {'CANCELLED'}
            
            # Create ComfyUI client
            client = comfyui_client.ComfyUIClient(server_address)
            
            # Upload images to ComfyUI
            scene.ai_pose_status = "Uploading images..."
            self.report({'INFO'}, "Uploading images to ComfyUI...")
            
            with open(front_rest, 'rb') as f:
                front_data = f.read()
            with open(side_rest, 'rb') as f:
                side_data = f.read()
            
            front_result = client.upload_image(front_data, "front_rest.png")
            side_result = client.upload_image(side_data, "side_rest.png")
            
            if not front_result or not side_result:
                self.report({'ERROR'}, "Failed to upload images to ComfyUI")
                return {'CANCELLED'}
            
            # Update workflow with inputs
            scene.ai_pose_status = "Processing with AI..."
            updated_workflow = wm.update_workflow_inputs(
                workflow,
                "front_rest.png",
                "side_rest.png",
                scene.ai_pose_prompt
            )
            
            # Validate updated workflow before sending
            is_valid, validation_error = wm.validate_workflow_structure(updated_workflow)
            if not is_valid:
                self.report({'ERROR'}, f"Workflow validation failed: {validation_error}")
                return {'CANCELLED'}
            
            # Queue prompt
            self.report({'INFO'}, "Sending to ComfyUI for processing...")
            
            # Debug: Print workflow structure
            print(f"Workflow has {len(updated_workflow)} nodes")
            for node_id in updated_workflow.keys():
                print(f"  Node {node_id}: {updated_workflow[node_id].get('class_type', 'NO CLASS_TYPE')}")
            
            prompt_id = client.queue_prompt(updated_workflow)
            
            if not prompt_id:
                self.report({'ERROR'}, "Failed to queue prompt in ComfyUI")
                return {'CANCELLED'}
            
            # Wait for completion
            scene.ai_pose_status = "Waiting for AI processing..."
            self.report({'INFO'}, f"Prompt queued (ID: {prompt_id}). Waiting for completion...")
            
            history = client.wait_for_completion(prompt_id, timeout=300)
            
            if not history:
                self.report({'ERROR'}, "Timeout waiting for ComfyUI to complete")
                return {'CANCELLED'}
            
            # Get output images
            scene.ai_pose_status = "Downloading results..."
            output_images = client.get_output_images(history)
            
            if len(output_images) < 2:
                self.report({'ERROR'}, f"Expected 2 output images, got {len(output_images)}")
                return {'CANCELLED'}
            
            # Download images
            self.report({'INFO'}, "Downloading generated images...")
            import tempfile
            
            front_posed_path = os.path.join(tempfile.gettempdir(), "front_posed.png")
            side_posed_path = os.path.join(tempfile.gettempdir(), "side_posed.png")
            
            front_image_data = client.get_image(*output_images[0])
            side_image_data = client.get_image(*output_images[1])
            
            if not front_image_data or not side_image_data:
                self.report({'ERROR'}, "Failed to download output images")
                return {'CANCELLED'}
            
            with open(front_posed_path, 'wb') as f:
                f.write(front_image_data)
            with open(side_posed_path, 'wb') as f:
                f.write(side_image_data)
            
            # Process images and apply pose
            scene.ai_pose_status = "Applying pose..."
            self.report({'INFO'}, "Extracting pose and applying to armature...")
            
            success = pose_processor.process_ai_generated_images(
                scene.ai_pose_armature,
                front_rest, side_rest,
                front_posed_path, side_posed_path,
                influence=1.0
            )
            
            if success:
                scene.ai_pose_status = "Pose applied successfully!"
                self.report({'INFO'}, "Pose generated and applied successfully!")
            else:
                scene.ai_pose_status = "Failed to apply pose"
                self.report({'ERROR'}, "Failed to process pose from AI images")
                return {'CANCELLED'}
            
            # Cleanup temp files
            for path in [front_rest, side_rest, front_posed_path, side_posed_path]:
                try:
                    if os.path.exists(path):
                        os.remove(path)
                except:
                    pass
            
            return {'FINISHED'}
            
        except Exception as e:
            scene.ai_pose_status = f"Error: {str(e)}"
            self.report({'ERROR'}, f"Error during pose generation: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'CANCELLED'}


class AIPOSE_OT_ResetPose(Operator):
    """Reset armature to rest pose"""
    bl_idname = "aipose.reset_pose"
    bl_label = "Reset Pose"
    bl_description = "Reset armature to rest pose"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        armature = context.scene.ai_pose_armature
        
        if not armature or armature.type != 'ARMATURE':
            self.report({'ERROR'}, "No valid armature selected")
            return {'CANCELLED'}
        
        # Set active and enter pose mode
        context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='POSE')
        
        # Select all bones
        bpy.ops.pose.select_all(action='SELECT')
        
        # Clear transforms
        bpy.ops.pose.transforms_clear()
        
        # Return to object mode
        bpy.ops.object.mode_set(mode='OBJECT')
        
        context.scene.ai_pose_status = "Pose reset to rest position"
        self.report({'INFO'}, "Pose reset to rest position")
        
        return {'FINISHED'}


# List of operator classes
classes = [
    AIPOSE_OT_TestConnection,
    AIPOSE_OT_LoadWorkflow,
    AIPOSE_OT_GeneratePose,
    AIPOSE_OT_ResetPose,
]


def register():
    """Register operators"""
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    """Unregister operators"""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

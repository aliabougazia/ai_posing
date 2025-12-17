"""
Test script for AI Pose Generator add-on
Run this from Blender's scripting console to test the add-on
"""

import bpy
import sys
import os

def test_addon_installation():
    """Test if the add-on is properly installed"""
    print("=" * 60)
    print("Testing AI Pose Generator Add-on Installation")
    print("=" * 60)
    
    # Check if add-on is enabled
    addon_name = "blender_addon"
    preferences = bpy.context.preferences
    addon = preferences.addons.get(addon_name)
    
    if addon:
        print("✓ Add-on is installed and enabled")
        print(f"  Version: {addon.bl_info.get('version', 'Unknown')}")
    else:
        print("✗ Add-on is not enabled")
        print("  Please enable it in Edit > Preferences > Add-ons")
        return False
    
    # Check if UI panel is available
    try:
        bpy.types.AIPOSE_PT_MainPanel
        print("✓ UI Panel is registered")
    except AttributeError:
        print("✗ UI Panel not found")
        return False
    
    # Check if operators are available
    operators = [
        "aipose.test_connection",
        "aipose.load_workflow",
        "aipose.generate_pose",
        "aipose.reset_pose"
    ]
    
    for op in operators:
        if hasattr(bpy.ops, op.split('.')[0]):
            op_module = getattr(bpy.ops, op.split('.')[0])
            if hasattr(op_module, op.split('.')[1]):
                print(f"✓ Operator '{op}' is available")
            else:
                print(f"✗ Operator '{op}' not found")
                return False
    
    # Check scene properties
    scene = bpy.context.scene
    properties = [
        "ai_pose_prompt",
        "ai_pose_target_object",
        "ai_pose_armature",
        "ai_pose_workflow_path",
        "ai_pose_status"
    ]
    
    for prop in properties:
        if hasattr(scene, prop):
            print(f"✓ Scene property '{prop}' is available")
        else:
            print(f"✗ Scene property '{prop}' not found")
            return False
    
    print("\n" + "=" * 60)
    print("All tests passed! Add-on is properly installed.")
    print("=" * 60)
    return True


def test_comfyui_connection(server_url="http://localhost:8188"):
    """Test connection to ComfyUI server"""
    print("\n" + "=" * 60)
    print("Testing ComfyUI Connection")
    print("=" * 60)
    
    try:
        from blender_addon import comfyui_client
        
        client = comfyui_client.ComfyUIClient(server_url)
        success, message = client.test_connection()
        
        if success:
            print(f"✓ {message}")
            print(f"  Server: {server_url}")
            return True
        else:
            print(f"✗ Connection failed: {message}")
            print(f"  Server: {server_url}")
            print("\nTroubleshooting:")
            print("  1. Make sure ComfyUI is running")
            print("  2. Check the server address")
            print("  3. Verify firewall settings")
            return False
            
    except ImportError:
        print("✗ Could not import comfyui_client module")
        return False
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


def test_workflow_loading(workflow_path=None):
    """Test workflow JSON loading"""
    print("\n" + "=" * 60)
    print("Testing Workflow Loading")
    print("=" * 60)
    
    if not workflow_path:
        print("⚠ No workflow path provided, skipping test")
        return None
    
    try:
        from blender_addon import workflow_manager
        
        wm = workflow_manager.WorkflowManager()
        workflow, error = wm.load_workflow(workflow_path)
        
        if workflow:
            print(f"✓ Workflow loaded successfully")
            print(f"  File: {workflow_path}")
            
            # Validate structure
            is_valid, validation_error = wm.validate_workflow_structure(workflow)
            if is_valid:
                print("✓ Workflow structure is valid")
            else:
                print(f"⚠ Workflow validation warning: {validation_error}")
            
            # Get info
            info = wm.get_workflow_info(workflow)
            print("\nWorkflow Info:")
            for line in info.split('\n'):
                print(f"  {line}")
            
            return True
        else:
            print(f"✗ Failed to load workflow: {error}")
            return False
            
    except ImportError:
        print("✗ Could not import workflow_manager module")
        return False
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


def test_scene_setup():
    """Test scene setup with a simple cube and armature"""
    print("\n" + "=" * 60)
    print("Testing Scene Setup")
    print("=" * 60)
    
    try:
        # Clear scene
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()
        
        # Add armature
        bpy.ops.object.armature_add()
        armature = bpy.context.active_object
        print("✓ Created test armature")
        
        # Add cube
        bpy.ops.mesh.primitive_cube_add()
        cube = bpy.context.active_object
        print("✓ Created test mesh")
        
        # Set properties
        scene = bpy.context.scene
        scene.ai_pose_target_object = cube
        scene.ai_pose_armature = armature
        scene.ai_pose_prompt = "test pose"
        
        print("✓ Scene properties set")
        print(f"  Target: {scene.ai_pose_target_object.name}")
        print(f"  Armature: {scene.ai_pose_armature.name}")
        print(f"  Prompt: {scene.ai_pose_prompt}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


def run_all_tests(workflow_path=None, server_url="http://localhost:8188"):
    """Run all tests"""
    print("\n" + "=" * 80)
    print(" " * 20 + "AI POSE GENERATOR - TEST SUITE")
    print("=" * 80 + "\n")
    
    results = {}
    
    # Test 1: Installation
    results['installation'] = test_addon_installation()
    
    # Test 2: ComfyUI Connection
    results['connection'] = test_comfyui_connection(server_url)
    
    # Test 3: Workflow Loading
    if workflow_path:
        results['workflow'] = test_workflow_loading(workflow_path)
    
    # Test 4: Scene Setup
    results['scene'] = test_scene_setup()
    
    # Summary
    print("\n" + "=" * 80)
    print(" " * 30 + "TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASSED" if result is True else "✗ FAILED" if result is False else "⚠ SKIPPED"
        print(f"{test_name.upper():20s}: {status}")
    
    print("\n" + "=" * 80)
    print(f"Total: {total} | Passed: {passed} | Failed: {failed} | Skipped: {skipped}")
    print("=" * 80 + "\n")
    
    return passed == (total - skipped)


if __name__ == "__main__":
    # Run tests with default parameters
    # Modify these as needed
    WORKFLOW_PATH = "/home/aa/docker/ai_posing/example_workflow.json"
    SERVER_URL = "http://localhost:8188"
    
    success = run_all_tests(workflow_path=WORKFLOW_PATH, server_url=SERVER_URL)
    
    if success:
        print("All tests passed! The add-on is ready to use.")
    else:
        print("Some tests failed. Please check the output above for details.")

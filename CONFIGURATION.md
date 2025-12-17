# Configuration Guide for AI Pose Generator

## ComfyUI Server Configuration

### Default Configuration
- **Server URL**: `http://localhost:8188`
- **Timeout**: 300 seconds (5 minutes)
- **Poll Interval**: 1 second

### Changing Server Address

#### Method 1: Via Blender Preferences
1. Open Blender
2. Go to `Edit > Preferences > Add-ons`
3. Find "AI Pose Generator"
4. Expand the add-on details
5. Change "ComfyUI Server" field
6. Save preferences

#### Method 2: Via Python Script
```python
import bpy

prefs = bpy.context.preferences.addons['blender_addon'].preferences
prefs.comfyui_server = "http://your-server:8188"
bpy.ops.wm.save_userpref()
```

### Remote Server Setup

If running ComfyUI on a different machine:

```python
# Example: Remote server
server = "http://192.168.1.100:8188"

# Example: Docker container
server = "http://comfyui-container:8188"

# Example: Cloud server
server = "https://your-domain.com:8188"
```

**Important**: Ensure firewall allows connections on port 8188

## Workflow Configuration

### Workflow Structure

Your workflow JSON must include:

1. **Image Input Nodes**: For loading front and side views
2. **Text/Prompt Nodes**: For pose description
3. **Image Processing Nodes**: For the AI model
4. **Output Nodes**: For saving results

### Customizing Workflow Updates

If your workflow uses different node IDs or types, modify `workflow_manager.py`:

```python
def update_workflow_inputs(workflow, front_image_path, side_image_path, prompt):
    updated = workflow.copy()
    
    # Customize these based on your workflow structure
    FRONT_IMAGE_NODE_ID = "1"  # Change to your node ID
    SIDE_IMAGE_NODE_ID = "2"   # Change to your node ID
    PROMPT_NODE_ID = "3"        # Change to your node ID
    
    # Update specific nodes
    updated[FRONT_IMAGE_NODE_ID]['inputs']['image'] = os.path.basename(front_image_path)
    updated[SIDE_IMAGE_NODE_ID]['inputs']['image'] = os.path.basename(side_image_path)
    updated[PROMPT_NODE_ID]['inputs']['text'] = prompt
    
    return updated
```

### Workflow Node Mapping

Example mapping for different workflows:

```python
# Standard Qwen workflow
WORKFLOW_MAPPING = {
    'front_image_node': '1',
    'side_image_node': '2',
    'prompt_node': '3',
    'front_output_node': '6',
    'side_output_node': '7'
}

# Custom workflow
WORKFLOW_MAPPING = {
    'front_image_node': 'LoadImage_Front',
    'side_image_node': 'LoadImage_Side',
    'prompt_node': 'TextPrompt',
    'front_output_node': 'SaveImage_Front',
    'side_output_node': 'SaveImage_Side'
}
```

## Render Settings

### Default Settings
- **Resolution**: 1024x1024 pixels
- **Format**: PNG with transparency
- **Bone Visibility**: Enabled

### Changing Render Resolution

Via UI:
- Adjust "Render Resolution" slider (512-2048px)

Via Python:
```python
import bpy
bpy.context.scene.ai_pose_render_resolution = 2048
```

### Custom Camera Settings

Modify `render_utils.py` for different camera angles:

```python
def setup_camera_for_view(view_type='FRONT', distance=5.0):
    # Front view (default)
    if view_type == 'FRONT':
        camera.location = (0, -distance, 0)
        camera.rotation_euler = (1.5708, 0, 0)
    
    # Side view (default)
    elif view_type == 'SIDE':
        camera.location = (distance, 0, 0)
        camera.rotation_euler = (1.5708, 0, 1.5708)
    
    # Custom: Three-quarter view
    elif view_type == 'THREE_QUARTER':
        import math
        angle = math.radians(45)
        camera.location = (distance * math.cos(angle), -distance * math.sin(angle), 0)
        camera.rotation_euler = (1.5708, 0, angle)
```

## Bone Detection Configuration

### Adjusting Detection Threshold

In `pose_processor.py`:

```python
def detect_bone_positions(image, threshold=100):
    # Lower threshold = more sensitive (detects fainter bones)
    # Higher threshold = less sensitive (only bright bones)
    
    # For darker renders
    threshold = 50
    
    # For brighter renders
    threshold = 150
```

### Custom Bone Colors

Change bone visualization color in `render_utils.py`:

```python
def create_bone_mesh_overlay(armature):
    # ...
    # Default: Red (1.0, 0.0, 0.0)
    emission.inputs['Color'].default_value = (1.0, 0.0, 0.0, 1.0)
    
    # Green
    emission.inputs['Color'].default_value = (0.0, 1.0, 0.0, 1.0)
    
    # Blue
    emission.inputs['Color'].default_value = (0.0, 0.0, 1.0, 1.0)
    
    # Yellow (better visibility on some backgrounds)
    emission.inputs['Color'].default_value = (1.0, 1.0, 0.0, 1.0)
```

**Note**: If you change the color, update detection logic accordingly:

```python
def detect_bone_positions(image, threshold=100):
    # For green bones
    green_channel = image[:, :, 1]  # Instead of red (index 0)
    
    # For blue bones
    blue_channel = image[:, :, 2]
```

## Pose Application Configuration

### Influence Factor

Control how much of the AI pose is applied:

```python
# In operators.py, modify AIPOSE_OT_GeneratePose.execute()
success = pose_processor.process_ai_generated_images(
    scene.ai_pose_armature,
    front_rest, side_rest,
    front_posed_path, side_posed_path,
    influence=1.0  # 0.0 = no change, 1.0 = full pose, 0.5 = half blend
)
```

Add UI slider:
```python
# In __init__.py register()
bpy.types.Scene.ai_pose_influence = bpy.props.FloatProperty(
    name="Pose Influence",
    description="How much of the AI pose to apply",
    default=1.0,
    min=0.0,
    max=1.0
)
```

### Bone Filtering

Apply pose only to specific bones:

```python
def apply_pose_to_armature(armature, rest_bone_positions, new_bone_positions, 
                          influence=1.0, bone_filter=None):
    # bone_filter example: ['spine', 'arm', 'leg']
    
    for bone_name in rest_bone_positions:
        # Skip if filtering is enabled and bone not in filter
        if bone_filter and not any(f in bone_name.lower() for f in bone_filter):
            continue
        
        # ... rest of the function
```

## Performance Tuning

### Timeout Settings

For slower servers or complex models:

```python
# In comfyui_client.py
def wait_for_completion(self, prompt_id, timeout=300, poll_interval=1.0):
    # Increase timeout for slow processing
    timeout = 600  # 10 minutes
    
    # Increase poll interval to reduce server load
    poll_interval = 2.0  # Check every 2 seconds
```

### Image Upload Optimization

For faster uploads with compression:

```python
# In operators.py before upload
from PIL import Image
import io

# Compress images
img = Image.open(front_rest)
img = img.resize((512, 512))  # Reduce resolution
buffer = io.BytesIO()
img.save(buffer, format='PNG', optimize=True)
front_data = buffer.getvalue()
```

### Caching

Enable render caching to avoid re-rendering:

```python
# Add to operators.py
RENDER_CACHE = {}

def get_cached_render(obj, armature, view_type):
    cache_key = f"{obj.name}_{armature.name}_{view_type}_{obj.data.vertices[0].co.x}"
    return RENDER_CACHE.get(cache_key)

def cache_render(obj, armature, view_type, image_path):
    cache_key = f"{obj.name}_{armature.name}_{view_type}_{obj.data.vertices[0].co.x}"
    RENDER_CACHE[cache_key] = image_path
```

## Troubleshooting Configuration Issues

### Connection Timeouts
```python
# Increase all timeout values
import socket
socket.setdefaulttimeout(60)  # 60 seconds
```

### Memory Issues
```python
# Reduce resolution
bpy.context.scene.ai_pose_render_resolution = 512
```

### Workflow Compatibility
```python
# Add debug logging
import json
print(json.dumps(workflow, indent=2))
```

## Environment Variables

Create a `.env` file in the add-on directory:

```bash
# ComfyUI Settings
COMFYUI_SERVER=http://localhost:8188
COMFYUI_TIMEOUT=300

# Rendering Settings
DEFAULT_RESOLUTION=1024
SHOW_BONES=true

# Detection Settings
BONE_DETECTION_THRESHOLD=100
BONE_COLOR_R=1.0
BONE_COLOR_G=0.0
BONE_COLOR_B=0.0

# Processing Settings
POSE_INFLUENCE=1.0
ENABLE_CACHING=false
```

Load in Python:
```python
import os
from pathlib import Path

def load_config():
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
```

## Advanced Configuration

### Custom Model Support

To use different AI models, modify the workflow to use your model's nodes and ensure the output format matches (two images with visible bone structure).

### Multi-GPU Setup

If ComfyUI uses multiple GPUs:
```python
# ComfyUI automatically handles GPU allocation
# No add-on configuration needed
```

### Network Configuration for Teams

For team setups with shared ComfyUI server:
```python
# Set in preferences
SHARED_SERVER = "http://comfyui-server.local:8188"

# Add authentication if needed (modify comfyui_client.py)
headers = {
    'Authorization': 'Bearer YOUR_TOKEN'
}
```

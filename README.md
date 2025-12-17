# AI Pose Generator - Blender Add-on

A powerful Blender add-on that uses ComfyUI and AI image editing models (like Qwen Image Edit 2509) to automatically generate and apply poses to rigged 3D models.

## Overview

This add-on bridges Blender with ComfyUI, allowing you to generate realistic poses for your rigged characters using AI. Simply describe the pose you want (e.g., "running", "jumping", "sitting"), and the add-on will:

1. Render your model from front and side views with visible armature bones
2. Send the images to ComfyUI with your pose description
3. Receive AI-generated posed images from the image editing model
4. Extract bone positions from the generated images
5. Apply the new pose to your Blender armature

## Features

- **AI-Powered Pose Generation**: Use state-of-the-art image editing models for natural pose generation
- **ComfyUI Integration**: Full integration with ComfyUI backend for flexible workflow management
- **Custom Workflows**: Upload and use your own ComfyUI workflow JSON files
- **Connection Testing**: Built-in connection testing to verify ComfyUI server availability
- **Flexible Server Configuration**: Easy configuration of ComfyUI server address
- **Armature Visualization**: Automatic rendering with visible bone structure for accurate pose extraction
- **Dual-View Processing**: Uses front and side views for accurate 3D pose reconstruction
- **Reset Functionality**: Quick reset to rest pose when needed

## Requirements

### Software Requirements
- **Blender**: 3.0 or higher
- **ComfyUI**: Running ComfyUI server
- **Python Packages** (optional, for enhanced features):
  - OpenCV (`cv2`): For better image processing
  - NumPy: Included with Blender

### ComfyUI Requirements
- ComfyUI server running (default: `http://localhost:8188`)
- Qwen Image Edit 2509 model or compatible image editing model
- Workflow configured to accept image inputs and text prompts

### Model Requirements
- 3D model with armature rig
- Model must be in a bindable state with the armature

## Installation

1. **Download the Add-on**
   - Download or clone this repository
   - The add-on files should be in a folder named `blender_addon`

2. **Install in Blender**
   - Open Blender
   - Go to `Edit > Preferences > Add-ons`
   - Click `Install...`
   - Navigate to the `blender_addon` folder and select `__init__.py`
   - Enable the add-on by checking the checkbox next to "Animation: AI Pose Generator"

3. **Configure Preferences**
   - In the add-on preferences, set your ComfyUI server address (default: `http://localhost:8188`)
   - Optionally, set a default workflow JSON file path

## Usage

### Quick Start

1. **Prepare Your Model**
   - Open a Blender file with a rigged character model
   - Ensure the model has an armature properly configured

2. **Open AI Pose Panel**
   - In the 3D Viewport, press `N` to open the sidebar
   - Click on the "AI Pose" tab

3. **Configure Settings**
   - Select your mesh model in "Target Model"
   - Select the armature in "Armature"
   - Load your ComfyUI workflow JSON file
   - Test the connection to ComfyUI

4. **Generate Pose**
   - Enter a pose description (e.g., "running", "jumping", "waving")
   - Click "Generate Pose"
   - Wait for processing (typically 1-2 minutes)
   - The pose will be automatically applied to your armature

5. **Reset if Needed**
   - Click "Reset to Rest Pose" to return to the original pose

### Panel Sections

#### Main Panel
- **Status Display**: Shows current operation status
- **Model Selection**: Choose target model and armature
- **Pose Prompt**: Enter your desired pose description
- **Render Settings**: Configure resolution and bone visibility
- **Generate Pose**: Main action button
- **Reset Pose**: Return to rest pose

#### ComfyUI Workflow
- **Load Workflow**: Upload your ComfyUI workflow JSON file
- **View Current Workflow**: See which workflow is loaded

#### ComfyUI Connection
- **Server URL**: Configure ComfyUI server address
- **Test Connection**: Verify connectivity to ComfyUI

#### Help & Instructions
- Quick start guide
- Requirements checklist
- Usage tips

## ComfyUI Workflow

### Workflow Structure

Your ComfyUI workflow should:
1. Accept two input images (front and side views)
2. Accept a text prompt describing the desired pose
3. Use an image editing model (e.g., Qwen Image Edit 2509)
4. Output two images (front and side views of the posed character)
5. Maintain visible bone structure in the output images

### Example Workflow Setup

A basic workflow structure:
```
Input Image (Front) → Image Edit Model → Output Image (Front)
Input Image (Side)  → Image Edit Model → Output Image (Side)
Text Prompt         → Text Encode     → Both Models
```

### Workflow JSON Format

The workflow JSON should follow ComfyUI's standard format. Example structure:
```json
{
  "1": {
    "class_type": "LoadImage",
    "inputs": {
      "image": "front_rest.png"
    }
  },
  "2": {
    "class_type": "LoadImage",
    "inputs": {
      "image": "side_rest.png"
    }
  },
  "3": {
    "class_type": "CLIPTextEncode",
    "inputs": {
      "text": "pose prompt here"
    }
  }
  // ... more nodes
}
```

## Pose Extraction Algorithm

The add-on uses a multi-step process to extract and apply poses:

1. **Rendering**: Captures rest pose from two orthogonal views with visible bones
2. **Upload**: Sends images to ComfyUI server
3. **AI Processing**: ComfyUI runs the workflow with the image editing model
4. **Download**: Retrieves posed images from ComfyUI
5. **Bone Detection**: Identifies bone positions in both views (looks for red emission shader)
6. **3D Reconstruction**: Combines front and side views to estimate 3D bone positions
7. **Bone Matching**: Maps detected bones to armature bones
8. **Rotation Calculation**: Computes rotation quaternions for each bone
9. **Pose Application**: Applies rotations to the armature in pose mode

## Troubleshooting

### Connection Issues
- **Error**: "Connection failed"
  - Ensure ComfyUI server is running
  - Check the server address in preferences (default: `http://localhost:8188`)
  - Verify firewall settings aren't blocking the connection

### Workflow Issues
- **Error**: "Failed to load workflow"
  - Ensure JSON file is valid
  - Check workflow structure matches ComfyUI format
  - Validate that all required nodes are present

### Pose Generation Issues
- **Poor Results**: 
  - Try more specific pose descriptions
  - Ensure bones are visible in renders (check "Show Bones in Render")
  - Verify model is in a neutral rest pose before generation
  - Check that armature is properly bound to mesh

- **Processing Timeout**:
  - Increase timeout in code if using complex models
  - Ensure ComfyUI has sufficient resources (GPU/RAM)
  - Check ComfyUI console for errors

### Image Processing Issues
- **Error**: "Failed to process images"
  - Install OpenCV for better image processing: `pip install opencv-python`
  - Check that rendered images have visible bone structure
  - Verify bone overlay material is rendering correctly

## Advanced Configuration

### Custom Bone Detection

The default bone detection looks for red emission shader. To customize:
- Edit `pose_processor.py`
- Modify `detect_bone_positions()` function
- Adjust threshold or detection method

### Workflow Customization

To customize how the workflow is updated:
- Edit `workflow_manager.py`
- Modify `update_workflow_inputs()` function
- Adjust node identification logic for your specific workflow

### Camera Configuration

To adjust camera positioning:
- Edit `render_utils.py`
- Modify `setup_camera_for_view()` function
- Adjust distance and angles as needed

## File Structure

```
blender_addon/
├── __init__.py              # Main add-on entry point
├── preferences.py           # Add-on preferences and settings
├── ui_panel.py             # UI panels and layout
├── operators.py            # Blender operators (actions)
├── comfyui_client.py       # ComfyUI API client
├── render_utils.py         # Rendering utilities
├── pose_processor.py       # Pose extraction and application
└── workflow_manager.py     # Workflow JSON management
```

## API Reference

### ComfyUIClient
- `test_connection()`: Test server connectivity
- `queue_prompt(workflow)`: Queue a workflow for execution
- `upload_image(image_data, filename)`: Upload image to ComfyUI
- `get_image(filename)`: Download image from ComfyUI
- `wait_for_completion(prompt_id)`: Wait for workflow completion

### WorkflowManager
- `load_workflow(filepath)`: Load workflow JSON file
- `update_workflow_inputs(workflow, ...)`: Update workflow with inputs
- `validate_workflow_structure(workflow)`: Validate workflow format

### RenderUtils
- `render_both_views(obj, armature, ...)`: Render front and side views
- `setup_camera_for_view(view_type)`: Configure camera for specific view

### PoseProcessor
- `process_ai_generated_images(armature, ...)`: Main pose processing function
- `detect_bone_positions(image)`: Detect bones in image
- `apply_pose_to_armature(armature, ...)`: Apply pose to armature

## Known Limitations

- Bone detection is simplified and may not work perfectly for all cases
- Complex poses with significant occlusion may not work well
- The add-on assumes a relatively standard humanoid rig structure
- Processing time depends on ComfyUI server performance and model complexity
- Requires ComfyUI workflow to maintain bone visibility in outputs

## Future Improvements

- [ ] More sophisticated bone detection using computer vision
- [ ] Support for custom bone naming conventions
- [ ] Batch pose generation for animation sequences
- [ ] Pose library for saving and reusing common poses
- [ ] Better error handling and user feedback
- [ ] Support for partial body poses
- [ ] Integration with more AI models
- [ ] Automatic workflow generation

## Contributing

Contributions are welcome! Areas for improvement:
- Better bone detection algorithms
- More robust bone matching
- Support for different rig structures
- Enhanced UI/UX
- Documentation and examples

## License

This project is provided as-is for educational and commercial use.

## Credits

- Developed for integration with ComfyUI
- Uses Qwen Image Edit 2509 or compatible models
- Built for Blender 3.0+

## Support

For issues, questions, or suggestions:
- Check the troubleshooting section
- Review ComfyUI documentation
- Verify all requirements are met

## Version History

### Version 1.0.0
- Initial release
- Basic pose generation functionality
- ComfyUI integration
- Workflow management
- Dual-view rendering and processing

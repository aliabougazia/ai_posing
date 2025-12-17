# Installation Guide

## Prerequisites

1. **Blender 3.0+** installed on your system
2. **ComfyUI** server set up and running
3. **Qwen Image Edit 2509** model installed in ComfyUI (or compatible image editing model)

## Installing ComfyUI (if not already installed)

### Option 1: Standalone Installation

```bash
# Clone ComfyUI repository
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI

# Install dependencies
pip install -r requirements.txt

# Run ComfyUI
python main.py
```

### Option 2: Docker Installation

```bash
docker pull comfyui/comfyui:latest
docker run -p 8188:8188 comfyui/comfyui:latest
```

## Installing the Blender Add-on

### Method 1: Direct Installation

1. Open Blender
2. Go to `Edit > Preferences`
3. Select the `Add-ons` tab
4. Click `Install...` button
5. Navigate to the `blender_addon` folder
6. Select `__init__.py`
7. Click `Install Add-on`
8. Enable the add-on by checking the box next to "Animation: AI Pose Generator"

### Method 2: Manual Installation

1. Locate your Blender addons folder:
   - **Windows**: `C:\Users\[YourUsername]\AppData\Roaming\Blender Foundation\Blender\[Version]\scripts\addons\`
   - **macOS**: `/Users/[YourUsername]/Library/Application Support/Blender/[Version]/scripts/addons/`
   - **Linux**: `~/.config/blender/[Version]/scripts/addons/`

2. Copy the entire `blender_addon` folder to the addons directory

3. Rename `blender_addon` to `ai_pose_generator` (optional but recommended)

4. Restart Blender

5. Go to `Edit > Preferences > Add-ons`

6. Search for "AI Pose"

7. Enable the add-on

## Configuring the Add-on

1. After enabling, click the arrow to expand add-on preferences
2. Set your ComfyUI server address (default: `http://localhost:8188`)
3. Optionally set a default workflow JSON path
4. Click `Save Preferences`

## Installing Optional Dependencies

For enhanced image processing capabilities, install OpenCV in Blender's Python:

### Find Blender's Python

**Windows:**
```bash
cd "C:\Program Files\Blender Foundation\Blender [Version]\[Version]\python\bin"
```

**macOS:**
```bash
cd /Applications/Blender.app/Contents/Resources/[Version]/python/bin
```

**Linux:**
```bash
cd /usr/share/blender/[Version]/python/bin
```

### Install OpenCV

```bash
./python -m pip install opencv-python numpy
```

Or from Blender's scripting console:
```python
import subprocess
import sys

# Get Blender's Python executable
python_exe = sys.executable

# Install OpenCV
subprocess.check_call([python_exe, "-m", "pip", "install", "opencv-python"])
```

## Setting Up the ComfyUI Workflow

1. Open ComfyUI in your web browser (typically `http://localhost:8188`)

2. Install required custom nodes (if not already installed):
   - Qwen Image Edit node (or your chosen image editing model)
   - Standard ComfyUI nodes should already be available

3. Create or load a workflow that:
   - Accepts two image inputs (front and side views)
   - Accepts a text prompt for the pose
   - Processes both images through an image editing model
   - Outputs two images (front and side posed views)

4. Save the workflow as JSON:
   - In ComfyUI, click "Save" or "Export"
   - Save as `workflow.json`

5. Use this workflow file in the Blender add-on

## Verifying Installation

1. Open Blender
2. Press `N` in the 3D Viewport to open the sidebar
3. Look for the "AI Pose" tab
4. If you see the panel, installation was successful
5. Click "Test Connection" to verify ComfyUI connectivity

## Troubleshooting Installation

### Add-on doesn't appear in Blender
- Ensure you selected the correct `__init__.py` file
- Check Blender version compatibility (3.0+)
- Look for error messages in Blender's console: `Window > Toggle System Console`

### Connection test fails
- Verify ComfyUI is running
- Check the server address in preferences
- Try accessing ComfyUI web interface manually
- Check firewall settings

### Import errors
- Ensure all files are in the same folder
- Check for missing dependencies
- Review error messages in Blender's console

### OpenCV installation issues
- Make sure you're using Blender's Python, not system Python
- Try installing with `--user` flag: `pip install --user opencv-python`
- Check Blender's Python version compatibility

## Next Steps

After successful installation:
1. Read the [README.md](README.md) for usage instructions
2. Prepare a rigged 3D model
3. Set up your ComfyUI workflow
4. Try generating your first pose!

## Getting Help

If you encounter issues:
1. Check the console output in Blender
2. Verify ComfyUI is running and accessible
3. Review the workflow JSON format
4. Ensure all requirements are met
5. Check file permissions for addon folder

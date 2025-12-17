# Quick Start Guide - AI Pose Generator

Get up and running with AI-powered pose generation in 5 minutes!

## Prerequisites Checklist

- [ ] Blender 3.0+ installed
- [ ] ComfyUI server running
- [ ] Qwen Image Edit model in ComfyUI
- [ ] A rigged 3D model ready

## Step 1: Install ComfyUI (5 minutes)

If you don't have ComfyUI yet:

```bash
# Clone and setup
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
pip install -r requirements.txt

# Start server
python main.py
```

ComfyUI should be accessible at: `http://localhost:8188`

## Step 2: Install the Add-on (2 minutes)

1. Download the add-on files
2. Open Blender
3. Go to: `Edit > Preferences > Add-ons > Install...`
4. Select: `blender_addon/__init__.py`
5. ✓ Check the box to enable "AI Pose Generator"

## Step 3: Configure Connection (1 minute)

1. In add-on preferences, set ComfyUI server:
   - Default: `http://localhost:8188`
   - Remote: `http://your-server-ip:8188`

2. Test connection:
   - Open 3D Viewport sidebar (press `N`)
   - Click "AI Pose" tab
   - Expand "ComfyUI Connection"
   - Click "Test Connection"
   - ✓ Should see "Connected successfully"

## Step 4: Load Workflow (1 minute)

1. In the "AI Pose" panel:
   - Expand "ComfyUI Workflow"
   - Click "Load Workflow JSON"
   - Select `example_workflow.json`
   - ✓ Should see "Loaded: example_workflow.json"

## Step 5: Generate Your First Pose (2 minutes)

1. **Select Model**:
   - Target Model: Choose your mesh object
   - Armature: Choose your armature

2. **Enter Pose**:
   - Type a pose description, e.g., "running"

3. **Generate**:
   - Click "Generate Pose"
   - Wait 1-2 minutes for processing
   - ✓ Pose will be automatically applied!

## Quick Example

Let's create a simple test:

```python
import bpy

# 1. Create a basic armature
bpy.ops.object.armature_add()
armature = bpy.context.active_object

# 2. Create a mesh
bpy.ops.mesh.primitive_uv_sphere_add()
mesh = bpy.context.active_object

# 3. Set up the add-on
scene = bpy.context.scene
scene.ai_pose_target_object = mesh
scene.ai_pose_armature = armature
scene.ai_pose_prompt = "jumping"

# 4. Make sure workflow is loaded
scene.ai_pose_workflow_path = "/path/to/example_workflow.json"

# 5. Generate (via UI or operator)
# bpy.ops.aipose.generate_pose()
```

## Common First-Time Issues

### "Connection Failed"
**Solution**: Make sure ComfyUI is running
```bash
# In ComfyUI directory
python main.py
```

### "No workflow loaded"
**Solution**: Load the workflow JSON file
- Use the "Load Workflow JSON" button in the UI
- Or set path: `scene.ai_pose_workflow_path = "/path/to/workflow.json"`

### "Please select an armature"
**Solution**: Your model needs a proper rig
- Model must have an armature
- Armature must be bound to mesh
- Select both in the UI

### "Timeout waiting for ComfyUI"
**Solution**: First run takes longer
- ComfyUI loads models on first use
- Subsequent runs will be faster
- Check ComfyUI console for progress

## Usage Tips

### Best Practices

1. **Start Simple**
   - Use simple poses first: "standing", "sitting", "walking"
   - Progress to complex poses: "backflip", "dancing"

2. **Rest Pose Matters**
   - Start with T-pose or A-pose
   - Neutral pose gives best results

3. **Bone Visibility**
   - Keep "Show Bones in Render" checked
   - AI needs to see bone structure

4. **Resolution**
   - 1024 is good for most cases
   - Higher = better quality but slower
   - Lower = faster but less accurate

### Workflow Tips

1. **Test Connection First**
   - Always test before generating
   - Saves time if server is down

2. **Load Workflow Once**
   - Workflow persists in scene
   - No need to reload each time

3. **Use Reset Pose**
   - Return to rest pose anytime
   - Good for trying multiple poses

4. **Save Your Work**
   - Save .blend file before generating
   - Processing can take time

## Example Workflow

Here's a typical session:

```
1. Open Blender with rigged model
2. Press N → Click "AI Pose" tab
3. Test Connection → ✓
4. Load Workflow → ✓
5. Select Model → Select Armature → ✓
6. Type "running" → Generate → ✓
7. Wait 2 minutes
8. Pose applied! Try another:
9. Type "jumping" → Generate → ✓
10. Not happy? Reset Pose → Try again
```

## Keyboard Shortcuts

While no custom shortcuts by default, you can add them:

```python
# In Blender preferences > Keymap
# Add new shortcut for:
bpy.ops.aipose.generate_pose()  # e.g., Ctrl+Shift+P
bpy.ops.aipose.reset_pose()     # e.g., Ctrl+Shift+R
```

## Next Steps

Once you're comfortable with basics:

1. **Create Custom Workflows**
   - Design in ComfyUI
   - Export as JSON
   - Load in Blender

2. **Experiment with Prompts**
   - Try different poses
   - Combine actions: "running and waving"
   - Add style: "dynamic jumping pose"

3. **Adjust Settings**
   - Try different resolutions
   - Test with/without bone visibility
   - Experiment with render angles

4. **Batch Processing**
   - Generate multiple poses
   - Build pose library
   - Create animation sequences

## Video Tutorial Outline

If creating a video tutorial:

1. **Intro** (0:00-0:30)
   - Show final result
   - Explain what the add-on does

2. **Installation** (0:30-2:00)
   - Show ComfyUI setup
   - Install add-on in Blender

3. **Configuration** (2:00-3:30)
   - Test connection
   - Load workflow

4. **First Pose** (3:30-5:30)
   - Select model/armature
   - Enter prompt
   - Generate and show result

5. **Tips & Tricks** (5:30-7:00)
   - Multiple poses
   - Reset function
   - Troubleshooting

## Support Resources

- **README.md**: Full documentation
- **INSTALLATION.md**: Detailed installation
- **CONFIGURATION.md**: Advanced settings
- **ARCHITECTURE.md**: Technical details

## Community Examples

Share your results! Example prompts that work well:

**Action Poses**:
- "running fast"
- "jumping high"
- "kicking"
- "punching"

**Everyday Poses**:
- "sitting on chair"
- "waving hello"
- "thinking pose"
- "relaxed standing"

**Dynamic Poses**:
- "dancing"
- "martial arts stance"
- "yoga tree pose"
- "superhero landing"

**Character Poses**:
- "sneaking"
- "celebrating victory"
- "reaching for something"
- "looking around corner"

## Troubleshooting Quick Reference

| Problem | Quick Fix |
|---------|-----------|
| Connection fails | Start ComfyUI server |
| Slow generation | First run loads models (normal) |
| Pose not applied | Check console for errors |
| Wrong pose | Try clearer prompt |
| No bones visible | Enable "Show Bones in Render" |

## Getting Help

1. Check error message in status display
2. Look at Blender console: `Window > Toggle System Console`
3. Check ComfyUI console for server errors
4. Review configuration settings
5. Try with example workflow first

## Success!

You should now be generating AI-powered poses! 

**Remember**: 
- Start simple
- Test connection first
- Be patient (first run is slower)
- Experiment with prompts

Happy posing! 🎨🤖

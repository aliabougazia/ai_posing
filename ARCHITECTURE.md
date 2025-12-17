# AI Pose Generator - Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Blender Add-on                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐         ┌──────────────┐                 │
│  │  UI Panel    │────────▶│  Operators   │                 │
│  │ (ui_panel.py)│         │(operators.py)│                 │
│  └──────────────┘         └───────┬──────┘                 │
│                                    │                         │
│                                    ▼                         │
│  ┌──────────────┐         ┌──────────────┐                 │
│  │ Preferences  │         │   Render     │                 │
│  │(preferences) │         │   Utils      │                 │
│  └──────────────┘         │(render_utils)│                 │
│                           └──────┬───────┘                 │
│                                  │                          │
│  ┌──────────────┐         ┌──────▼──────┐                 │
│  │  Workflow    │         │  ComfyUI    │                 │
│  │  Manager     │────────▶│   Client    │                 │
│  │(workflow_mgr)│         │(comfyui_    │                 │
│  └──────────────┘         │  client.py) │                 │
│                           └──────┬───────┘                 │
│                                  │                          │
│  ┌──────────────┐                │                         │
│  │    Pose      │◀───────────────┘                         │
│  │  Processor   │                                          │
│  │(pose_        │                                          │
│  │ processor.py)│                                          │
│  └──────────────┘                                          │
│                                                             │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │ HTTP/REST API
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    ComfyUI Server                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐         ┌──────────────┐                 │
│  │   Workflow   │────────▶│  Image Edit  │                 │
│  │   Engine     │         │    Model     │                 │
│  │              │         │   (Qwen)     │                 │
│  └──────────────┘         └──────────────┘                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Component Overview

### 1. UI Layer (`ui_panel.py`)
- **Purpose**: Provides user interface in Blender's 3D Viewport sidebar
- **Components**:
  - Main Panel: Model selection, pose prompt, render settings
  - Workflow Panel: Workflow JSON management
  - Connection Panel: ComfyUI server settings
  - Help Panel: Instructions and tips
- **Interactions**: Triggers operators when buttons are clicked

### 2. Operators (`operators.py`)
- **Purpose**: Handles user actions and orchestrates the pose generation process
- **Key Operators**:
  - `AIPOSE_OT_TestConnection`: Tests ComfyUI connectivity
  - `AIPOSE_OT_LoadWorkflow`: Loads workflow JSON files
  - `AIPOSE_OT_GeneratePose`: Main pose generation operator
  - `AIPOSE_OT_ResetPose`: Resets armature to rest pose
- **Responsibilities**:
  - Input validation
  - Process coordination
  - Error handling
  - User feedback

### 3. Rendering System (`render_utils.py`)
- **Purpose**: Captures model views with visible armature
- **Key Functions**:
  - `render_both_views()`: Main rendering function
  - `setup_camera_for_view()`: Camera positioning
  - `create_bone_mesh_overlay()`: Creates visible bone representation
  - `frame_object_in_camera()`: Auto-framing
- **Features**:
  - Dual-view rendering (front and side)
  - Temporary camera creation
  - Bone visualization with emission shader
  - Non-destructive (restores original settings)

### 4. ComfyUI Client (`comfyui_client.py`)
- **Purpose**: Handles all communication with ComfyUI server
- **Key Methods**:
  - `test_connection()`: Health check
  - `upload_image()`: Upload images to ComfyUI
  - `queue_prompt()`: Submit workflow for execution
  - `wait_for_completion()`: Poll for results
  - `get_image()`: Download output images
- **Features**:
  - RESTful API communication
  - Multipart form data handling
  - Polling with timeout
  - Error handling and retry logic

### 5. Workflow Manager (`workflow_manager.py`)
- **Purpose**: Manages ComfyUI workflow JSON files
- **Key Functions**:
  - `load_workflow()`: Parse and validate JSON
  - `update_workflow_inputs()`: Inject images and prompts
  - `validate_workflow_structure()`: Structure validation
  - `get_workflow_info()`: Extract workflow metadata
- **Features**:
  - JSON parsing and validation
  - Dynamic input injection
  - Workflow inspection

### 6. Pose Processor (`pose_processor.py`)
- **Purpose**: Extracts poses from images and applies to armature
- **Key Functions**:
  - `process_ai_generated_images()`: Main processing pipeline
  - `detect_bone_positions()`: Bone detection in images
  - `extract_bone_structure()`: 3D reconstruction from 2D views
  - `apply_pose_to_armature()`: Apply extracted pose
- **Algorithm**:
  1. Load images as numpy arrays
  2. Detect bone positions (red channel thresholding)
  3. Reconstruct 3D positions from front/side views
  4. Match detected bones to armature bones
  5. Calculate rotation quaternions
  6. Apply transformations in pose mode

### 7. Preferences (`preferences.py`)
- **Purpose**: Stores user preferences and settings
- **Settings**:
  - ComfyUI server address
  - Default workflow path
- **Integration**: Accessible from all modules via `get_addon_preferences()`

## Data Flow

### Pose Generation Process

```
1. User Input
   ├─ Model selection
   ├─ Armature selection
   ├─ Pose prompt
   └─ Workflow JSON

2. Rendering Phase
   ├─ Setup cameras (front/side)
   ├─ Create bone overlays
   ├─ Render with bone visibility
   └─ Save temporary images

3. Upload Phase
   ├─ Read rendered images
   ├─ Upload to ComfyUI
   └─ Get upload confirmation

4. Processing Phase
   ├─ Load workflow JSON
   ├─ Update with inputs
   ├─ Queue prompt
   ├─ Wait for completion
   └─ Poll for status

5. Download Phase
   ├─ Get result history
   ├─ Extract image info
   ├─ Download posed images
   └─ Save locally

6. Pose Extraction
   ├─ Load all 4 images (rest + posed)
   ├─ Detect bones in each
   ├─ Reconstruct 3D structure
   ├─ Match to armature
   └─ Calculate rotations

7. Application
   ├─ Enter pose mode
   ├─ Apply rotations
   ├─ Update viewport
   └─ Exit pose mode
```

## Key Design Decisions

### 1. Dual-View Approach
- **Rationale**: Single view is ambiguous for 3D reconstruction
- **Implementation**: Orthogonal cameras (front and side)
- **Trade-off**: More processing time vs. better accuracy

### 2. Bone Visualization
- **Rationale**: AI needs to "see" bone structure to pose correctly
- **Implementation**: Red emission shader overlay
- **Trade-off**: Requires specific detection logic

### 3. Workflow Flexibility
- **Rationale**: Different users may want different models/settings
- **Implementation**: JSON-based workflow system
- **Trade-off**: Users need to understand ComfyUI workflows

### 4. Synchronous Processing
- **Rationale**: Easier to implement and debug
- **Implementation**: Blocking operations with status updates
- **Trade-off**: UI freezes during processing (could be improved)

### 5. Simplified Bone Matching
- **Rationale**: Complex CV algorithms would require heavy dependencies
- **Implementation**: Heuristic-based matching
- **Trade-off**: Less accurate but more portable

## Extension Points

### Adding New Detection Methods
1. Modify `detect_bone_positions()` in `pose_processor.py`
2. Implement custom detection algorithm
3. Return list of (x, y) positions

### Adding New Visualization Methods
1. Modify `create_bone_mesh_overlay()` in `render_utils.py`
2. Create custom mesh/material
3. Ensure visibility in renders

### Adding New Workflow Types
1. Create workflow JSON following ComfyUI format
2. Ensure nodes are named consistently
3. Load via UI panel

### Adding Background Processing
1. Modify operators to use threading
2. Implement progress callbacks
3. Update UI asynchronously

## Performance Considerations

### Bottlenecks
1. **ComfyUI Processing**: 30-120 seconds depending on model
2. **Image Upload**: 1-5 seconds depending on resolution
3. **Rendering**: 2-10 seconds per view
4. **Bone Detection**: 1-3 seconds per image

### Optimization Opportunities
1. Cache rendered views if rest pose doesn't change
2. Parallel processing of front/side views
3. GPU-accelerated bone detection
4. WebSocket for real-time ComfyUI updates
5. Async operations with progress indicators

## Security Considerations

1. **Network**: HTTP traffic is unencrypted (consider HTTPS for production)
2. **File Access**: Validates file paths but trusts JSON content
3. **Server Trust**: Assumes ComfyUI server is trusted
4. **Temporary Files**: Creates temp files (cleaned up after use)

## Future Enhancements

### Short Term
- Better error messages
- Progress bars for long operations
- Workflow validation against ComfyUI schema
- Undo/redo support for poses

### Medium Term
- Multiple pose generation (batch)
- Pose library system
- Animation timeline integration
- Better bone correspondence algorithm

### Long Term
- Real-time pose preview
- Machine learning-based bone detection
- Multi-view reconstruction (>2 views)
- Integration with motion capture data
- Support for facial rigging

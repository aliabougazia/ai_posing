"""
Workflow manager for loading and managing ComfyUI workflows
"""

import json
import os
from typing import Dict, Optional, Tuple


class WorkflowManager:
    """Manages ComfyUI workflow JSON files"""
    
    @staticmethod
    def load_workflow(filepath: str) -> Tuple[Optional[Dict], str]:
        """
        Load a ComfyUI workflow from JSON file
        
        Args:
            filepath: Path to workflow JSON file
            
        Returns:
            Tuple of (workflow_dict, error_message)
        """
        if not filepath:
            return None, "No workflow file specified"
        
        if not os.path.exists(filepath):
            return None, f"Workflow file not found: {filepath}"
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                workflow = json.load(f)
            
            # Basic validation
            if not isinstance(workflow, dict):
                return None, "Invalid workflow format: root must be a dictionary"
            
            return workflow, ""
            
        except json.JSONDecodeError as e:
            return None, f"JSON parsing error: {str(e)}"
        except Exception as e:
            return None, f"Error loading workflow: {str(e)}"
    
    @staticmethod
    def save_workflow(workflow: Dict, filepath: str) -> Tuple[bool, str]:
        """
        Save a workflow to JSON file
        
        Args:
            workflow: Workflow dictionary
            filepath: Path to save to
            
        Returns:
            Tuple of (success, error_message)
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(workflow, f, indent=2)
            return True, ""
        except Exception as e:
            return False, f"Error saving workflow: {str(e)}"
    
    @staticmethod
    def update_workflow_inputs(workflow: Dict, 
                              front_image_path: str, 
                              side_image_path: str,
                              prompt: str) -> Dict:
        """
        Update workflow with input images and prompt
        This assumes a specific workflow structure - may need customization
        
        Args:
            workflow: Original workflow dictionary
            front_image_path: Path to front view image
            side_image_path: Path to side view image
            prompt: Pose prompt text
            
        Returns:
            Updated workflow dictionary
        """
        # Make a deep copy to avoid modifying original
        import copy
        updated = copy.deepcopy(workflow)
        
        # Search for image input nodes and text nodes
        # This is a simplified approach - actual implementation would need to be
        # customized based on the specific workflow structure
        
        for node_id, node_data in updated.items():
            if not isinstance(node_data, dict):
                continue
            
            class_type = node_data.get('class_type', '')
            inputs = node_data.get('inputs', {})
            
            # Look for image load nodes
            if 'LoadImage' in class_type or 'Image' in class_type:
                # Try to determine if this is for front or side view
                # This is heuristic and may need adjustment
                title = node_data.get('_meta', {}).get('title', '').lower()
                if 'front' in title or node_id == '1':
                    if 'image' in inputs:
                        inputs['image'] = os.path.basename(front_image_path)
                elif 'side' in title or node_id == '2':
                    if 'image' in inputs:
                        inputs['image'] = os.path.basename(side_image_path)
            
            # Look for text/prompt nodes
            if 'Text' in class_type or 'Prompt' in class_type or 'String' in class_type:
                if 'text' in inputs:
                    inputs['text'] = prompt
                elif 'prompt' in inputs:
                    inputs['prompt'] = prompt
                elif 'string' in inputs:
                    inputs['string'] = prompt
        
        return updated
    
    @staticmethod
    def validate_workflow_structure(workflow: Dict) -> Tuple[bool, str]:
        """
        Validate that workflow has required structure
        
        Args:
            workflow: Workflow dictionary
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(workflow, dict):
            return False, "Workflow must be a dictionary"
        
        if len(workflow) == 0:
            return False, "Workflow is empty"
        
        # Check that nodes have required fields
        for node_id, node_data in workflow.items():
            if not isinstance(node_data, dict):
                continue
            
            if 'class_type' not in node_data:
                return False, f"Node {node_id} missing 'class_type' field"
            
            if 'inputs' not in node_data:
                return False, f"Node {node_id} missing 'inputs' field"
        
        return True, ""
    
    @staticmethod
    def get_workflow_info(workflow: Dict) -> str:
        """
        Get human-readable information about workflow
        
        Args:
            workflow: Workflow dictionary
            
        Returns:
            Information string
        """
        if not isinstance(workflow, dict):
            return "Invalid workflow"
        
        node_types = {}
        for node_data in workflow.values():
            if isinstance(node_data, dict):
                class_type = node_data.get('class_type', 'Unknown')
                node_types[class_type] = node_types.get(class_type, 0) + 1
        
        info_lines = [
            f"Total nodes: {len(workflow)}",
            "Node types:"
        ]
        
        for class_type, count in sorted(node_types.items()):
            info_lines.append(f"  - {class_type}: {count}")
        
        return "\n".join(info_lines)


def register():
    """Register module"""
    pass


def unregister():
    """Unregister module"""
    pass

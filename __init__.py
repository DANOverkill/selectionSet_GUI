bl_info = {
    "name": "Selection Set Panel - DEV",
    "author": "DANOverkill",
    "version": (2, 0, 0),
    "blender": (2, 80, 0),
    "category": "Object",
}

import bpy
import os
from datetime import datetime

#defining boolean to track activation of removal mode (default as false)
def register_properties():
    bpy.types.Scene.selection_set_remove_mode = bpy.props.BoolProperty(
        name="Selection Set Remove Mode",
        description="Toggle removal mode to show delete buttons next to each set",
        default=False
    )
    bpy.types.Scene.selection_set_edit_mode = bpy.props.BoolProperty(
        name="Edit Mode",
        description="Show reorder arrows for selection sets",
        default=False
    )
    bpy.types.Scene.selection_set_modify_mode = bpy.props.BoolProperty(
        name="Bones Edit Mode",
        description="Show +/- signs for adding or removing selected bones from selection sets",
        default=False
    )
    bpy.types.Scene.selection_set_rename_mode = bpy.props.BoolProperty(
        name="Rename Mode",
        description="Show pencil icon to rename selection sets",
        default=False
    ) 

def unregister_properties():
    del bpy.types.Scene.selection_set_remove_mode
    del bpy.types.Scene.selection_set_edit_mode
    del bpy.types.Scene.selection_set_modify_mode
    del bpy.types.Scene.selection_set_rename_mode 

class SelectionSetOperator(bpy.types.Operator):
    bl_idname = "object.selection_set_operator"
    bl_label = "Select Set"
    
    set_name: bpy.props.StringProperty()

    def invoke(self, context, event):
        self.shift_held = event.shift
        self.ctrl_held = event.ctrl
        return self.execute(context)
    
    def execute(self, context):
        obj = context.object
        selection_set_name = self.set_name

        # Ensure we're in Pose mode
        if context.mode == 'POSE':

                # Deselect all bones first if shift is NOT selected.
                if not self.shift_held and not self.ctrl_held:
                    bpy.ops.pose.select_all(action='DESELECT')
            
                # Access linked data
                if hasattr(obj, 'proxy') and obj.proxy:
                    obj = obj.proxy

                # Debugging: Print selection set details
                if hasattr(obj, 'selection_sets'):
                    selection_set = obj.selection_sets.get(selection_set_name)
                    bone_list = []
                    
                    for bone_id in selection_set['bone_ids']:
                        bone_list.append(bone_id['name'])
                    
                    if isinstance(bone_list, list):
                        for bone_name in bone_list:
                            bone = obj.pose.bones.get(bone_name)
                            if bone:
                                if self.ctrl_held:
                                    bone.bone.select = False
                                else:
                                    bone.bone.select = True
                            else:
                                print(f"Bone not found: {bone_name}")
                    else:
                        self.report({'ERROR'}, f"Selection set '{selection_set_name}' is not iterable or not in expected format.")
                else:
                    self.report({'ERROR'}, "Object has no selection sets.")
        else:
            self.report({'ERROR'}, "Not in Pose mode.")
        
        return {'FINISHED'}

class ExportSelectionSetsOperator(bpy.types.Operator):
    bl_idname = "pose.export_selection_sets"
    bl_label = "Export Selection Sets"
    bl_description = "Export all selection sets to a text file"
    
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def invoke(self, context, event):
        obj = context.object
        if obj and obj.type == 'ARMATURE':
            base_name = obj.name
        else:
            base_name = "selection_sets"
        
        # Sanitize the name (optional but safe)
        safe_name = "".join(c for c in base_name if c.isalnum() or c in "._- ")
        self.filepath = f"{safe_name}_selection_sets.json"
        
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        obj = context.object
        if context.mode != 'POSE':
            self.report({'ERROR'}, "Must be in Pose mode")
            return {'CANCELLED'}

        if hasattr(obj, 'proxy') and obj.proxy:
            obj = obj.proxy

        if not hasattr(obj, 'selection_sets') or len(obj.selection_sets) == 0:
            self.report({'ERROR'}, "No selection sets to export")
            return {'CANCELLED'}

        # Select all selection sets
        for i, _ in enumerate(obj.selection_sets):
            obj.selection_sets[i].is_selected = True

        # Copy to clipboard
        bpy.ops.pose.selection_set_copy()

        # Write clipboard content to file
        filepath = self.filepath
        if not os.path.splitext(filepath)[1]:
            filepath += '.json'

        try:
            clipboard_text = context.window_manager.clipboard
            header = f"# Selection Sets exported from {obj.name} on {datetime.now()}\n"
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(clipboard_text)
            self.report({'INFO'}, f"Exported to {filepath}")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to write file: {e}")
            return {'CANCELLED'}

        return {'FINISHED'}


class ImportSelectionSetsOperator(bpy.types.Operator):
    bl_idname = "pose.import_selection_sets"
    bl_label = "Import Selection Sets"
    bl_description = "Import selection sets from a text file"
    
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        obj = context.object
        if context.mode != 'POSE':
            self.report({'ERROR'}, "Must be in Pose mode")
            return {'CANCELLED'}

        if hasattr(obj, 'proxy') and obj.proxy:
            obj = obj.proxy

        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                clipboard_text = f.read()
        except Exception as e:
            self.report({'ERROR'}, f"Could not read file: {e}")
            return {'CANCELLED'}

        # Set clipboard and paste
        context.window_manager.clipboard = clipboard_text
        bpy.ops.pose.selection_set_paste()

        self.report({'INFO'}, f"Imported from {self.filepath}")
        return {'FINISHED'}


class RemoveAllSelectionSetsOperator(bpy.types.Operator):
    bl_idname = "pose.remove_all_selection_sets"
    bl_label = "Remove All Selection Sets"
    bl_description = "Delete every selection set on the current object"

    def execute(self, context):
        obj = context.object
        if context.mode != 'POSE':
            self.report({'ERROR'}, "Must be in Pose mode")
            return {'CANCELLED'}

        if hasattr(obj, 'proxy') and obj.proxy:
            obj = obj.proxy

        if not hasattr(obj, 'selection_sets') or len(obj.selection_sets) == 0:
            self.report({'WARNING'}, "No selection sets to remove")
            return {'CANCELLED'}

        # Select all sets
        for i, _ in enumerate(obj.selection_sets):
            obj.selection_sets[i].is_selected = True

        # Remove them one by one (the active index changes after each removal)
        # We'll iterate from the last to first to avoid index shifting issues
        for i in range(len(obj.selection_sets) - 1, -1, -1):
            obj.active_selection_set = i
            bpy.ops.pose.selection_set_remove()

        self.report({'INFO'}, "All selection sets removed")
        return {'FINISHED'}

class NewSelectionSetOperator(bpy.types.Operator):
    bl_idname = "pose.new_selection_set"
    bl_label = "New Selection Set"
    bl_description = "Create a new selection set from selected bones"
    bl_options = {'REGISTER', 'UNDO'}

    set_name: bpy.props.StringProperty(
        name="Name",
        default="NewSet",
        description="Name for the new selection set"
    )

    def invoke(self, context, event):
        # Show a dialog to let the user enter a name
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        obj = context.object

        # Safety checks
        if context.mode != 'POSE':
            self.report({'ERROR'}, "Must be in Pose mode")
            return {'CANCELLED'}

        if hasattr(obj, 'proxy') and obj.proxy:
            obj = obj.proxy

        if not hasattr(obj, 'selection_sets'):
            self.report({'ERROR'}, "Object does not support selection sets")
            return {'CANCELLED'}

        # Ensure at least one bone is selected (optional but good UX)
        if not context.selected_pose_bones:
            self.report({'WARNING'}, "No bones selected – creating empty set")

        # 1. Create new selection set
        bpy.ops.pose.selection_set_add()

        # 2. The new set becomes the active one; get its index
        new_index = obj.active_selection_set
        if new_index < 0:
            self.report({'ERROR'}, "Failed to create selection set")
            return {'CANCELLED'}

        # 3. Rename it
        obj.selection_sets[new_index].name = self.set_name

        # 4. Assign selected bones
        bpy.ops.pose.selection_set_assign()

        self.report({'INFO'}, f"Created set '{self.set_name}'")
        return {'FINISHED'}
    
class RemoveSelectionSetOperator(bpy.types.Operator):
    bl_idname = "pose.remove_selection_set"
    bl_label = "Remove Selection Set"
    bl_description = "Delete a specific selection set"
    bl_options = {'REGISTER', 'UNDO'}

    set_name: bpy.props.StringProperty(name="Set Name")

    def invoke(self, context, event):
        # Show confirmation dialog with the set name in the title/message
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        obj = context.object

        # Safety checks (should already be in Pose mode from panel context)
        if context.mode != 'POSE':
            self.report({'ERROR'}, "Must be in Pose mode")
            return {'CANCELLED'}

        if hasattr(obj, 'proxy') and obj.proxy:
            obj = obj.proxy

        if not hasattr(obj, 'selection_sets'):
            self.report({'ERROR'}, "Object has no selection sets")
            return {'CANCELLED'}

        # Find the set by name
        set_index = obj.selection_sets.find(self.set_name)
        if set_index < 0:
            self.report({'ERROR'}, f"Set '{self.set_name}' not found")
            return {'CANCELLED'}

        # Set it as active and remove it
        obj.active_selection_set = set_index
        bpy.ops.pose.selection_set_remove()

        self.report({'INFO'}, f"Removed '{self.set_name}'")
        return {'FINISHED'}
    
class AssignToSelectionSetOperator(bpy.types.Operator):
    bl_idname = "pose.assign_to_selection_set"
    bl_label = "Assign Bones"
    bl_description = "Add selected bones to this selection set"
    bl_options = {'REGISTER', 'UNDO'}

    set_name: bpy.props.StringProperty(name="Set Name")

    def execute(self, context):
        obj = context.object
        if context.mode != 'POSE':
            self.report({'ERROR'}, "Must be in Pose mode")
            return {'CANCELLED'}

        if hasattr(obj, 'proxy') and obj.proxy:
            obj = obj.proxy

        if not context.selected_pose_bones:
            self.report({'WARNING'}, "No bones selected")
            return {'CANCELLED'}

        set_index = obj.selection_sets.find(self.set_name)
        if set_index < 0:
            self.report({'ERROR'}, f"Set '{self.set_name}' not found")
            return {'CANCELLED'}

        obj.active_selection_set = set_index
        bpy.ops.pose.selection_set_assign()
        self.report({'INFO'}, f"Assigned bones to '{self.set_name}'")
        return {'FINISHED'}
    
class UnassignFromSelectionSetOperator(bpy.types.Operator):
    bl_idname = "pose.unassign_from_selection_set"
    bl_label = "Unassign Bones"
    bl_description = "Remove selected bones from this selection set"
    bl_options = {'REGISTER', 'UNDO'}

    set_name: bpy.props.StringProperty(name="Set Name")

    def execute(self, context):
        obj = context.object
        if context.mode != 'POSE':
            self.report({'ERROR'}, "Must be in Pose mode")
            return {'CANCELLED'}

        if hasattr(obj, 'proxy') and obj.proxy:
            obj = obj.proxy

        if not context.selected_pose_bones:
            self.report({'WARNING'}, "No bones selected")
            return {'CANCELLED'}

        set_index = obj.selection_sets.find(self.set_name)
        if set_index < 0:
            self.report({'ERROR'}, f"Set '{self.set_name}' not found")
            return {'CANCELLED'}

        obj.active_selection_set = set_index
        bpy.ops.pose.selection_set_unassign()
        self.report({'INFO'}, f"Unassigned bones from '{self.set_name}'")
        return {'FINISHED'}

class RenameSelectionSetOperator(bpy.types.Operator):
    bl_idname = "pose.rename_selection_set"
    bl_label = "Rename Selection Set"
    bl_description = "Change the name of this selection set"
    bl_options = {'REGISTER', 'UNDO'}

    set_name: bpy.props.StringProperty(name="Current Set Name")
    new_name: bpy.props.StringProperty(
        name="New Name",
        default="",
        description="Enter a new name for the selection set"
    )

    def invoke(self, context, event):
        # Pre-fill the new name with the current set name
        self.new_name = self.set_name
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        obj = context.object
        if context.mode != 'POSE':
            self.report({'ERROR'}, "Must be in Pose mode")
            return {'CANCELLED'}

        if hasattr(obj, 'proxy') and obj.proxy:
            obj = obj.proxy

        if not self.new_name.strip():
            self.report({'ERROR'}, "Name cannot be empty")
            return {'CANCELLED'}

        set_index = obj.selection_sets.find(self.set_name)
        if set_index < 0:
            self.report({'ERROR'}, f"Set '{self.set_name}' not found")
            return {'CANCELLED'}

        # Check if the new name already exists (optional but good practice)
        if self.new_name in obj.selection_sets.keys() and self.new_name != self.set_name:
            self.report({'ERROR'}, f"Set '{self.new_name}' already exists")
            return {'CANCELLED'}

        obj.selection_sets[set_index].name = self.new_name
        self.report({'INFO'}, f"Renamed '{self.set_name}' to '{self.new_name}'")
        return {'FINISHED'}

# ============= Toggle Operators ====================
class ToggleRemoveModeOperator(bpy.types.Operator):
    bl_idname = "pose.toggle_remove_mode"
    bl_label = "Toggle Remove Mode"
    bl_description = "Show/hide remove buttons for selection sets"
    bl_options = {'REGISTER'}

    def execute(self, context):
        context.scene.selection_set_remove_mode = not context.scene.selection_set_remove_mode
        # Force UI redraw
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
        return {'FINISHED'}
    
class MoveSelectionSetOperator(bpy.types.Operator):
    bl_idname = "pose.move_selection_set"
    bl_label = "Move Selection Set"
    bl_description = "Move the selection set up or down in the list"
    bl_options = {'REGISTER', 'UNDO'}

    set_name: bpy.props.StringProperty(name="Set Name")
    direction: bpy.props.EnumProperty(
        items=[
            ('UP', "Up", ""),
            ('DOWN', "Down", ""),
        ],
        name="Direction"
    )

    def execute(self, context):
        obj = context.object

        # Safety checks
        if context.mode != 'POSE':
            self.report({'ERROR'}, "Must be in Pose mode")
            return {'CANCELLED'}

        if hasattr(obj, 'proxy') and obj.proxy:
            obj = obj.proxy

        if not hasattr(obj, 'selection_sets'):
            self.report({'ERROR'}, "Object has no selection sets")
            return {'CANCELLED'}

        # Find the set index
        set_index = obj.selection_sets.find(self.set_name)
        if set_index < 0:
            self.report({'ERROR'}, f"Set '{self.set_name}' not found")
            return {'CANCELLED'}

        # Set it as active and move
        obj.active_selection_set = set_index
        bpy.ops.pose.selection_set_move(direction=self.direction)

        return {'FINISHED'}
    
class ToggleEditModeOperator(bpy.types.Operator):
    bl_idname = "pose.toggle_edit_mode"
    bl_label = "Toggle Move Mode"
    bl_description = "Show/hide reorder arrows for selection sets"
    bl_options = {'REGISTER'}

    def execute(self, context):
        context.scene.selection_set_edit_mode = not context.scene.selection_set_edit_mode
        # Redraw UI
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
        return {'FINISHED'}
    
class ToggleModifyModeOperator(bpy.types.Operator):
    bl_idname = "pose.toggle_modify_mode"
    bl_label = "Toggle Modify Mode"
    bl_description = "Show/hide assign/unassign buttons for selection sets"
    bl_options = {'REGISTER'}

    def execute(self, context):
        context.scene.selection_set_modify_mode = not context.scene.selection_set_modify_mode
        # Redraw UI
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
        return {'FINISHED'}
    
class ToggleRenameModeOperator(bpy.types.Operator):
    bl_idname = "pose.toggle_rename_mode"
    bl_label = "Toggle Rename Mode"
    bl_description = "Show/hide rename buttons for selection sets"
    bl_options = {'REGISTER'}

    def execute(self, context):
        context.scene.selection_set_rename_mode = not context.scene.selection_set_rename_mode
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
        return {'FINISHED'}
#------------------------------------------------

# =============== Draw Panel ====================
class SelectionSetPanel(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_selection_set_panel"
    bl_label = "Selection Sets - DEV"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Selection Sets - DEV'

    def draw(self, context):
        layout = self.layout
        obj = context.object
        scene = context.scene
        
        if hasattr(obj, 'proxy') and obj.proxy:
            obj = obj.proxy
        
        if hasattr(obj, 'selection_sets'):
            selection_sets = obj.selection_sets.keys()
            for set_name in selection_sets:
                row = layout.row(align=True)
                op = row.operator("object.selection_set_operator", text=set_name)
                op.set_name = set_name
                if scene.selection_set_edit_mode:
                    # Up arrow draw
                    op_up = row.operator("pose.move_selection_set", text="", icon='TRIA_UP')
                    op_up.set_name = set_name
                    op_up.direction = 'UP'
                    # Down arrow draw
                    op_down = row.operator("pose.move_selection_set", text="", icon='TRIA_DOWN')
                    op_down.set_name = set_name
                    op_down.direction = 'DOWN'

                if scene.selection_set_remove_mode:    
                    #remove button draw                    
                    op_remove = row.operator("pose.remove_selection_set", text="", icon='X')
                    op_remove.set_name = set_name

                if scene.selection_set_modify_mode:
                    op_assign = row.operator("pose.assign_to_selection_set", text="", icon='ADD')
                    op_assign.set_name = set_name
                    op_unassign = row.operator("pose.unassign_from_selection_set", text="", icon='REMOVE')
                    op_unassign.set_name = set_name
                
                if scene.selection_set_rename_mode:
                    op_rename = row.operator("pose.rename_selection_set", text="", icon='GREASEPENCIL')
                    op_rename.set_name = set_name
                                
        else:
            layout.label(text="No selection sets found.")
        
        layout.separator()

        box = layout.box()
        box.label(text="Tools", icon='TOOL_SETTINGS')

        row = box.row(align=True)
        row.operator("pose.new_selection_set", text="New Set", icon='ADD')

        row = box.row(align=True)
        modify_on = scene.selection_set_modify_mode
        modify_icon = 'CHECKBOX_HLT' if modify_on else 'CHECKBOX_DEHLT'
        row.operator("pose.toggle_modify_mode", text="Add/Rem", icon=modify_icon)

        rename_mode_on = scene.selection_set_rename_mode
        rename_icon = 'CHECKBOX_HLT' if rename_mode_on else 'CHECKBOX_DEHLT'
        row.operator("pose.toggle_rename_mode", text="Rename", icon=rename_icon)
        
        edit_mode_on = scene.selection_set_edit_mode
        edit_icon = 'CHECKBOX_HLT' if edit_mode_on else 'CHECKBOX_DEHLT'
        row.operator("pose.toggle_edit_mode", text="Move", icon=edit_icon)

        remove_mode_on = scene.selection_set_remove_mode
        toggle_icon = 'CHECKBOX_HLT' if remove_mode_on else 'CHECKBOX_DEHLT'
        toggle_text = "Remove Mode" if remove_mode_on else "Remove Mode"
        row.operator("pose.toggle_remove_mode", text="Del", icon=toggle_icon)

        row = box.row(align=True)
        row.operator("pose.export_selection_sets", text="Export", icon='EXPORT')
        row.operator("pose.import_selection_sets", text="Import", icon='IMPORT')

        box.operator("pose.remove_all_selection_sets", text="Remove All", icon='TRASH')

def register():
    register_properties()
    bpy.utils.register_class(SelectionSetOperator)
    bpy.utils.register_class(ExportSelectionSetsOperator)
    bpy.utils.register_class(ImportSelectionSetsOperator)
    bpy.utils.register_class(RemoveAllSelectionSetsOperator)
    bpy.utils.register_class(NewSelectionSetOperator)
    bpy.utils.register_class(RemoveSelectionSetOperator)
    bpy.utils.register_class(ToggleRemoveModeOperator)
    bpy.utils.register_class(MoveSelectionSetOperator)
    bpy.utils.register_class(ToggleEditModeOperator)
    bpy.utils.register_class(ToggleModifyModeOperator)
    bpy.utils.register_class(AssignToSelectionSetOperator)
    bpy.utils.register_class(UnassignFromSelectionSetOperator)
    bpy.utils.register_class(ToggleRenameModeOperator)
    bpy.utils.register_class(RenameSelectionSetOperator)
    bpy.utils.register_class(SelectionSetPanel)

def unregister():
    unregister_properties()
    bpy.utils.unregister_class(SelectionSetOperator)
    bpy.utils.unregister_class(ExportSelectionSetsOperator)
    bpy.utils.unregister_class(ImportSelectionSetsOperator)
    bpy.utils.unregister_class(RemoveAllSelectionSetsOperator)
    bpy.utils.unregister_class(NewSelectionSetOperator)
    bpy.utils.unregister_class(RemoveSelectionSetOperator)
    bpy.utils.unregister_class(ToggleRemoveModeOperator)
    bpy.utils.unregister_class(MoveSelectionSetOperator)
    bpy.utils.unregister_class(ToggleEditModeOperator)
    bpy.utils.unregister_class(ToggleModifyModeOperator)
    bpy.utils.unregister_class(AssignToSelectionSetOperator)
    bpy.utils.unregister_class(UnassignFromSelectionSetOperator)
    bpy.utils.unregister_class(ToggleRenameModeOperator)
    bpy.utils.unregister_class(RenameSelectionSetOperator)
    bpy.utils.unregister_class(SelectionSetPanel)

if __name__ == "__main__":
    register()


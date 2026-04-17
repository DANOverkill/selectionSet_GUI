bl_info = {
    "name": "Dan's Selection Set Panel - TOOLS DEV",
    "author": "DANOverkill",
    "version": (2, 0, 0),
    "blender": (2, 80, 0),
    "category": "Object",
}

import bpy

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
    filename: bpy.props.StringProperty(name="File Name", default="selection_sets.txt")

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
        if not filepath.lower().endswith('.txt'):
            filepath += '.txt'

        try:
            clipboard_text = context.window_manager.clipboard
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

class SelectionSetPanel(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_selection_set_panel"
    bl_label = "Selection Sets - DEV"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Selection Sets - DEV'

    def draw(self, context):
        layout = self.layout
        obj = context.object
        
        if hasattr(obj, 'proxy') and obj.proxy:
            obj = obj.proxy
        
        if hasattr(obj, 'selection_sets'):
            selection_sets = obj.selection_sets.keys()
            for set_name in selection_sets:
                row = layout.row(align=True)
                op = row.operator("object.selection_set_operator", text=set_name)
                op.set_name = set_name
                op_remove = row.operator("pose.remove_selection_set", text="", icon='X')
                op_remove.set_name = set_name                

        else:
            layout.label(text="No selection sets found.")
        
        layout.separator()

        row = layout.row(align=True)
        row.operator("pose.new_selection_set", text="New Set", icon='ADD')
        #row.operator("pose.remove_selection_set", text="Remove Set", icon='REMOVE')

        row = layout.row(align=True)
        row.operator("pose.export_selection_sets", text="Export", icon='EXPORT')
        row.operator("pose.import_selection_sets", text="Import", icon='IMPORT')

        layout.operator("pose.remove_all_selection_sets", text="Remove All", icon='TRASH')

def register():
    bpy.utils.register_class(SelectionSetOperator)
    bpy.utils.register_class(NewSelectionSetOperator)
    # bpy.utils.register_class(RemoveSelectionSetOperator)
    bpy.utils.register_class(ExportSelectionSetsOperator)
    bpy.utils.register_class(ImportSelectionSetsOperator)
    bpy.utils.register_class(RemoveAllSelectionSetsOperator)
    bpy.utils.register_class(SelectionSetPanel)

def unregister():
    bpy.utils.register_class(SelectionSetOperator)
    bpy.utils.register_class(NewSelectionSetOperator)
    # bpy.utils.register_class(RemoveSelectionSetOperator)
    bpy.utils.register_class(ExportSelectionSetsOperator)
    bpy.utils.register_class(ImportSelectionSetsOperator)
    bpy.utils.register_class(RemoveAllSelectionSetsOperator)
    bpy.utils.register_class(SelectionSetPanel)

if __name__ == "__main__":
    register()


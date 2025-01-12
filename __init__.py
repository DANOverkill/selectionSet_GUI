bl_info = {
    "name": "Dan's Selection Set Panel",
    "author": "DANOverkill",
    "version": (1, 0, 0),
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

class SelectionSetPanel(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_selection_set_panel"
    bl_label = "Selection Sets"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Selection Sets'

    def draw(self, context):
        layout = self.layout
        obj = context.object
        
        # Access linked data
        if hasattr(obj, 'proxy') and obj.proxy:
            obj = obj.proxy
        
        # Fetch the selection sets directly
        if hasattr(obj, 'selection_sets'):
            selection_sets = obj.selection_sets.keys()
            for set_name in selection_sets:
                op = layout.operator("object.selection_set_operator", text=set_name)
                op.set_name = set_name
        else:
            layout.label(text="No selection sets found.")

def register():
    bpy.utils.register_class(SelectionSetOperator)
    bpy.utils.register_class(SelectionSetPanel)

def unregister():
    bpy.utils.unregister_class(SelectionSetOperator)
    bpy.utils.unregister_class(SelectionSetPanel)

if __name__ == "__main__":
    register()


import bpy

class MyPropertyGroup(bpy.types.PropertyGroup):

    age: bpy.props.IntProperty(name="Year of construction", min=1500, max=2050, default=(1970))
    usage: bpy.props.EnumProperty(
        name= "",
        description= "Building usage type",
        items= [('SFH', "Single-family house", ""),
                ('AB', "Apartments", ""),
                ('OTH', "Other building", "")
        ]
    )

class MyAddonProperties(bpy.types.PropertyGroup):
    def update_tick_box_1(self, context):
        if self.tick_box_1:
            self.tick_box_2 = False  # Uncheck the other option

    def update_tick_box_2(self, context):
        if self.tick_box_2:
            self.tick_box_1 = False  # Uncheck the other option

    tick_box_1: bpy.props.BoolProperty(
        name="Option 1",
        description="Select Option 1",
        default=False,
        update=update_tick_box_1
    )
    tick_box_2: bpy.props.BoolProperty(
        name="Option 2",
        description="Select Option 2",
        default=False,
        update=update_tick_box_2
    )

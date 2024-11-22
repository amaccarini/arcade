import bpy

class MyPropertyGroup(bpy.types.PropertyGroup):

    age: bpy.props.IntProperty(name="Year of construction", min=1500, max=2050, default=(1970))
    usage: bpy.props.EnumProperty(
        name= "",
        description= "Building usage type",
        items= [('detached', "Detached", ""),
                ('apartments', "Apartments", ""),
                ('terrace', "Terrace", "")
        ]
    )

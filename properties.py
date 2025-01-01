import bpy

class MyPropertyGroup(bpy.types.PropertyGroup):

    age: bpy.props.IntProperty(name="Age of construction", description="Archetype era", min=1500, max=2050, default=(1970))
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
        name="Probabilistic",
        description="Missing parameters (i.e. age, height and usage) are based on a probabilistic normal distribution.",
        default=False,
        update=update_tick_box_1
    )
    tick_box_2: bpy.props.BoolProperty(
        name="AI",
        description="Missing parameters (i.e. age, height and usage) are determined using AI-powered image recognition techniques.",
        default=False,
        update=update_tick_box_2
    )
    probability: bpy.props.FloatProperty(
        name="Probability",
        description="Set probability between 0 and 1",
        default=0.5,
        min=0.0,
        max=1.0
    )
    lon_min: bpy.props.FloatProperty(name="Min longitude", description="Minimum longitutide of the box containing the urban area", min=-180, max=180, default=(12.587832), precision=4)
    lat_max: bpy.props.FloatProperty(name="Max latitude", description="Maximum latitude of the box containing the urban area", min=-90, max=90, default=(55.649166), precision=4)
    lon_max: bpy.props.FloatProperty(name="Max longitude", description="Maximum longitutide of the box containing the urban area", min=-180, max=180, default=(12.589409), precision=4)
    lat_min: bpy.props.FloatProperty(name="Min latitude", description="Minimum latitude of the box containing the urban area", min=-90, max=90, default=(55.647846), precision=4)

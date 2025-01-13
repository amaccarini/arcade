import bpy


class MyPropertyGroup(bpy.types.PropertyGroup):

    age: bpy.props.IntProperty(name="Age of construction", description="Archetype era", min=1500, max=2050, default=(1970))
    usage: bpy.props.EnumProperty(
        name= "",
        description= "Building usage type",
        items= [('RES_1', "Residential", ""),
                ('COM_1', "Commercial", "")
        ]
    )



    def get_num_stories(self):
        obj = self.id_data  # Access the object this property group belongs to
        if obj and obj.type == 'MESH':  # Ensure it's a valid object
            return round(obj.dimensions.z / 3)  # Calculate number of stories (1 story = 3 meters)
        return 0  # Default value if no object or not a mesh

    def set_num_stories(self, value):
        obj = self.id_data  # Access the object this property group belongs to
        if obj and obj.type == 'MESH':  # Ensure it's a valid object
            obj.dimensions.z = value * 3  # Set height based on number of stories (1 story = 3 meters)

    num_stories: bpy.props.IntProperty(
        name="Number of Stories",
        description="Number of stories in the building (1 story = 3 meters)",
        min=1,  # Minimum of 1 story
        default=1,  # Default value, will be overwritten dynamically
        get=get_num_stories,
        set=set_num_stories,
    )

    #Add property to search for the geojson file



class MyAddonProperties(bpy.types.PropertyGroup):
    def update_tick_box_1(self, context):
        # If tick_box_1 is selected, ensure tick_box_2 is unchecked
        if self.tick_box_1:
            self.tick_box_2 = False
        elif not self.tick_box_2:
            # Ensure at least one box is selected (tick_box_1 becomes default)
            self.tick_box_1 = True

    def update_tick_box_2(self, context):
        # If tick_box_2 is selected, ensure tick_box_1 is unchecked
        if self.tick_box_2:
            self.tick_box_1 = False
        elif not self.tick_box_1:
            # Ensure at least one box is selected (tick_box_1 becomes default)
            self.tick_box_2 = True

    tick_box_1: bpy.props.BoolProperty(
        name="Probabilistic",
        description="Missing parameters (i.e. age, height and usage) are based on a probabilistic normal distribution.",
        default=True,
        update=update_tick_box_1
    )

    tick_box_2: bpy.props.BoolProperty(
        name="AI",
        description="Missing parameters (i.e. age, height and usage) are determined using AI-powered image recognition techniques.",
        default=False,
        update=update_tick_box_2
    )

    avg_age: bpy.props.IntProperty(
        name="average_age",
        description="Average value for the normal distribution used to estimate building age.",
        default=1950,
        min=1500,
        max=2024
    )

    std_age: bpy.props.FloatProperty(
        name="standard_deviation_age",
        description="Standard deviation for the normal distribution of building age. A smaller value indicates low variation around the average value, while a larger value allows for greater variation",
        default=20,
        min=0.1,
        max=100,
        precision=1
    )

    avg_nfloor: bpy.props.IntProperty(
        name="average_num_floor",
        description="Average value for the normal distribution used to estimate the number of stories, and consequenctly the height of buildings.",
        default=2,
        min=1,
        max=100
    )

    std_nfloor: bpy.props.FloatProperty(
        name="standard_deviation_num_floor",
        description="Standard deviation for the normal distribution of nunber of stories. A smaller value indicates low variation around the average value, while a larger value allows for greater variation",
        default=0.5,
        min=0.1,
        max=100,
        precision=1
    )

    lon_min: bpy.props.FloatProperty(name="Min longitude", description="Minimum longitutide of the box containing the urban area", min=-180, max=180, default=(12.587832), precision=4)
    lat_max: bpy.props.FloatProperty(name="Max latitude", description="Maximum latitude of the box containing the urban area", min=-90, max=90, default=(55.649166), precision=4)
    lon_max: bpy.props.FloatProperty(name="Max longitude", description="Maximum longitutide of the box containing the urban area", min=-180, max=180, default=(12.589409), precision=4)
    lat_min: bpy.props.FloatProperty(name="Min latitude", description="Minimum latitude of the box containing the urban area", min=-90, max=90, default=(55.647846), precision=4)

    file_path: bpy.props.StringProperty(
        name="File Path",
        description="Enter the file path or use the folder icon to browse",
        default="",
        subtype="FILE_PATH"
    )

    bui_arch: bpy.props.EnumProperty(
        name= "",
        description= "Building archetype",
        items= [('DK', "Denmark", ""),
                ('US_2A', "USA_2A - Houston", ""),
                ('US_3C', "USA_3C - San Francisco", ""),
                ('US_5A', "USA_5A - Chicago", "")
        ]
    )

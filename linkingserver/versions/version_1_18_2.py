from quarry.types.nbt import TagString

from linkingserver.versions import Version_1_18


class Version_1_18_2(Version_1_18):
    protocol_version = 758

    def get_dimension_settings(self):
        settings = super().get_dimension_settings()

        settings['infiniburn'] = TagString("#minecraft:infiniburn_overworld")

        return settings


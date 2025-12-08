from copy import deepcopy

from quarry.data.data_packs import vanilla_data_packs, pack_formats
from quarry.types.data_pack import DataPack
from quarry.types.namespaced_key import NamespacedKey

from linkingserver.protocol import Protocol
from linkingserver.versions import Version_1_21_9


class Version_1_21_11(Version_1_21_9):
    protocol_version = 1073742109

    def __init__(self, protocol: Protocol, bedrock: bool):
        super(Version_1_21_9, self).__init__(protocol, bedrock)

    def get_written_book_id(self):
        return 1221

    def get_data_pack(self):
        if self.data_pack:
            return self.data_pack

        vanilla_pack = vanilla_data_packs[self.protocol_version]

        # Remove void overrides
        void = deepcopy(vanilla_pack.contents[NamespacedKey.minecraft('worldgen/biome')]
                        .get(NamespacedKey.minecraft('the_void')))

        void['attributes'] = {}
        void['effects'] = {
            'water_color': '#ffffff'
        }

        contents = {
            NamespacedKey.minecraft('dimension_type'): {
                NamespacedKey.minecraft('overworld'): self.get_dimension_settings(),
            },
            NamespacedKey.minecraft('worldgen/biome'): {
                NamespacedKey.minecraft('plains'): void
            }
        }

        self.data_pack = DataPack(NamespacedKey("rtgame", "waitingserver"), "1.0", pack_formats[self.protocol_version], contents)
        return self.data_pack

    def get_dimension_settings(self):
        vanilla_pack = vanilla_data_packs[self.protocol_version]
        settings = deepcopy(vanilla_pack.contents[NamespacedKey.minecraft('dimension_type')]
                        .get(NamespacedKey.minecraft('overworld')))

        settings['attributes'] = {
            'minecraft:visual/sun_angle': 180,
            'minecraft:visual/moon_angle': 180,
            }
        del settings['timelines']

        settings['attributes']['minecraft:audio/background_music'] = {}
        settings['attributes']['minecraft:audio/ambient_sounds'] = {}

        return settings
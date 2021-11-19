import os

from quarry.types.chunk import PackedArray
from quarry.types.nbt import TagCompound, TagRoot, TagString, TagList, TagLongArray, NBTFile, TagInt

from linkingserver.versions import Version_1_17_1
from linkingserver.server import Protocol, path


class Version_1_18pre4(Version_1_17_1):
    def __init__(self, protocol: Protocol, bedrock: False):
        super(Version_1_18pre4, self).__init__(protocol, bedrock)
        self.version_name = '1.18pre4'

        self.biomes = NBTFile(TagRoot({})).load(os.path.join(path, 'biomes', '1.18pre4.nbt'))

    def get_dimension_settings(self):
        settings = super().get_dimension_settings()

        settings['min_y'] = TagInt(-64)
        settings['height'] = TagInt(384)

        return settings

    def send_spawn(self):
        super().send_spawn()
        self.protocol.send_packet("player_abilities", self.protocol.buff_type.pack("bff", 7, 0.05, 0.1))

    def send_join_game(self):
        codec = TagRoot({
            '': TagCompound({
                'minecraft:dimension_type': TagCompound({
                    'type': TagString("minecraft:dimension_type"),
                    'value': TagList([
                        TagCompound(self.dimension)
                    ]),
                }),
                'minecraft:worldgen/biome': self.biomes.root_tag.body
            })
        })

        self.protocol.send_packet("join_game",
                                  self.protocol.buff_type.pack("i?BB", 0, False, 1, 1),
                                  self.protocol.buff_type.pack_varint(2),
                                  self.protocol.buff_type.pack_string("rtgame:waiting"),
                                  self.protocol.buff_type.pack_string("rtgame:reset"),
                                  self.protocol.buff_type.pack_nbt(codec),
                                  self.protocol.buff_type.pack_nbt(self.current_dimension),
                                  self.protocol.buff_type.pack_string("rtgame:waiting"),
                                  self.protocol.buff_type.pack("q", 0),
                                  self.protocol.buff_type.pack_varint(0),
                                  self.protocol.buff_type.pack_varint(32),
                                  self.protocol.buff_type.pack_varint(0),
                                  self.protocol.buff_type.pack("????", False, True, False, False))

    def send_reset_world(self):
        data = [
            self.protocol.buff_type.pack_nbt(
                TagRoot({'': TagCompound({"MOTION_BLOCKING": TagLongArray(PackedArray.empty_height())})})),
            self.protocol.buff_type.pack_varint(1541),
            self.protocol.buff_type.pack("qB", 0, 0)
        ]

        data.append(b'')
        self.protocol.buff_type.pack_varint(0)
        data.append(b'')
        self.protocol.buff_type.pack_varint(0)
        data.append(b'')

        for x in range(-8, 8):
            for y in range(-8, 8):
                self.protocol.send_packet("chunk_data", self.protocol.buff_type.pack("ii", x, y), *data)

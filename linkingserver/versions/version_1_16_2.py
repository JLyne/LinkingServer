import os.path

from quarry.types.nbt import TagList, TagCompound, TagRoot, TagString, TagByte, TagFloat, TagInt, NBTFile

from linkingserver.versions import Version_1_16
from linkingserver.protocol import Protocol
from linkingserver.versions.version import parent_folder


class Version_1_16_2(Version_1_16):
    protocol_version = 751
    chunk_format = '1.16.2'

    biomes = None

    def __init__(self, protocol: Protocol, bedrock: False):
        super(Version_1_16_2, self).__init__(protocol, bedrock)

        self.dimension_settings = None
        self.dimension = None
        self.dimension_codec = None
        self.current_dimension = None

    def init_dimension_codec(self):
        self.dimension_settings = self.get_dimension_settings()

        self.dimension = {
            'name': TagString("minecraft:overworld"),
            'id': TagInt(0),
            'element': TagCompound(self.dimension_settings),
        }

        self.current_dimension = TagRoot({
            '': TagCompound(self.dimension_settings),
        })

        self.dimension_codec = TagRoot({
            '': TagCompound({
                'minecraft:dimension_type': TagCompound({
                    'type': TagString("minecraft:dimension_type"),
                    'value': TagList([
                        TagCompound(self.dimension)
                    ]),
                }),
                'minecraft:worldgen/biome': self.__class__.get_biomes().root_tag.body
            })
        })

    def get_dimension_settings(self):
        return {
            'piglin_safe': TagByte(0),
            'natural': TagByte(1),
            'ambient_light': TagFloat(1.0),
            'infiniburn': TagString("minecraft:infiniburn_overworld"),
            'respawn_anchor_works': TagByte(0),
            'has_skylight': TagByte(1),
            'bed_works': TagByte(0),
            "effects": TagString("minecraft:overworld") if self.is_bedrock else TagString("minecraft:the_nether"),
            'has_raids': TagByte(0),
            'logical_height': TagInt(256),
            'coordinate_scale': TagFloat(1.0),
            'ultrawarm': TagByte(0),
            'has_ceiling': TagByte(0),
            'fixed_time': TagInt(18000),
        }

    def send_join_game(self):
        self.init_dimension_codec()

        self.protocol.send_packet("join_game",
                                  self.protocol.buff_type.pack("i?BB", 0, False, 3, 3),
                                  self.protocol.buff_type.pack_varint(2),
                                  self.protocol.buff_type.pack_string("rtgame:linking"),
                                  self.protocol.buff_type.pack_string("rtgame:reset"),
                                  self.protocol.buff_type.pack_nbt(self.dimension_codec),
                                  self.protocol.buff_type.pack_nbt(self.current_dimension),
                                  self.protocol.buff_type.pack_string("rtgame:linking"),
                                  self.protocol.buff_type.pack("q", 0),
                                  self.protocol.buff_type.pack_varint(0),
                                  self.protocol.buff_type.pack_varint(32),
                                  self.protocol.buff_type.pack("????", False, True, False, False))

    def send_respawn(self):
        self.init_dimension_codec()

        self.protocol.send_packet("respawn",
                                  self.protocol.buff_type.pack_nbt(self.current_dimension),
                                  self.protocol.buff_type.pack_string("rtgame:reset"),
                                  self.protocol.buff_type.pack("qBB", 0, 1, 1),
                                  self.protocol.buff_type.pack("???", False, False, True))

        self.protocol.send_packet("respawn",
                                  self.protocol.buff_type.pack_nbt(self.current_dimension),
                                  self.protocol.buff_type.pack_string("rtgame:linking"),
                                  self.protocol.buff_type.pack("qBB", 0, 1, 1),
                                  self.protocol.buff_type.pack("???", False, False, True))

    def send_world(self):
        data = [
            self.protocol.buff_type.pack_varint(0),
            self.protocol.buff_type.pack_nbt(TagRoot({'': TagCompound({})})),
            self.protocol.buff_type.pack_varint(1024),
        ]

        for i in range(0, 1024):
            data.append(self.protocol.buff_type.pack_varint(127))

        data.append(self.protocol.buff_type.pack_varint(0))
        data.append(self.protocol.buff_type.pack_varint(0))

        if self.is_bedrock:  # Clear geyser chunk cache from previous server
            for x in range(-8, 8):
                for y in range(-8, 8):
                    self.protocol.send_packet("chunk_data", self.protocol.buff_type.pack("ii?", x, y, True), *data)

            self.protocol.ticker.add_loop(100, self.send_time)

    def get_written_book_id(self):
        return 826

    @classmethod
    def get_biomes(cls):
        if cls.biomes is None:
            cls.biomes = NBTFile(TagRoot({})).load(os.path.join(parent_folder, 'biomes', cls.chunk_format + '.nbt'))

        return cls.biomes

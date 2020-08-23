from quarry.types.nbt import TagList, TagCompound, TagRoot, TagString, TagByte, TagFloat, TagInt

import book
from versions import Version_1_16
from linkingserver import Protocol

class Version_1_16_2(Version_1_16):
    dimension_settings = {
        'piglin_safe': TagByte(0),
        'natural': TagByte(1),
        'ambient_light': TagFloat(0.0),
        'infiniburn': TagString("minecraft:infiniburn_overworld"),
        'respawn_anchor_works': TagByte(0),
        'has_skylight': TagByte(0),
        'bed_works': TagByte(0),
        "effects": TagString("minecraft:the_nether"),
        'has_raids': TagByte(0),
        'logical_height': TagInt(256),
        'coordinate_scale': TagFloat(1.0),
        'ultrawarm': TagByte(0),
        'has_ceiling': TagByte(0),
        'fixed_time': TagInt(18000),
    }
    dimension = {
        'name': TagString("minecraft:overworld"),
        'id': TagInt(0),
        'element': TagCompound(dimension_settings),
    }
    current_dimension = TagRoot({
        '': TagCompound(dimension_settings),
    })
    biomes = [
        TagCompound({
            'name': TagString("minecraft:plains"),
            'id': TagInt(1),
            'element': TagCompound({
                'precipitation': TagString("none"),
                'effects': TagCompound({
                    'sky_color': TagInt(0),
                    'water_fog_color': TagInt(0),
                    'fog_color': TagInt(0),
                    'water_color': TagInt(0),
                }),
                'depth': TagFloat(0.1),
                'temperature': TagFloat(0.5),
                'scale': TagFloat(0.2),
                'downfall': TagFloat(0.5),
                'category': TagString("plains")
            }),
        }),
    ]

    def __init__(self, protocol: Protocol):
        super(Version_1_16_2, self).__init__(protocol)
        self.version_name = '1.16.2'

        self.written_book_id = 826

    def send_join_game(self):
        codec = TagRoot({
            '': TagCompound({
                'minecraft:dimension_type': TagCompound({
                    'type': TagString("minecraft:dimension_type"),
                    'value': TagList([
                        TagCompound(self.dimension)
                    ]),
                }),
                'minecraft:worldgen/biome': TagCompound({
                    'type': TagString("minecraft:worldgen/biome"),
                    'value': TagList(self.biomes),
                })
            })
        })

        self.protocol.send_packet("join_game",
                         self.protocol.buff_type.pack("i?BB", 0, False, 3, 3),
                         self.protocol.buff_type.pack_varint(2),
                         self.protocol.buff_type.pack_string("rtgame:linking"),
                         self.protocol.buff_type.pack_string("rtgame:reset"),
                         self.protocol.buff_type.pack_nbt(codec),
                         self.protocol.buff_type.pack_nbt(self.current_dimension),
                         self.protocol.buff_type.pack_string("rtgame:linking"),
                         self.protocol.buff_type.pack("q", 0),
                         self.protocol.buff_type.pack_varint(0),
                         self.protocol.buff_type.pack_varint(32),
                         self.protocol.buff_type.pack("????", False, True, False, False))

    def send_world(self):
        data = [
            self.protocol.buff_type.pack_varint(0),
            self.protocol.buff_type.pack_nbt(TagRoot({'': TagCompound({})})),
            self.protocol.buff_type.pack_varint(1024),
        ]

        for i in range(0, 1024):
            data.append(self.protocol.buff_type.pack_varint(0))

        data.append(self.protocol.buff_type.pack_varint(0))
        data.append(self.protocol.buff_type.pack_varint(0))

        for x in range(-3, 4):
            for y in range(-3, 4):
                self.protocol.send_packet("chunk_data", self.protocol.buff_type.pack("ii?", x, y, True), *data)

    def send_respawn(self):
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
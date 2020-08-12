from quarry.types.nbt import TagList, TagCompound, TagRoot, TagString, TagByte, TagFloat, TagInt, NBTFile

from versions import Version_1_16
from linkingserver import Protocol

class Version_1_16_2(Version_1_16):
    dimension_settings = {
        'name': TagString("minecraft:overworld"),
        'natural': TagByte(1),
        'ambient_light': TagFloat(0.0),
        'has_ceiling': TagByte(0),
        'has_skylight': TagByte(1),
        'ultrawarm': TagByte(0),
        'has_raids': TagByte(0),
        'respawn_anchor_works': TagByte(0),
        'bed_works': TagByte(0),
        'piglin_safe': TagByte(0),
        'infiniburn': TagString("minecraft:infiniburn_overworld"),
        "effects": TagString("minecraft:overworld"),
        'logical_height': TagInt(256),
        'coordinate_scale': TagFloat(1.0),
    }
    dimension = {
        'name': TagString("minecraft:overworld"),
        'id': TagInt(0),
        'element': TagCompound(dimension_settings),
    }
    current_dimension = TagRoot({
        '': TagCompound(dimension_settings),
    })
    biomes = NBTFile(TagRoot({})).load('vanilla-biomes.nbt')

    def __init__(self, protocol: Protocol):
        super(Version_1_16_2, self).__init__(protocol)
        self.version_name = '1.16.2'

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
                         self.protocol.buff_type.pack_string("rtgame:linking"),
                         self.protocol.buff_type.pack_string("rtgame:reset"),
                         self.protocol.buff_type.pack_nbt(codec),
                         self.protocol.buff_type.pack_nbt(self.current_dimension),
                         self.protocol.buff_type.pack_string("rtgame:queue"),
                         self.protocol.buff_type.pack("q", 0),
                         self.protocol.buff_type.pack_varint(0),
                         self.protocol.buff_type.pack_varint(32),
                         self.protocol.buff_type.pack("????", False, True, False, False))

    def spawn_viewpoint_entity(self, viewpoint):
        self.protocol.send_packet(
                'spawn_mob',
                self.protocol.buff_type.pack_varint(self.viewpoint_id),
                self.protocol.buff_type.pack_uuid(self.uuid),
                self.protocol.buff_type.pack_varint(69),
                self.protocol.buff_type.pack("dddbbbhhh",
                                    viewpoint.get('x'),
                                    viewpoint.get('y'),
                                    viewpoint.get('z'),
                                    viewpoint.get('yaw_256'),
                                    viewpoint.get('pitch'),
                                    viewpoint.get('yaw_256'), 0, 0, 0))

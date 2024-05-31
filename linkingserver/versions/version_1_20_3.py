from typing import Protocol

from quarry.data.data_packs import data_packs
from quarry.types.chat import Message
from quarry.types.nbt import TagRoot, TagCompound, TagByte, TagFloat, TagString, TagInt, TagList

from linkingserver.versions import Version


class Version_1_20_3(Version):
    protocol_version = 765

    def __init__(self, protocol: Protocol, bedrock: False):
        super(Version_1_20_3, self).__init__(protocol, bedrock)

        self.dimension_settings = None
        self.dimension = None
        self.dimension_codec = None
        self.current_dimension = None

        self.commands = {
            "name": None,
            "suggestions": None,
            "type": "root",
            "executable": True,
            "redirect": None,
            "children": {
                "link": {
                    "type": "literal",
                    "name": "unlink",
                    "executable": True,
                    "redirect": None,
                    "children": dict(),
                    "suggestions": None
                },
            },
        }

    def send_join_game(self):
        self.protocol.send_packet("join_game",
                                  self.protocol.buff_type.pack("i?", 0, False),
                                  self.protocol.buff_type.pack_varint(2),
                                  self.protocol.buff_type.pack_string("rtgame:linking"),
                                  self.protocol.buff_type.pack_string("rtgame:reset"),
                                  self.protocol.buff_type.pack_varint(0),
                                  self.protocol.buff_type.pack_varint(7),
                                  self.protocol.buff_type.pack_varint(0),
                                  self.protocol.buff_type.pack("???", False, True, False),  # Added is limited crafting
                                  self.protocol.buff_type.pack_string("minecraft:overworld"),  # Moved current dimension
                                  self.protocol.buff_type.pack_string("rtgame:linking"),  # Moved current world
                                  self.protocol.buff_type.pack("qBb??", 0, 1, 1, False, False),
                                  # Moved hashed seed, current/prev gamemode
                                  self.protocol.buff_type.pack("?", False),
                                  self.protocol.buff_type.pack_varint(0))

    def send_spawn(self):
        self.protocol.send_packet("spawn_position", self.protocol.buff_type.pack("iii", 0, 0, 0))

        self.protocol.send_packet("player_position_and_look",
                                  self.protocol.buff_type.pack("dddff?", 0, 2048, 0, 0.0, 0.0, 0b00000),
                                  self.protocol.buff_type.pack_varint(0))  # Remove dismount vehicle

        self.protocol.send_packet("change_game_state", self.protocol.buff_type.pack("Bf", 13, 0.0))  # Hide loading terrain screen

    def send_respawn(self):
        self.protocol.send_packet("respawn",
                                  self.protocol.buff_type.pack_string("minecraft:overworld"),
                                  # Current dimension is now a string
                                  self.protocol.buff_type.pack_string("rtgame:reset"),
                                  self.protocol.buff_type.pack("qBB", 0, 1, 1),
                                  self.protocol.buff_type.pack("????", False, False, True, False))

        self.protocol.send_packet("respawn",
                                  self.protocol.buff_type.pack_string("minecraft:overworld"),
                                  # Current dimension is now a string
                                  self.protocol.buff_type.pack_string("rtgame:linking"),
                                  self.protocol.buff_type.pack("qBB", 0, 1, 1),
                                  self.protocol.buff_type.pack("????", False, False, True, False))

    def send_reset_world(self):
        data = [
            self.protocol.buff_type.pack_nbt(TagRoot({'': TagCompound({})})),  # Heightmap
            self.protocol.buff_type.pack_varint(0),  # Data size
            self.protocol.buff_type.pack_varint(0),  # Block entity count
            self.protocol.buff_type.pack_varint(0),  # Sky light mask
            self.protocol.buff_type.pack_varint(0),  # Block light mask
            self.protocol.buff_type.pack_varint(0),  # Empty sky light mask
            self.protocol.buff_type.pack_varint(0),  # Empty block light mask
            self.protocol.buff_type.pack_varint(0),  # Sky light array count
            self.protocol.buff_type.pack_varint(0),  # Block light array count
        ]

        for x in range(-8, 8):
            for y in range(-8, 8):
                self.protocol.send_packet("chunk_data", self.protocol.buff_type.pack("ii", x, y), *data)

    def send_keep_alive(self):
        self.protocol.send_packet("keep_alive", self.protocol.buff_type.pack("Q", 0))

    def send_time(self):
        self.protocol.send_packet("time_update", self.protocol.buff_type.pack("ll", 0, -18000))

    def send_title(self):
        self.protocol.send_packet("set_title_text",
                                  self.protocol.buff_type.pack_chat(Message("Read the Book")))
        self.protocol.send_packet("set_title_time",
                                  self.protocol.buff_type.pack("iii", 10, 72000, 72000))

    def send_commands(self):
        self.protocol.send_packet('declare_commands', self.protocol.buff_type.pack_commands(self.commands))

    def send_tablist(self):
        self.protocol.send_packet("player_list_header_footer",
                                  self.protocol.buff_type.pack_chat(Message("\n\ue300\n")),
                                  self.protocol.buff_type.pack_chat(Message("")))

        self.protocol.send_packet("player_list_item",
                                  self.protocol.buff_type.pack('B', 63),
                                  self.protocol.buff_type.pack_varint(1),
                                  self.protocol.buff_type.pack_uuid(self.protocol.uuid),
                                  self.protocol.buff_type.pack_string(self.protocol.display_name),
                                  self.protocol.buff_type.pack_varint(0),
                                  self.protocol.buff_type.pack("?", False),  # False for no chat session info
                                  self.protocol.buff_type.pack_varint(1),
                                  self.protocol.buff_type.pack("?", True),  # Show in tab list
                                  self.protocol.buff_type.pack_varint(1),
                                  self.protocol.buff_type.pack("?", False))

    def send_inventory(self):
        data = [
            self.protocol.buff_type.pack('B', 0),
            self.protocol.buff_type.pack_varint(0),
            self.protocol.buff_type.pack_varint(46),
        ]

        for i in range(0, 46):
            data.append(self.protocol.buff_type.pack('?', False))

        data.append(self.protocol.buff_type.pack('?', False))
        self.protocol.send_packet('window_items', *data)

    def get_written_book_id(self):
        return 1086

    def send_book(self, nbt):
        self.protocol.send_packet("set_slot", self.protocol.buff_type.pack("b", 0),
                                  self.protocol.buff_type.pack_varint(0),
                                  self.protocol.buff_type.pack("h?", 36, True),
                                  self.protocol.buff_type.pack_varint(self.written_book_id),
                                  self.protocol.buff_type.pack("b", 1),
                                  self.protocol.buff_type.pack_nbt(nbt))

        self.send_open_book()

    def send_open_book(self):
        self.protocol.send_packet("held_item_change", self.protocol.buff_type.pack("b", 0))
        self.protocol.send_packet("open_book", self.protocol.buff_type.pack_varint(0))

    def get_dimension_codec(self):
        self.init_dimension_codec()

        return self.dimension_codec

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

        self.dimension_codec = data_packs[self.protocol_version]

        self.dimension_codec.body.value['minecraft:dimension_type'] = TagCompound({
            'type': TagString("minecraft:dimension_type"),
            'value': TagList([
                TagCompound(self.dimension)
            ]),
        })

        # Make sky and fog black
        for biome in self.dimension_codec.body.value['minecraft:worldgen/biome'].value['value'].value:
            if biome.value['name'].value == "minecraft:plains":
                effects = biome.value['element'].value['effects']

                effects.value['sky_color'].value = effects.value['fog_color'].value = \
                    effects.value['water_color'].value = effects.value['water_fog_color'].value = 0

    def get_dimension_settings(self):
        return {
            'piglin_safe': TagByte(0),
            'natural': TagByte(1),
            'ambient_light': TagFloat(1.0),
            'infiniburn': TagString("#minecraft:infiniburn_overworld"),
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
            'min_y': TagInt(-64),
            'height': TagInt(384),
            'monster_spawn_block_light_limit': TagInt(0),
            'monster_spawn_light_level': TagInt(0),
        }

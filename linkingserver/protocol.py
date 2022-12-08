import hmac
import json
import random
import time

from copy import deepcopy

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives.hashes import SHA256
from quarry.net import crypto, auth
from quarry.net.crypto import verify_mojang_v1_signature, verify_mojang_v2_signature
from quarry.net.protocol import ProtocolError
from quarry.net.server import ServerProtocol
from quarry.types.uuid import UUID

from linkingserver.log import console_handler, file_handler, logger
from linkingserver.prometheus import set_players_online

versions = {}


class Protocol(ServerProtocol):
    linking_secret = None
    bungee_forwarding = False
    velocity_forwarding = False
    velocity_forwarding_secret = None

    def __init__(self, factory, remote_addr):
        super(Protocol, self).__init__(factory, remote_addr)

        self.velocity_message_id = None
        self.is_bedrock = False
        self.version = None

        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    def packet_handshake(self, buff):
        buff2 = deepcopy(buff)
        super().packet_handshake(buff)

        buff2.unpack_varint()
        p_connect_host = buff2.unpack_string()

        if self.bungee_forwarding is True:
            # Bungeecord ip forwarding, ip/uuid is included in host string separated by \00s
            split_host = str.split(p_connect_host, "\00")

            if len(split_host) < 3:
                logger.warning("Invalid bungeecord forwarding data received from {}".format(self.remote_addr))
                self.close("Invalid bungeecord forwarding data")
                return

            # TODO: Should probably verify the encrypted data in some way.
            # Not important until something on this server uses uuids
            if split_host[1] == 'Geyser-Floodgate':
                self.is_bedrock = True

                host = split_host[4]
                online_uuid = split_host[5]
            elif split_host[1].startswith('^Floodgate^'):
                self.is_bedrock = True

                host = split_host[2]
                online_uuid = split_host[3]
            else:
                host = split_host[1]
                online_uuid = split_host[2]

            self.connect_host = host
            self.uuid = UUID.from_hex(online_uuid)

            logger.info("Bungeecord: {}".format(self.uuid))

        version = None

        # Select version handler
        for protocol_version, v in versions.items():
            if self.protocol_version >= protocol_version:
                version = v

        if version is not None:
            self.version = version(self, self.is_bedrock)
        else:
            self.close("Unsupported Minecraft Version")

    def packet_login_start(self, buff):
        if self.login_expecting != 0:
            logger.warning("Unexpected login_start received from {}".format(self.remote_addr))
            self.close("Out-of-order login")
            return

        if self.velocity_forwarding is True:
            self.login_expecting = 2
            self.velocity_message_id = random.randint(0, 2147483647)
            self.send_packet("login_plugin_request",
                             self.buff_type.pack_varint(self.velocity_message_id),
                             self.buff_type.pack_string("velocity:player_info"),
                             b'')
            buff.read()
            return

                # FIXME: Remove below when quarry updates
        self.display_name = buff.unpack_string()

        if self.factory.online_mode:
            self.login_expecting = 1

            # 1.19 - 1.19.2 may send a Mojang signed public key which needs to be verified
            if 759 <= self.protocol_version < 761:
                try:
                    self.public_key_data = buff.unpack_optional(buff.unpack_player_public_key)
                except ValueError:
                    raise ProtocolError("Unable to parse profile public key")

                # Validate public key if present
                if self.public_key_data is not None:
                    if self.public_key_data.expiry < time.time():
                        raise ProtocolError("Expired profile public key")

                    if self.protocol_version >= 760:
                        uuid = buff.unpack_optional(buff.unpack_uuid)  # 1.19.1+ may also send player UUID
                        valid = verify_mojang_v2_signature(self.public_key_data, uuid)
                    else:
                        valid = verify_mojang_v1_signature(self.public_key_data)

                    if not valid:
                        raise ProtocolError("Invalid profile public key signature")

                # If secure profiles are required, throw if no public key provided
                elif self.factory.enforce_secure_profile:
                    raise ProtocolError("Missing profile public key")

            # send encryption request

            # 1.7.x
            if self.protocol_version <= 5:
                pack_array = lambda a: self.buff_type.pack('h', len(a)) + a

            # 1.8.x
            else:
                pack_array = lambda a: self.buff_type.pack_varint(
                    len(a), max_bits=16) + a

            self.send_packet(
                "login_encryption_request",
                self.buff_type.pack_string(self.server_id),
                pack_array(self.factory.public_key),
                pack_array(self.verify_token))

        else:
            self.login_expecting = None
            self.display_name_confirmed = True
            self.uuid = UUID.from_offline_player(self.display_name)

            self.player_joined()

        buff.discard()

        # FIXME: Uncomment when quarry updates
        #super().packet_login_start(buff)

    # FIXME: Remove method when quarry updates
    def packet_login_encryption_response(self, buff):
        if self.login_expecting != 1:
            raise ProtocolError("Out-of-order login")

        # 1.7.x
        if self.protocol_version <= 5:
            unpack_array = lambda b: b.read(b.unpack('h'))
        # 1.8.x
        else:
            unpack_array = lambda b: b.read(b.unpack_varint(max_bits=16))

        p_shared_secret = unpack_array(buff)
        salt = None

        # 1.19 - 1.19.2 can now sign the verify token + a salt with the players public key, rather than encrypting the token
        if 759 <= self.protocol_version < 761:
            if buff.unpack("?") is False:
                salt = buff.unpack("Q").to_bytes(8, 'big')

        p_verify_token = unpack_array(buff)

        shared_secret = crypto.decrypt_secret(
            self.factory.keypair,
            p_shared_secret)

        if salt is not None:
            try:
                self.public_key_data.key.verify(p_verify_token, self.verify_token + salt, PKCS1v15(), SHA256())
            except InvalidSignature:
                raise ProtocolError("Verify token incorrect")
        else:
            verify_token = crypto.decrypt_secret(
                self.factory.keypair,
                p_verify_token)

            if verify_token != self.verify_token:
                raise ProtocolError("Verify token incorrect")

        self.login_expecting = None

        # enable encryption
        self.cipher.enable(shared_secret)
        self.logger.debug("Encryption enabled")

        # make digest
        digest = crypto.make_digest(
            self.server_id.encode('ascii'),
            shared_secret,
            self.factory.public_key)

        # do auth
        remote_host = None
        if self.factory.prevent_proxy_connections:
            remote_host = self.remote_addr.host
        deferred = auth.has_joined(
            self.factory.auth_timeout,
            digest,
            self.display_name,
            remote_host)
        deferred.addCallbacks(self.auth_ok, self.auth_failed)

        # FIXME: Remove below when quarry updates
        self.display_name = buff.unpack_string()

        if self.factory.online_mode:
            self.login_expecting = 1

            # 1.19 - 1.19.2 may send a Mojang signed public key which needs to be verified
            if 759 <= self.protocol_version < 761:
                try:
                    self.public_key_data = buff.unpack_optional(buff.unpack_player_public_key)
                except ValueError:
                    raise ProtocolError("Unable to parse profile public key")

                # Validate public key if present
                if self.public_key_data is not None:
                    if self.public_key_data.expiry < time.time():
                        raise ProtocolError("Expired profile public key")

                    if self.protocol_version >= 760:
                        uuid = buff.unpack_optional(buff.unpack_uuid)  # 1.19.1+ may also send player UUID
                        valid = verify_mojang_v2_signature(self.public_key_data, uuid)
                    else:
                        valid = verify_mojang_v1_signature(self.public_key_data)

                    if not valid:
                        raise ProtocolError("Invalid profile public key signature")

                # If secure profiles are required, throw if no public key provided
                elif self.factory.enforce_secure_profile:
                    raise ProtocolError("Missing profile public key")

            # send encryption request

            # 1.7.x
            if self.protocol_version <= 5:
                pack_array = lambda a: self.buff_type.pack('h', len(a)) + a

            # 1.8.x
            else:
                pack_array = lambda a: self.buff_type.pack_varint(
                    len(a), max_bits=16) + a

            self.send_packet(
                "login_encryption_request",
                self.buff_type.pack_string(self.server_id),
                pack_array(self.factory.public_key),
                pack_array(self.verify_token))

        else:
            self.login_expecting = None
            self.display_name_confirmed = True
            self.uuid = UUID.from_offline_player(self.display_name)

            self.player_joined()

        buff.discard()

        # FIXME: Uncomment when quarry updates
        #super().packet_login_start(buff)

    # FIXME: Remove method when quarry updates
    def packet_login_encryption_response(self, buff):
        if self.login_expecting != 1:
            raise ProtocolError("Out-of-order login")

        # 1.7.x
        if self.protocol_version <= 5:
            unpack_array = lambda b: b.read(b.unpack('h'))
        # 1.8.x
        else:
            unpack_array = lambda b: b.read(b.unpack_varint(max_bits=16))

        p_shared_secret = unpack_array(buff)
        salt = None

        # 1.19 - 1.19.2 can now sign the verify token + a salt with the players public key, rather than encrypting the token
        if 759 <= self.protocol_version < 761:
            if buff.unpack("?") is False:
                salt = buff.unpack("Q").to_bytes(8, 'big')

        p_verify_token = unpack_array(buff)

        shared_secret = crypto.decrypt_secret(
            self.factory.keypair,
            p_shared_secret)

        if salt is not None:
            try:
                self.public_key_data.key.verify(p_verify_token, self.verify_token + salt, PKCS1v15(), SHA256())
            except InvalidSignature:
                raise ProtocolError("Verify token incorrect")
        else:
            verify_token = crypto.decrypt_secret(
                self.factory.keypair,
                p_verify_token)

            if verify_token != self.verify_token:
                raise ProtocolError("Verify token incorrect")

        self.login_expecting = None

        # enable encryption
        self.cipher.enable(shared_secret)
        self.logger.debug("Encryption enabled")

        # make digest
        digest = crypto.make_digest(
            self.server_id.encode('ascii'),
            shared_secret,
            self.factory.public_key)

        # do auth
        remote_host = None
        if self.factory.prevent_proxy_connections:
            remote_host = self.remote_addr.host
        deferred = auth.has_joined(
            self.factory.auth_timeout,
            digest,
            self.display_name,
            remote_host)
        deferred.addCallbacks(self.auth_ok, self.auth_failed)

    def packet_login_plugin_response(self, buff):
        if self.login_expecting != 2 or self.protocol_mode != "login":
            logger.warning("Unexpected login_plugin_response received from {}".format(self.remote_addr))
            self.close("Out-of-order login")
            return

        message_id = buff.unpack_varint()
        successful = buff.unpack('b')

        if message_id != self.velocity_message_id:
            logger.warning("Unexpected login_plugin_response received from {}".format(self.remote_addr))
            self.close("Unexpected login_plugin_response")
            return

        if not successful or len(buff) == 0:
            logger.warning("Empty velocity forwarding response received from {}".format(self.remote_addr))
            self.close("Empty velocity forwarding response")
            return

        # Verify HMAC
        signature = buff.read(32)
        verify = hmac.new(key=str.encode(self.velocity_forwarding_secret), msg=deepcopy(buff).read(),
                          digestmod="sha256").digest()

        if verify != signature:
            logger.warning("Invalid velocity forwarding response received from {}".format(self.remote_addr))
            self.close("Invalid velocity forwarding response received")
            buff.discard()
            return

        version = buff.unpack_varint()

        if version != 1:
            logger.warning("Unsupported velocity forwarding version received from {}".format(self.remote_addr))
            self.close("Unsupported velocity forwarding version")
            buff.discard()
            return

        buff.unpack_string()  # Ip

        self.uuid = buff.unpack_uuid()
        self.display_name = buff.unpack_string()

        buff.discard()  # Don't care about the rest

        self.login_expecting = None
        self.display_name_confirmed = True
        logger.info("Velocity: {} {}".format(self.display_name, self.uuid))
        self.player_joined()

    def player_joined(self):
        if self.uuid is None:
            self.uuid = UUID.from_offline_player(self.display_name)

        super().player_joined()

        set_players_online(len(self.factory.players))

        self.version.player_joined()

    def player_left(self):
        super().player_left()

        set_players_online(len(self.factory.players))

    def packet_animation(self, buff):
        self.version.send_open_book()
        buff.discard()

    def packet_use_item(self, buff):
        self.version.send_open_book()
        buff.discard()

    def packet_held_item_change(self, buff):
        buff.discard()

        if self.version.is_bedrock:
            self.version.give_book()

    def packet_plugin_message(self, buff):
        channel = buff.unpack_string()
        data = buff.read()

        if channel != "proxydiscord:status":
            return

        payload = json.loads(data.decode(encoding="utf-8"))
        payload_hmac = payload.get("hmac")

        msg = "{0:d}{1:d}{2:s}".format(payload.get("status"), payload.get("bedrock"), payload.get("token"))
        calculated_hmac = hmac.new(key=str.encode(self.linking_secret, encoding="utf-8"),
                                   msg=str.encode(msg, encoding="utf-8"), digestmod="sha512")

        if calculated_hmac.hexdigest() != payload_hmac:
            self.logger.warn("Failed to validate plugin message for {}. Is the linking secret configured correctly?"
                             .format(self.display_name))
            return

        self.version.status_received(payload)


# Build dictionary of protocol version -> version class
# Local import to prevent circlular import issues
def build_versions():
    import linkingserver.versions

    for version in vars(linkingserver.versions).values():
        if hasattr(version, 'protocol_version') and version.protocol_version is not None:
            versions[version.protocol_version] = version

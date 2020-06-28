import glob
import json
import os
import re

from quarry.types.buffer import Buffer


class Chunk:

    def __init__(self, name: str, environment: dict, folder: str, version: str, viewpoints: list):
        self.name = name

        self.time = environment.get('time', 0)
        self.dimension = environment.get('dimension', 'Overworld')
        self.weather = environment.get('weather', 'clear')
        self.cycle = environment.get('cycle', False)

        self.packets = list()
        self.viewpoints = list()

        path = os.path.join(os.getcwd(), 'packets', folder, version, '*.bin')

        for filename in sorted(glob.glob(path)):
            file = open(filename, 'rb')
            packet_type = re.match(r'(\d+)_dn_(\w+)\.bin', os.path.basename(filename))

            self.packets.append({
                "id": packet_type.group(1),
                "type": packet_type.group(2),
                "packet": Buffer(file.read()).read()
            })
            file.close()

        for viewpoint in viewpoints:
            parts = [0, 0, 0, 0, 0]

            for i, part in enumerate(viewpoint.split(',')):
                parts[i] = part

            self.viewpoints.append({
                "x": float(parts[0]),
                "y": float(parts[1]),
                "z": float(parts[2]),
                "yaw": float(parts[3]),
                "yaw_256": int((float(parts[3]) / 360) * 256),
                "pitch": int(float(parts[4])),
            })

        if len(self.viewpoints) is 0:
            self.viewpoints.append({
                "x": 0.0,
                "y": 0.0,
                "z": 0.0,
                "yaw": 0,
                "yaw_256": 0,
                "pitch": 0
            })

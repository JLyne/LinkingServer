import logging
import os

from chunk import Chunk

import yaml

logger = logging.getLogger('config')

def load_chunk_config():
    chunks = list()

    with open(r'config.yml') as file:
        entries = yaml.load(file)

        for entry in entries:
            name = entry.get('name', 'Untitled')
            contributors = entry.get('contributors', list())
            environment = entry.get('environment', dict())
            folder = entry.get('folder')
            viewpoints = entry.get('viewpoints', list())

            if folder is None:
                logger.error('Entry %s has no folder defined. Skipped.', name)
                continue

            folder_path = os.path.join(os.getcwd(), 'packets', folder)

            if os.path.exists(folder_path) is False:
                logger.error('Folder for entry %s does not exist. Skipped.', name)
                continue

            chunk = Chunk(name, contributors, environment, folder, viewpoints)
            logger.info('Loaded {}', chunk.credit_string)

            chunks.append(chunk)

        return chunks
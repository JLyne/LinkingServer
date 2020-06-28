import logging
import os
import glob

from chunk import Chunk

import yaml

logger = logging.getLogger('config')

chunks = {
    '1.15': [],
    '1.16': [],
}

def load_chunk_config():
    with open(r'config.yml') as file:
        entries = yaml.load(file)

        for entry in entries:
            name = entry.get('name', 'Untitled')
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

            for subfolder in glob.glob(os.path.join(folder_path, '*/')):
                version = os.path.basename(os.path.normpath(subfolder))

                if chunks.get(version) is not None:
                    chunk = Chunk(name, environment, folder, version, viewpoints)
                    logger.info('Loaded {} for version {}', chunk.name, version)

                    chunks[version].append(chunk)

        for version in chunks:
            if len(chunks[version]) == 0:
                logger.error('No entries defined for {}'.format(str(version)))
                exit(1)

        return chunks
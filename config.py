import os

# API URL
SAT_API = os.getenv('SAT_API', 'https://api.developmentseed.org/satellites')

# Директория, в которой будут помещаться скачанные снимки
DATADIR = os.getenv('SATUTILS_DATADIR', os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') )

SUBDIRS = 'satellite_name/scene_id'

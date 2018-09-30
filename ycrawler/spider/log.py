import logging

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname).1s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger('run')

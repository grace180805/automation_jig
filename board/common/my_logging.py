from board.common import logging

# Create logger
logger = logging.getLogger('esp32')

# Create console handler and set level to debug
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)

# Create file handler and set level to error
file_handler = logging.FileHandler("debug.log", mode="w")
file_handler.setLevel(logging.DEBUG)

# Create a formatter
formatter = logging.Formatter("%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s")

# Add formatter to the handlers
stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)


logger.addHandler(file_handler)
logger.addHandler(stream_handler)



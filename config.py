# how long of the recordings will be saved, which means the recordings produced earlier will be removed
PRESERVE_DAY = 7

# The recordings is being cut into pieces for two reasons:
# 1. Adjust the resolution of the recording for the Gnome session in time and as appropriately. When the recording is running, if user enlarge the resolution of the screen, the recording will keep the original resolution, which means only part of screen is recorded. At this moment, we cannot detect the resolution change real time, so we need to adjust the resolution of the recording regularly;
# 2. The too old recordings could be removed little by little;
RECORDING_SESSION_DURATION_HOUR = 1

# The interval between two executions in the main loop of the recording manager
INTERVAL_OF_MANAGER_MAIN_LOOP_SEC = 2

# The interval between two file checkings, with which too old recordings will be removed
INTERVAL_OF_FILE_CHECK_SEC = 3600

# Domain the LVDA is added to, with which the active GNOME session could be searched
DOMAIN = "hccltbrnet"

# Where to place the recordings
RECORDING_DIR = "/media/storage-ssd/SessionRecording/"
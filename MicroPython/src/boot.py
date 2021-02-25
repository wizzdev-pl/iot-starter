from uos import statvfs
from logging import basicConfig, getLogger, DEBUG, debug
from gc import enable, collect, threshold, mem_free, mem_alloc

from common import utils

# Logger config
basicConfig(level=DEBUG)
main_logger = getLogger(None)
main_logger.setLevel(DEBUG)

# Info about start
debug("=== BOOT START ===")
utils.print_reset_wake_state()

# Garbage Collector
enable()
threshold(mem_free() // 4 + mem_alloc())

# Diagnostic info - not needed in production
collect()
debug("Free memory: " + str(mem_free()))
fs_stat = statvfs('//')
debug("Free flash: {} MB".format((fs_stat[0]*fs_stat[3])/1048576))
del fs_stat

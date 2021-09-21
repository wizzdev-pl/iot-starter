from uos import statvfs
from gc import collect, enable, mem_alloc, mem_free, threshold
from logging import DEBUG, basicConfig, debug, getLogger
import micropython
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
debug("Optimalisation level: []".format(micropython.opt_level()))
micropython.opt_level(3)
debug("Optimalisation level: [{}]".format(micropython.opt_level()))
micropython.alloc_emergency_exception_buf(1000)
del fs_stat

import pyMesa as pym
import sys

utils_lib, utils_def = pym.loadMod("utils")

utils_lib.utils_omp_get_max_threads()
utils_lib.utils_omp_get_thread_num()

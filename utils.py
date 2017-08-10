import pyMesaUtils as pym
import sys

#Decreases recursion depth to make debugging easier
sys.setrecursionlimit(100)
utils_lib, utils_def = pym.loadMod("utils")

utils_lib.utils_omp_get_max_threads()
utils_lib.utils_omp_get_thread_num()

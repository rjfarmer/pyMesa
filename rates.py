import pyMesaUtils as pym

rates_lib,rates_def = pym.loadMod("rates")

rates_lib.rates_init('reactions.list','jina_reaclib_results_20130213default2',
                    'rate_tables',False,'','','',ierr)

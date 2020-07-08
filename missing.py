"""
This defnotdatatools.missing module is tools for handling missing data.

For how to import, see defnotdatatools/README.md.
"""



# < Setup > ============================================================================

import numpy as np



# < tfrm fns > ============================================================================

def tfrm_fill_median(series, fill_val_if_no_median_possible=0):
    """
    Fill any NaN's with series median, if series is float-like (eg not int, object, date).
    Unless the ENTIRE series is NaN, then fill with 0s.
    Optimized for fast runtime.
    """
    if not np.issubdtype(series.dtype, np.inexact):  # check whether series is float-like
        return series
    if not series.isnull().values.any():  # check if there are any NaN's are there
        return series
    if series.count() == 0:  # if ENTIRE series is all NaN...
        return series.fillna(fill_val_if_no_median_possible)
    return series.fillna(series.median())

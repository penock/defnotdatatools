"""
defnotdatatools.iact module is for interactive (iact) use in Jupyter Notebooks. Often this is code you'll run just to view something for the moment.

For how to import, see defnotdatatools/README.md.
"""



# < Setup > ============================================================================

import re
import inspect
import numpy as np
import pandas as pd
from collections import OrderedDict

try:
    __IPYTHON__
    IPYTHON_RUNNING = True
    from IPython.core.display import HTML
except NameError:
    IPYTHON_RUNNING = False



# < dir_ fns to look inside modules, classes > ==================================

DIR_ATTR_NAME_WIDTH = 16  # Attr means 'attribute', something that shows up in a dir()
DIR_DEFAULT_PATTERN = '^[^_].*'

def dir_regex(obj, pattern=DIR_DEFAULT_PATTERN):
    """
    dir_regex(obj) lists module or class's properties like normal dir(obj),
    but just ones matching your pattern.

    By default, lists items that don't start with underscore.

    If you want to do dir() to look at your current environment, not a specific object,
    well we might not be able to make a fn within a package do this. Instead, run this in your
    code to set up your own idir():
        idir = lambda: [s for s in globals() if not s.startswith('_')]
    """
    dir_list = dir(obj)
    return [s for s in dir_list if re.search(pattern, s)]

def dir_str(obj=None, pattern=DIR_DEFAULT_PATTERN, max_line_len=90):
    """Shows str() representations of items inside the module or class (max len 100)"""
    dir_list = dir_regex(obj=obj, pattern=pattern)
    ret = []
    for attr_name in dir_list:
        attr = _getattr_or_attribute(obj=obj, attr_name=attr_name)
        ret.append(attr_name.ljust(DIR_ATTR_NAME_WIDTH) + ": " + str(attr)[:max_line_len])
    return ret

def dir_doc(obj=None, pattern=DIR_DEFAULT_PATTERN, max_line_len=90):
    """Shows docstrings (.__doc__) of items inside the module or class (max len 100)"""
    dir_list = dir_regex(obj=obj, pattern=pattern)
    ret = []
    for attr_name in dir_list:
        attr = _getattr_or_attribute(obj=obj, attr_name=attr_name)
        docstring = inspect.getdoc(attr)
        if docstring is None:
            docstring = '(no docstring)'
        try:
            ret.append(attr_name.ljust(DIR_ATTR_NAME_WIDTH) + ": " + docstring[:max_line_len])
        except TypeError:
            print('during TypeError, docstring was:' + str(attr))
    return ret

def _getattr_or_attribute(obj, attr_name):
    """Gets attr or attribute, see comments below or FMI http://stackoverflow.com/a/1944714 (it's really confusing though)"""
    try:
        # if attr_name is a property (not method or fn), attr is what the class gives back
        # when it's normally requested
        return getattr(obj, attr_name)
    except AttributeError:
        # if attr_name is a property (not method or fn), the getattribute is what's really there
        # in the class, not what's given back when it's normally requested
        # this exception clause here applies only at times when what's normally given causes an error
        # (example: if you type pd.DataFrame.index, you get this AttributeError)
        return obj.__getattribute__(obj, attr_name)



# < To get info about DataFrames and columns > ===========================================

def df_summary(df):
    """Return df of info about passed DataFrame."""
    assert isinstance(df, pd.DataFrame)
    info_pairs = OrderedDict()
    info_pairs['nrows'] = str(len(df))
    if len(df) > 99999:
        info_pairs['nrows'] += ' (' + _readable_num(len(df)) + ')'
    info_pairs['ncols'] = len(df.columns)
    info_pairs['index'] = df.index.name
    info_pairs['memory_usage'] = _readable_memory(df.memory_usage(index=True).sum())
    counts = df.dtypes.value_counts()
    info_pairs['dtypes'] = ', '.join([str(dtype) + '(' + str(count) + ')' for dtype, count in counts.iteritems()])
    return pd.DataFrame([info_pairs], columns=info_pairs.keys())

def cols_info_float(df):
    """
    Return df of info about float-like columns of passed DataFrame.

    pandas's most similar command is df.select_dtypes(exclude=['float']).describe().T

    """
    assert isinstance(df, pd.DataFrame)
    odicts_lst = []
    df_floats = df.select_dtypes(['float'])
    for cn, ser in df_floats.iteritems():
        odict = ser_info_any(ser)
        odict.update(ser_info_float(ser))
        odicts_lst.append(odict)
    if len(odicts_lst) == 0:
        return None
    ret_df = pd.DataFrame(odicts_lst, columns=odicts_lst[0].keys())
    assert len(df_floats.dtypes) == len(ret_df)
    ret_df = ret_df.set_index('name')
    ret_df['dtype'] = df_floats.dtypes.apply(str)
    ret_df = ret_df.applymap(lambda x: x.decode() if isinstance(x, bytes) else x)
    return ret_df

def cols_info_other(df):
    """
    Return df of info about other (non-float like) columns of passed DataFrame.

    pandas's most similar command is df.select_dtypes(exclude=['float']).describe().T
    """
    assert isinstance(df, pd.DataFrame)
    odicts_lst = []
    df_others = df.select_dtypes(exclude=['float'])
    for cn, ser in df_others.iteritems():
        odict = ser_info_any(ser)
        odict.update(ser_info_other(ser))
        odicts_lst.append(odict)
    if len(odicts_lst) == 0:
        return None
    ret_df = pd.DataFrame(odicts_lst, columns=odicts_lst[0].keys())
    ret_df = ret_df.set_index('name')
    ret_df['dtype'] = df_others.dtypes.apply(str)
    ret_df = ret_df.applymap(lambda x: x.decode() if isinstance(x, bytes) else x)
    return ret_df

def ser_info_any(ser):
    """Return OrderedDict of info about any Series."""
    assert isinstance(ser, pd.Series)
    info_pairs = OrderedDict()
    info_pairs['name'] = ser.name
    ser_count = ser.count()
    info_pairs['filled_pct'] = ser_count / len(ser)
    info_pairs['miss_ct'] = len(ser) - ser_count

    ser = ser[ser.notna()]  # because NaNs in object Serieses cause TypeError
    info_pairs['min'] = ser.min()
    info_pairs['max'] = ser.max()
    return info_pairs

def ser_info_float(ser):
    """Return OrderedDict of info about a float Series (ignoring NaNs)."""
    assert isinstance(ser, pd.Series)
    ser = ser.dropna()  # Ignore all NaNs
    info_pairs = OrderedDict()
    if len(ser) == 0:  # Return all NaNs to avoid RuntimeWarning for empty series
        info_pairs.update({'min_medADs': np.nan, 'max_medADs': np.nan,
                           'medAD': np.nan, 'MAD': np.nan, 'median': np.nan,
                           'mean': np.nan, 'std': np.nan,
                           '05_pctile': np.nan, '25_pctile': np.nan,
                           '50_pctile': np.nan, '75_pctile': np.nan, '95_pctile': np.nan})
        return info_pairs
    ser_median = ser.median()
    med_AD = np.median(np.abs(ser - ser_median))  # Median Absolute Deviation
    if med_AD != 0:
        info_pairs['min_medADs'] = (ser_median - ser.min()) / med_AD
        info_pairs['max_medADs'] = (ser.max() - ser_median) / med_AD
    info_pairs['medAD'] = med_AD
    info_pairs['MAD'] = ser.mad()
    info_pairs['median'] = ser_median
    info_pairs['mean'] = ser.mean()
    info_pairs['std'] = ser.std()
    info_pairs['05_pctile'] = ser.quantile(.05)
    info_pairs['25_pctile'] = ser.quantile(.25)
    info_pairs['50_pctile'] = ser.quantile(.50)
    info_pairs['75_pctile'] = ser.quantile(.75)
    info_pairs['95_pctile'] = ser.quantile(.95)
    info_pairs['zeros_pct'] = len(ser[ser == 0]) / len(ser)
    return info_pairs

def ser_info_other(ser):
    """Return OrderedDict of info about any non-float Series (ignoring NaNs)."""
    assert isinstance(ser, pd.Series)
    ser = ser.dropna()  # Ignore all NaNs
    info_pairs = OrderedDict()
    ser_count = ser.count()
    info_pairs['nunique'] = ser.nunique()
    n_mostfreq = 3
    value_counts = ser.value_counts()[:n_mostfreq]
    for i in range(n_mostfreq):
        if i+1 > len(value_counts):  # if there are fewer than 3 values in series, use nan
            info_pairs['mostfreq' + str(i+1)] = np.nan
            info_pairs['mf' + str(i+1) + '_pct'] = np.nan
        else:
            info_pairs['mostfreq' + str(i+1)] = value_counts.index[i]
            info_pairs['mf' + str(i+1) + '_pct'] = value_counts.iloc[i] / ser_count
    return info_pairs

def df_full_info(df, name=''):
    """
    Displays info about passed df, including df_summary(), cols_info_ fns, and more.

    Returns: a DFFullInfo object which makes all that info available, as well as the HTML
    displayed, in case you'd want to use this info in reports or combine with other tables' info.
    """
    assert isinstance(df, pd.DataFrame)
    return DFFullInfo(df=df, name=name)

def styler_cell(val, precision=3):
    """
    Format a value (really for an int or float, will return same otherwise) nicely,
    as used by df_full_info(), cols_info_float(), and cols_info_other().

    Returns:
        str
    """
    if isinstance(val, (int, float)):
        if abs(val) >= 10000:
            return _readable_num(val)
        else:
            ret = float("{0:.{1}e}".format(val, precision))
            if ret == 0 or ret == 1 or ret == -1:
                ret = int(ret)
            elif -1 < ret < 1:
                ret = "{:.4f}".format(ret)
    elif isinstance(val, str):
        ret = val
    else:
        ret = val
    return ret

def styler_df(df):
    """
    Return a pandas df Styler, which you can use in any Jupyter Notebook. It's 
    designed to by used by df_full_info(), cols_info_float(), and cols_info_other(). Displays large numbers as human readable in k thousands, M Millions, or 
    B billions, and also does 4 significant digits' precision.
    """
    return df.style.format(styler_cell)

def _readable_num(nrows):
    """Adapted from http://stackoverflow.com/a/1094933"""
    if abs(nrows) < 10000.0:
        return nrows
    for unit in ['k', 'M', 'B']:  # Thousand, Million, Billion
        nrows /= 1000.0
        if abs(nrows) < 1000.0:
            break
    return "%3.1f%s" % (nrows, unit)

def _readable_memory(num):
    """From pandas df.info() source code"""
    # returns size in human readable format
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            break
        num /= 1024.0
    return "%3.1f+ %s" % (num, x)


class DFFullInfo():
    """
    Class that creates, displays, and stores info about passed DataFrame. This doesn't
    store the original df, just the summary info about it, so this takes up virtually no memory.
    """

    def __init__(self, df, name):
        self.name = name
        self.df_summary = df_summary(df)
        self.df_cols_float = cols_info_float(df)
        self.df_cols_other = cols_info_other(df)
        self.df_cols_all = self._make_df_cols_all()
        self.html = self._make_html()

    def _make_df_cols_all(self):
        df = pd.merge(self.df_cols_float, self.df_cols_other,
                      how='outer', left_index=True, right_index=True)

        # For each pair of cols (created by pd.merge) like filled_pct_x
        # and filled_pct_y, make a new col filled_pct with the missings in the _x 
        # replaced with the right values from the _fromo
        cns_f = [cn for cn in df.columns if cn.endswith('_x')]
        stems = []
        for cn_f in cns_f:
            stem = cn_f[:-len('_x')]
            stems.append(stem)
            cn_o = stem + '_y'
            ser = df[cn_f].copy()
            ser.loc[ser.isnull()] = df[cn_o].loc[ser.isnull()]
            df[stem] = ser
            del df[cn_f]
            del df[cn_o]
        stems = ['dtype'] + stems  # putting dtype first in the order
        return pd.concat([df[stems], df.drop(stems, axis=1)], axis=1)

    def _make_html(self):
        """
        
        """
        hlst = []  # in hlst, each item is a line of html. Can stay same line for display though since \n isn't html.

        if self.name != '':
            hlst.append('<h3>df_full_info(): ' + self.name + '</h3>')

        hlst.append(self.df_summary.to_html(index=False))
        hlst.append('<h5>cols_info_float():</h5>')
        hlst.append(styler_df(self.df_cols_float).render())
        hlst.append('<h5>cols_info_other():</h5>')
        hlst.append(styler_df(self.df_cols_other).render())
        return '\n'.join(hlst)

    def _repr_html_(self):
        """
        Makes it so the full html comes out when you just type name of the instance in 
        at the end of an ipynb cell. Or you could use "from IPython.display import display", then "display(instance)", without being at the end of a cell.

        We're displaying the float columns and other columns in separate tables. To
        get them in a combined dataframe, either access the .df_cols_all property or
        use to_excel.
        """
        return self.html

    def to_html(self, full_file_path):
        """Writes HTML output to file"""
        with open(full_file_path, "w") as f:
            f.write(df_summary._make_html())

    def to_excel(self, full_file_path):
        with pd.ExcelWriter(full_file_path) as writer:
            self.df_summary.to_excel(writer, sheet_name = 'df_summary')
            self.df_cols_all.to_excel(writer, sheet_name = 'df_cols_all')
            self.df_cols_float.to_excel(writer, sheet_name = 'df_cols_float')
            self.df_cols_other.to_excel(writer, sheet_name = 'df_cols_other')



# < To get info about objects in general > ===========================================

def wit_str(obj, name=''):
    """
    Returns string of info about object, including len() and type().
    "wit" stands for "What Is That?"
    ?obj and help(obj) are Jupyter and Python's built-in alternatives to wit(),
    which honestly may be more useful until more functionality is added here.

    Args:
        obj: object you want info on
        name: what you want to display in the info header
    
    devnote: getting the passed varname as default name would be nice...
    It's easy if it's in globals(), stackoverflow.com/a/22182558
    but otherwise hard. May or may not be possible  to travel up the frames,
    see https://docs.python.org/3/library/inspect.html>
    """

    kMaxStrLen = 1000
    kMaxDocstringLen = 100000

    if not isinstance(name, str):
        raise TypeError('arg name is not a string')

    ret = ''
    ret += 'len: '
    try:
        ret += str(len(obj))
    except TypeError:
        ret += 'N/A'

    ret += '\n' + str(obj)[:kMaxStrLen]
    ret += '\n\ntype: ' + str(type(obj))
    ret += ' | docstring:\n"""' + str(obj.__doc__)[:kMaxDocstringLen]
    return ret

def wit(obj, name=''):
    """Prints string of info about object, including len() and type()."""
    if IPYTHON_RUNNING and isinstance(obj, pd.DataFrame):
        return df_full_info(df=obj, name=name)
    else:
        print(wit_str(obj=obj, name=name))

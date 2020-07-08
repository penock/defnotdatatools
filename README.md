
defnotdatatools package
================================================================================
Definitely Not Data Tools are rough but sometimes-nifty Python data (and other) utilities. The name is a play on my music persona, https://facebook.com/defnotdrphil ... in alpha, not supported, but feel free to ask me about anything: contact me via penock.com or enockphd.com.

This package is in alpha stage, not supported, and all aspects of it could change. But feel free to ask me about anything here--contact me via https://penock.com or https://linkedin.com/in/enockphd



How to import into your Python code
================================================================================
```Python
    import sys
    import os
    PATH_DNDT_PARENT = r'/XXX_THEPARENTDIR_XXX'  # must be parent dir of defnotdatatools
    if PATH_DNDT_PARENT not in sys.path:
        sys.path.append(PATH_DNDT_PARENT)
    from defnotdatatools import iact, misc, missing, timing  # just include the ones you need
```

We avoid doing import * for now because it's severely frowned-upon by Python community. We may figure out some shortcuts system involving an import * to provide easy access to the most frequently used parts of defnotdatatools. (When we do this, note PEP8's advice, "Modules that are designed for use via from M import * should use the __all__ mechanism to prevent exporting globals, or use the older convention of prefixing such globals with an underscore".)



How to import in the special case when you're modifying the defnotdatatools package
================================================================================
Note: IF you're in the process of modifying defnotdatatools package code while using it in IPython, you'll need this or similar reload code, so your modifications get reloaded. (Beware, as you could get confusing errors if defnotdatatools gets partially but not fully updated.)

```Python
    # Alternate import for when you're in Jupyter and are modifying defnotdatatools code
    import sys
    import os
    import importlib
    PATH_DNDT_PARENT = r'/XXX_THEPARENTDIR_XXX'  # must be parent dir of defnotdatatools
    if PATH_DNDT_PARENT not in sys.path:
        sys.path.append(PATH_DNDT_PARENT)
    for module_name in ['iact', 'misc', 'missing', 'timing']:
        try:
            globals()[module_name] = importlib.reload(globals()[module_name])
        except KeyError:
            globals()[module_name] = importlib.import_module('defnotdatatools.' + module_name)
```

import pytest
import warnings

def test_import_gateway():
    try:
        import gateway
    except ImportError:
        raise ImportError("""Can't import gateway library""")

def test_import_hub():
    try:
        from gateway import hub
    except ModuleNotFoundError:
        raise ModuleNotFoundError("""Can't import gateway library""")

def test_function_discover():
    from gateway import hub
    myhub = hub.hub()
    try:
        myhub.discover()
    except Exception as e:
        warnings.warn(UserWarning("""Can't use discover() without bleak!"""))

#def test_debug_test():
#    assert(2==2)

import pytest

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

def test_import_hubclass():
    from gateway import hub
    myhub = hub.hub()
    myhub.discover()

#def test_debug_test():
#    assert(2==2)

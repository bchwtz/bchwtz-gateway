========
Unittest
========

This section of the documentation describes our approach to developing the unit tests.
`pytest` was chosen as the framework for the test scenarios. The scenarios to be run by `pytest` are in the
subdirectory `/tests` formulated. Essentially, the unit test verifies the correct execution of the `setup.py`, 
as well as the modules `hub` and `sensor` and their dependencies. Individual key functions of these modules
are called by the respective test and checked for the occurrence of certain error messages.

To improve continuous code integration, the file `gateway_unittest.yml` was created under the subdirectory `.github/workflows`.
The workflow executes the `setup. py` in a virtual environment and then performs the unittest.

To run the pytest localy type the following command while you are in the gateway directory:

`pytest tests/test_gateway.py`

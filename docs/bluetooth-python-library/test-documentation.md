This module contains multiple software tests concerning the Tag and the hub.
All tests are pure software tests, meaning that all necessary data and devices are being mocked. They give
an overview of what behavior is expected of the methods in the hub and on the tag. 

All tests are primarily written using pytest. For the mocking aspect of the tests the __AsyncMock__ module
from the unittest-package is used. 
A good statingpoint for understanding the pytest library is this article from [real python](https://realpython.com/pytest-python-testing/)
and of course the official [documentation](https://docs.pytest.org/en/7.1.x/)

You do not need an active and flashed tag to test these functions. 
If after your changes some of the tests fail, you broke something. 

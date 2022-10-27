Author: Furkan Tombul

This section will handle all topics regarding integration tests and testautomation. 
## Setup Environment
Before you can start with testing please follow the Getting-Started Guide (README.md) from the gateway folder to setup your Environment.
## Setup Test Environment
In the current folder test_cases you can find all currently developed functions (Testautomation.py) which are needed for our tests.
Additionally you can find all our tests which have to be tested as Jupyter Notebooks (ipynb) in the folder Testcases_ipynb. 

To be able to execute this tests you have to Setup JupyterHub on your raspberry pi. The following link gives a short guide on the installation process

[Setup JupyterHub](https://towardsdatascience.com/setup-your-home-jupyterhub-on-a-raspberry-pi-7ad32e20eed)

## Overview
The files for our tests are structured in the library Testautomation.py and the subfolder Testcases_ipynb.

### Testautomation.py
This library is split into two sections.
In the first section we implement automated testcases including the check, if the test passed or failed.
Also reporting will be included here in the future.

The second sections includes all helping functions which are needed for our tests. This split improves readability
of the code as well as it gives the possibility to test more dynamic by e.g. using specific testdatas.

### Testcases_ipynb
Here we collect all our tests as Notebooks. Every Notebook cover one testcase, which can be directly executed from this file.
The idea behind this is to simplify reproduction of issues and to guarantee all test steps were the same.

You can click on the documentation in this subfolder for additonal information.

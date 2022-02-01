=======================
The Documentation Guide
=======================

This section is for all project members who want to expand or redesign the documentation.
The structure of the project documentation is implemented with the help of  `Sphinx <https://www.sphinx-doc.org/en/master/>`_ . To get started, the following provides some useful information about the 
structure of the documentation and how Sphinx works.


Getting-Started with Sphinx
###########################

Sphinx can be installed on different operating systems. In order to get a detailed overview of all possibilities of the installation, the corresponding chapter of the `program documentation <https://www.sphinx-doc.org/en/master/usage/installation.html>`_ should be looked up here. 
As an example, an installation like:code:’pip' is displayed via the Anaconda command line. To do this, the Anaconda command line must be called first. 
Subsequently, to execute the ’makefile', the directory must be adapted to the cloned Github repository.
Powered by

1. :file:`cd /User/Documents/Github/gateway/` example of the project path
2. :code:`conda install sphinx` at this point we would like to point out again the different installation options.

In a new repository without any documentation, the following command can be used to create a documentation structure.
* `sphinx-quickstart docs`

Alternatively, this command can also be used:

* `sphinx-quickstart docs`

In this repository, the structure has already been created, but the Anaconda command line can also be used to verify a change in the documentation.

* Das :code:`Makefile` kann mittels :code:`make html` ausgeführt werden.


Structure of the Gateway Repsoitories (so far)
**********************************************

Changing the internal referencing or adding new files to the documentation results in a change to the `Index.rst`.
This file is the home page of the documentation and refers to the linked chapters and sub-documents. 
Primarily we use the file format `Restructured Text <https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#sections>`_. 
Further references are made in the footnotes to further sources [1] for a better understanding of the syntax. 
However, `Markdown-Files <https://myst-parser.readthedocs.io/en/latest/sphinx/intro.html>`_ can also be interpreted. 
For more details please refer to the documentation of Sphinx.

::

	gateway
	│   .gitignore
	│   make.bat
	│   Makefile
	│   MANIFEST.in
	│   README.md
	│   requirements.txt
	│   setup.py
	│
	├───.github
	│   └───workflows
	│           gateway_unittest.yml
	│           mf.yml
	│
	├───.idea
	│   │   ...
	│
	├───.spyproject
	│   └───config
	│       │   ...
	│
	├───demos
	│       demo_accelerometer_logging.py
	│       demo_advertisement_logging.py
	│       demo_get_heartbeat.py
	│       demo_set_acceleration_config.py
	│
	├───deployments
	│   │   ...
	│   │
	│   ├───configs
	│   │
	│   ├───nats
	│   │       nats.conf
	│   │
	│   ├───nginx
	│   │   │   ...
	│   │   └───snippets
	│   │
	│   └───ssl
	│       │   ...
	│       │
	│       └───certs
	│               ...
	│
	├───docs
	│   │   conf.py
	│   │   index.rst
	│   │   intro_to_sphinx.rst
	│   │
	│   ├───_build
	│   ├───_static
	│   └───_templates
	|
	├───gateway
	│   │   communication_interface.yml
	│   │   __init__.py
	│   │
	│   ├───experimental
	│   │   │   Client.ipynb
	│   │   │   mfconf.yml
	│   │   │   MQTTprojectEXE.ipynb
	│   │   │   ProcessHandler.py
	│   │   │   settings.py
	│   │   │   __init__.py
	│   │   │
	│   │   ├───flashing
	│   │   │       __init__.py
	│   │   │
	│   │   ├───influxConnector
	│   │   └───mqttThing
	│   │           __init__.py
	│   │
	│   ├───hub
	│   │       AdvertisementDecoder.py
	│   │       AdvertisementLogging.py
	│   │       DataFormats.py
	│   │       decoder.py
	│   │       nix_hci.py
	│   │       nix_hci_dummy.py
	│   │       __init__.py 
	│   │
	│   └───sensor
	│           MessageObjects.py
	│           SensorConfigEnum.py
	│           __init__.py
	│
	├───tests
	│      README.md
	│      test_gateway.py
	│
	├───test_cases
	│   │   README.md
	│   │   Testautomation.py
	│   │
	│   └───Testcases_ipynb
	│           README.MD
	│           RuuviTag_Tests_Documentation.ipynb
	│           TC01_Check_Acceleration_Data.ipynb
	│           TC02_Set_Config_valid.ipynb
	│           TC03_Set_Config_All_valid.ipynb
	│           TC04_Set_Config_invalid.ipynb
	│           TC05_get_flash_statistics.ipynb
	│           TC06_change_logging_state.ipynb
	│           TC_M01_Hard_Reset_Tag.ipynb
	│           TC_M02_Set_Time_longtime.ipynb
	│           TC_M03_Get_Acceleration_Data_drop_connection.ipynb
	│
	└───tools
			set_acceleration_config.py


Configuration of Github pages
******************************


orem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.   

Duis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore eu feugiat nulla facilisis at vero eros et accumsan et iusto odio dignissim qui blandit praesent luptatum zzril delenit augue duis dolore te feugait nulla facilisi. Lorem ipsum dolor sit amet,





[1] https://thomas-cokelaer.info/tutorials/sphinx/rest_syntax.html
[2] https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html#paragraphs





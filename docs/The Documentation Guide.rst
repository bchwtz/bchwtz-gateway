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
	├── docs
	├    ├── build
	├    ├── make.bat
	├    ├── Makefile
	├    └── source
	├        ├── conf.py
	├        ├── index.rst
	├        ├── _static
	├        └── _templates 
	├── gateway
	├      ├── __Init__.py
	├      └── SensorGatewayBleak.py
	├── setup.py 
	├── config.ini
	├── Sensor.log
	├── Makefile



Konfiguration der Github pages
******************************


orem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.   

Duis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore eu feugiat nulla facilisis at vero eros et accumsan et iusto odio dignissim qui blandit praesent luptatum zzril delenit augue duis dolore te feugait nulla facilisi. Lorem ipsum dolor sit amet,





[1] https://thomas-cokelaer.info/tutorials/sphinx/rest_syntax.html
[2] https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html#paragraphs





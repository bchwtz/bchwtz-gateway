import os
from setuptools import find_packages
from setuptools import setup


with open('requirements.txt') as f:
    required = f.read().splitlines()

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
    
    
setup(name='gateway',
      version='v1.2.0',
      author='Team_Gateway',
      #author_email = 'example@adress.com'
      description = "RuuviTag Communication and Data processing tool",
      long_description = long_description,
      long_description_content_type = "text/markdown",
      url = 'https://github.com/bchwtz-fhswf/gateway.git',
      packages = find_packages(),      
      install_requires= required,
      python_requires=">=3.6"
      )
#https://github.com/navdeep-G/samplemod
#https://towardsdatascience.com/create-your-custom-python-package-that-you-can-pip-install-from-your-git-repository-f90465867893
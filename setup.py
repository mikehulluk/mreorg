import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "mreorg",
    version = "0.0.1",
    author = "Mike Hull",
    author_email = "mikehulluk@gmail.com",
    description = ("TODO - add description"),
    license = "BSD",
    keywords = "example documentation tutorial",
    url = "http://packages.python.org/an_example_pypi_project",
    
    package_dir = {'':'src' },

    packages=['mreorg',
              'mreorg.dependancies',
              'mreorg.dependancies.xmlwitch',
              'mreorg.dependancies.glob2',
              'mreorg.curator',
              'mreorg.curator.backend_sim',
              'mreorg.curator.frontend',
              'mreorg.curator.frontend.templates',
              'mreorg.requiredpreimport',
              'mreorg.doctools',
              'mreorg.scriptplots',
              ],
    
    
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)

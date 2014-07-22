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
    version = "0.1.2",
    author = "Mike Hull",
    author_email = "mikehulluk@gmail.com",
    description = ("Tools for organising and simplifying scripts for modelling"),
    license = "BSD",
    url = "https://github.com/mikehulluk/mreorg",

    package_dir = {'':'src' },
    packages=['mreorg',
              'mreorg.dependancies',
              'mreorg.dependancies.xmlwitch',
              'mreorg.dependancies.glob2',
              'mreorg.curator',
              'mreorg.curator.cmdline',
              'mreorg.curator.backend_sim',
              'mreorg.curator.frontend',
              'mreorg.curator.frontend.templates',
              'mreorg.requiredpreimport',
              'mreorg.doctools',
              'mreorg.scriptplots',
              ],
    # Could also have been done with 'scripts=':
    entry_points = {
        'console_scripts': [
            'mreorg.curate = mreorg.curator.cmdline.mreorg_curate:main',
        ],
    },

    package_data={
        'mreorg':[
            'curator/frontend/templates/*.html',
            'curator/frontend/static/javascript/*',
            'curator/frontend/static/customcss/*.css',
            'curator/frontend/static/customcss/images/*',
            'curator/frontend/static/javascript-moment/*',
            'curator/frontend/static/sphinx/*',
            ]
        },


    data_files=[('mreorg/etc', ['etc/configspec.ini']),
                #('config', ['cfg/data.cfg']),
                #('/etc/init.d', ['init-script'])
                ],


    install_requires=['matplotlib','configobj','Django','pygments', 'django-dajaxice'],

    long_description=read('README.txt'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)

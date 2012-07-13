
mreorg - Managing Workflows in Python
======================================

.. contents::
   

Overview
---------

Python is a widely used language in computational sciences for modelling 
and data analysis; however, with large amounts of data, scripts can 
quickly become unwiedly. *mreorg* is a library containing functions and
tools to manage large numbers of scripts and thier output. It was written
by Mike Hull as part of his Ph. D, to help manage scripts used in building
models in computational neuroscience. It is designed to be as non-invasive 
to scripts as possible. An  ``import mreorg`` is generally all that
needs to be added.

Main features:
  
  * Works with matplotlib to:
     - automatically save all plots at the end of a script (no more calls to pylab.save_figure)
     - configure behaviour of ``show()`` using environmental variables,
       so the same script can be used to generate graphs on screen, or just save 
       them to a file, without changing the contents of the file.
  
  * A stand-alone application **curate**, for managing a conllection of 
    scripts. Scripts can be queued
      - web interface to launch scripts and visualise output as html
    


Scripting with *mreorg*
------------------------

*mreorg` allows is configurable based





Managing Simulation with **mreorg.curate**
-------------------------------------------







Configuration
------------------

Environmental Variable
~~~~~~~~~~~~~~~~~~~~~~~

============================= =========================
Environmental variable name
============================= =========================
MREOG_AUTOSAVEFIGURES  

============================= =========================


~/.mreorgrc
~~~~~~~~

For Example::

    default_simulations = [
        "/home/michael/hw_to_come/morphforge/src/morphforgeexamples/singlecell_simulation/*",
        "/home/michael/hw_to_come/morphforge/src/morphforgeexamples/multicell_simulation/**",
        "/home/michael/hw_to_come/hw-results/src/March 2011/s0001/s0001 - Sautois dIN.py",
        "/home/michael/hw_to_come/hw-results/src/**",
    ]

    FILENAME_EXCLUDES = [
        "py.py",
        "__*.py",
        "*parsetab*",
        '/home/michael/hw_to_come/morphforge/src/bin/SimulateBundle.py',
        "*/analysis_dins.py",
        "*/dINFiles.py",
        "preload_files.py",
    ]


    SIMULATION_SQLLITE_FILENAME = '/home/michael/old_home/simmgr.sqlite'
    SIMULATION_IMAGE_STOREDIR = '/home/michael/old_home/.mreorg/images/'

    drop_into_editor_cmds = [
        'gnome-terminal &',
        'gvim "${full_filename}"',
    ]


    COVERAGE_CONFIG_FILE ="/home/michael/hw_to_come/morphforge/etc/.coveragerc"
    COVERAGE_OUTPUT_DIR = "/tmp/morphforge_coverage_output"



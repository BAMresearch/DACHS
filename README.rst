========
Overview
========

Database for Automation and Consistent Holistic Synthesis

.. start-badges

| |version| |commits-since| |license|
| |supported-versions| |wheel| |downloads|
| |cicd| |coverage|

.. |version| image:: https://img.shields.io/pypi/v/dachs.svg
    :target: https://test.pypi.org/project/dachs
    :alt: PyPI Package latest release

.. |commits-since| image:: https://img.shields.io/github/commits-since/BAMresearch/DACHS/v0.5.2.svg
    :target: https://github.com/BAMresearch/DACHS/compare/v0.5.2...main
    :alt: Commits since latest release

.. |license| image:: https://img.shields.io/pypi/l/dachs.svg
    :target: https://en.wikipedia.org/wiki/GNU_General_Public_License
    :alt: License

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/dachs.svg
    :target: https://test.pypi.org/project/dachs
    :alt: Supported versions

.. |wheel| image:: https://img.shields.io/pypi/wheel/dachs.svg
    :target: https://test.pypi.org/project/dachs#files
    :alt: PyPI Wheel

.. |downloads| image:: https://img.shields.io/pypi/dw/dachs.svg
    :target: https://test.pypi.org/project/dachs/
    :alt: Weekly PyPI downloads

.. |cicd| image:: https://github.com/BAMresearch/DACHS/actions/workflows/ci-cd.yml/badge.svg
    :target: https://github.com/BAMresearch/DACHS/actions/workflows/ci-cd.yml
    :alt: Continuous Integration and Deployment Status

.. |coverage| image:: https://img.shields.io/endpoint?url=https://BAMresearch.github.io/DACHS/coverage-report/cov.json
    :target: https://BAMresearch.github.io/DACHS/coverage-report/
    :alt: Coverage report

.. end-badges


Installation
============

::

    pip install dachs

You can also install the in-development version with::

    pip install git+https://github.com/BAMresearch/DACHS.git@main

Usage
=====

To invoke the command line interface for processing experimental log files to the DACHS hierarchical structure and to HDF5 output, run the following to show the usage help::

    python -m dachs -h

Documentation
=============

https://BAMresearch.github.io/DACHS

Development
===========

Assuming the current working directory is the top-level source directory:

1. To run tests only in a clean environment::

    tox -e py

2. For testing generation of the complete data structure in the local environment with stdout&stderr run::

    rm *.h5; pytest -rP --show-capture=all --capture=sys -k test_integral

3. Without *pytest* and without installation, the command line interface can be run by::

    PYTHONPATH=src python -m dachs -h

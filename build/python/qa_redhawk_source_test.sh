#!/bin/sh
export VOLK_GENERIC=1
export GR_DONT_LOAD_PREFS=1
export srcdir=/home/drew/redhawk-gnuradio/gr-redhawk_integration_python/python
export PATH=/home/drew/redhawk-gnuradio/gr-redhawk_integration_python/build/python:$PATH
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH
export PYTHONPATH=/home/drew/redhawk-gnuradio/gr-redhawk_integration_python/build/swig:$PYTHONPATH
/usr/bin/python2 /home/drew/redhawk-gnuradio/gr-redhawk_integration_python/python/qa_redhawk_source.py 

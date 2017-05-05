#!/bin/sh
export VOLK_GENERIC=1
export GR_DONT_LOAD_PREFS=1
export srcdir=/home/drew/redhawk-gnuradio/gr-redhawk_integration_python/build/gr-tutorial/python
export PATH=/home/drew/redhawk-gnuradio/gr-redhawk_integration_python/build/gr-tutorial/build/python:$PATH
export LD_LIBRARY_PATH=/home/drew/redhawk-gnuradio/gr-redhawk_integration_python/build/gr-tutorial/build/lib:$LD_LIBRARY_PATH
export PYTHONPATH=/home/drew/redhawk-gnuradio/gr-redhawk_integration_python/build/gr-tutorial/build/swig:$PYTHONPATH
/usr/bin/python2 /home/drew/redhawk-gnuradio/gr-redhawk_integration_python/build/gr-tutorial/python/qa_my_qpsk_demod_cb.py 

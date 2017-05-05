#!/bin/sh
export VOLK_GENERIC=1
export GR_DONT_LOAD_PREFS=1
export srcdir=/home/drew/redhawk-gnuradio/gr-redhawk_integration_python/build/gr-tutorial/lib
export PATH=/home/drew/redhawk-gnuradio/gr-redhawk_integration_python/build/gr-tutorial/build/lib:$PATH
export LD_LIBRARY_PATH=/home/drew/redhawk-gnuradio/gr-redhawk_integration_python/build/gr-tutorial/build/lib:$LD_LIBRARY_PATH
export PYTHONPATH=$PYTHONPATH
test-tutorial 

#!/usr/bin/python

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Sleep Test
Test the accuracy of the sleep function on a system, as this
has an impact on the performance of filt
"""
#*** Get division to return float:
from __future__ import division

#*** Time stuff:
import datetime
import time

#*** For file path:
import os

#*** Import sys and getopt for command line argument parsing:
import sys, getopt

def main(argv):
    """
    Main function of sleeptest
    """
    version = "0.1.1"

    #*** Initial sleep time (seconds)
    sleep_time = 0.1

    #*** Sleep decrement (seconds)
    sleep_decrement = 0.0001

    finished = 0
    header_row = 1
    output_file = 0
    output_file_enabled = 0
    output_path = 0

    #*** Start by parsing command line parameters:
    try:
        opts, args = getopt.getopt(argv, "hw:Wb:jv",
                                  ["help",
                                   "output-file=",
                                   "output-path=",
                                   "no-header-row",
                                   "version"])
    except getopt.GetoptError as err:
        print "sleeptest: Error with options:", err
        print_help()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print_help()
            sys.exit()
        elif opt in ("-v", "--version"):
            print 'sleeptest.py version', version
            sys.exit()
        elif opt in ("-w", "--output-file"):
            output_file = arg
            output_file_enabled = 1
        elif opt == "-W":
            output_file = "sleeptest_" + \
                              time.strftime("%Y%m%d-%H%M%S.csv")
            output_file_enabled = 1
        elif opt in ("-b", "--output-path"):
            output_path = arg
        elif opt in ("-j", "--no-header-row"):
            header_row = 0

    #*** Display output filename:
    if output_file_enabled:
        if output_path:
            output_file = os.path.join(output_path, output_file)
        print "Results filename is", output_file
        if header_row:
            result_csv_header = "Target_Sleep, Actual_Sleep, " \
                              + "Discrepancy, Percentage_Error\n"
            with open(output_file, 'a') as the_file:
                the_file.write(result_csv_header)
    else:
        print "Not outputing results to file, as option not selected"



    while not finished:
        if sleep_time > 0:
            #*** Get current time:
            start_time = time.time()
            #*** Sleep for interval seconds:
            time.sleep(sleep_time)
            #*** Get end time:
            end_time = time.time()
        else:
            break

        #*** Calculate accuracy:
        actual_sleep = end_time - start_time
        discrepancy = actual_sleep - sleep_time
        if discrepancy:
            percentage = (discrepancy / sleep_time) * 100
        else:
            percentage = 0

        print "Target sleep:", sleep_time, \
            " Actual Sleep:", actual_sleep, \
            " Discrepancy:", discrepancy, \
            " Percentage:", percentage
        if output_file_enabled:
            result_csv = str(sleep_time) + "," + str(actual_sleep) + \
                    "," + str(discrepancy) + "," + str(percentage) +"\n"
            with open(output_file, 'a') as the_file:
                        the_file.write(result_csv)

        #*** Decrement sleep time:
        sleep_time = sleep_time - sleep_decrement

def print_help():
    """
    Print out the help instructions
    """
    print """
sleeptest
---------------------------------

This code is used to test and record the accuracy of
system sleep calls.

Usage:
  python sleeptest.py [options]

Options:
 -h  --help                Display this help and exit
 -w  --output-file         Specify an output filename
 -W                        Output results to default filename
                             default is format YYYYMMDD-HHMMSS.csv
 -b  --output-path         Specify path to output file directory
 -j  --no-header-row       Suppress writing header row into CSV
 -v, --version             Output version information and exit

 Results are written in following CSV format (if -w is specified)
 """
    return()

if __name__ == "__main__":
    #*** Run the main function with command line
    #***  arguments from position 1
    main(sys.argv[1:])


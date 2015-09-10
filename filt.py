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
Flow Incremental Load Test (filt)
.
DIRE WARNING:
------------
THIS IS A NETWORK STRESS TOOL - DO NOT USE THIS
PROGRAM UNLESS YOU KNOW WHAT YOU ARE DOING AND
ARE AUTHORISED TO DO IT. THE LOAD GENERATED MAY
CAUSE NETWORK PERFORMANCE ISSUES!!!!!!!
.
This code is used to stress test a network by
incrementally increasing a new flows/second load.
.
Do not use this code on production networks - it
is proof of concept code and carries no warrantee
whatsoever. You have been warned.
.
May need to install scapy if not already installed
.
Uses raw socket to improve packet sending performance
.
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

#*** Import scapy for building packets:
from scapy.all import Ether, IP, TCP, UDP, Raw

#*** For raw socket sending of packets:
import socket

def main(argv):
    """
    Main function of filt
    """
    version = "0.1.5"
    loop_overhead_time = 0
    loop_min_overhead_time = 0
    avg_overhead_time = 0
    interval_overhead_sum = 0
    first_time = 1
    time_remaining_in_interval = 0
    prev_loop_finish_time = 0
    sleep_time = 0
    max_rate = 0
    min_rate = 0
    prev_pkt_sent_time = 0
    header_row = 1
    elapsed_time = 0
    initial_flow_rate = 1
    flow_rate_increase = 1
    max_flow_rate = 100
    target_ip = 0
    increment_interval = 1
    bypass_warn = 0
    protocol = 6
    sport = 1025
    dport = 12345
    finished = 0
    output_file = 0
    output_file_enabled = 0
    output_path = 0
    data = "Data in packet not specified, this is the default..."
    target_mac = "00:01:02:03:04:05"
    packets_sent = 0
    prev_packets_sent = 0
    actual_flow_rate = 0
    debug = 0
    algorithm = 'make-good'

    #*** Start by parsing command line parameters:
    try:
        opts, args = getopt.getopt(argv, "hr:f:m:t:c:p:d:w:Wb:jea:v",
                                  ["help",
                                   "initial-flow-rate=",
                                   "flow-rate-increase=",
                                   "max-flow-rate=",
                                   "target-ip=",
                                   "increment-interval=",
                                   "bypass-warn",
                                   "protocol=",
                                   "dport=",
                                   "output-file=",
                                   "output-path=",
                                   "no-header-row",
                                   "elapsed-time",
                                   "debug",
                                   "algorithm=",
                                   "version"])
    except getopt.GetoptError as err:
        print "filt: Error with options:", err
        print_help()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print_help()
            sys.exit()
        elif opt in ("-v", "--version"):
            print 'filt.py version', version
            sys.exit()
        elif opt in ("-r", "--initial-flow-rate"):
            initial_flow_rate = float(arg)
        elif opt in ("-f", "--flow-rate-increase"):
            flow_rate_increase = float(arg)
        elif opt in ("-m", "--max-flow-rate"):
            max_flow_rate = float(arg)
        elif opt in ("-t", "--target-ip"):
            target_ip = arg
        elif opt in ("-c", "--increment-interval"):
            increment_interval = float(arg)
        elif opt == "--bypass-warn":
            bypass_warn = 1
        elif opt in ("-p", "--protocol"):
            protocol = float(arg)
        elif opt in ("-d", "--dport"):
            port = float(arg)
        elif opt in ("-w", "--output-file"):
            output_file = arg
            output_file_enabled = 1
        elif opt == "-W":
            output_file = time.strftime("%Y%m%d-%H%M%S.csv")
            output_file_enabled = 1
        elif opt in ("-b", "--output-path"):
            output_path = arg
        elif opt in ("-j", "--no-header-row"):
            header_row = 0
        elif opt in ("-e", "--elapsed-time"):
            elapsed_time = 1
        elif opt == "--debug":
            print "Debug is on"
            debug = 1
        elif opt in ("-a", "--algorithm"):
            algorithm = arg

    if not target_ip:
        #*** We weren't passed a target IP so have to exit
        print "filt: Error, no target IP. Exiting..."
        sys.exit()

    #*** Display output filename:
    if output_file_enabled:
        if output_path:
            output_file = os.path.join(output_path, output_file)
        print "Results filename is", output_file
    else:
        print "Not outputing results to file, as option not selected"

    if not bypass_warn:
        #*** Display a warning message and ask for
        #*** explicit permission to proceed:
        if not warning_challenge():
            sys.exit()
    else:
        print "bypassing warning... be aware that this program"
        print "generates stress on network"

    print "================================================="
    print "WARNING!!!!: Starting network flow stress test..."
    print "================================================="
    time.sleep(1)

    print "Using", algorithm, "algorithm to calculate packet spacing"

    target_flow_rate = initial_flow_rate
    last_increment_time = time.time()

    #*** Build packet:
    if protocol == 6:
        #*** TCP packet:
        pkt = Ether(dst=target_mac)/IP(dst=target_ip)/TCP(sport=sport,
                                             dport=dport)/Raw(load=data)
    elif protocol == 17:
        #*** UDP packet:
        pkt = Ether(dst=target_mac)/IP(dst=target_ip)/UDP(sport=sport,
                                             dport=dport)/Raw(load=data)
    else:
        print "ERROR: unknown protocol", protocol
        print "Exiting..."
        sys.exit()

    #*** Create a raw socket:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, \
                                                   socket.IPPROTO_RAW)
    except socket.error, msg:
        print 'Socket could not be created. Error Code : ' \
                                  + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()

    #*** Use for base for calculating total elapsed time:
    base_start_time = time.time()

    #*** Start the packet sending loop:
    while not finished:
        loop_start_time = time.time()
        #*** Send a packet over raw socket for speed:
        strpkt = str(pkt)
        s.sendto(strpkt, (target_ip, 0))
        pkt_sent_time = time.time()
        packets_sent += 1
        packets_sent_in_interval = packets_sent - prev_packets_sent

        #*** Accumulate stats max and min instantaneous rates:
        if prev_pkt_sent_time:
            prev_rate = float(1/(pkt_sent_time - prev_pkt_sent_time))
            if prev_rate > max_rate:
                max_rate = prev_rate
            if prev_rate < min_rate:
                min_rate = prev_rate
            if not min_rate:
                min_rate = prev_rate
        prev_pkt_sent_time = pkt_sent_time

        #*** Increment packet source port:
        sport += 1
        if sport > 65535:
            sport = 1025

        #*** Update source port in packet structure:
        if protocol == 6:
            #*** Update TCP source port:
            pkt[TCP].sport = sport
        elif protocol == 17:
            #*** Update UDP source port:
            pkt[UDP].sport = sport

        time_remaining_in_interval = increment_interval - \
                                (time.time() - last_increment_time)

        if debug:
            print "===================="
            print "t = ", time_remaining_in_interval
            print "x = ", target_flow_rate
            print "i = ", increment_interval
            print "q = ", packets_sent_in_interval
            print "h = ", avg_overhead_time

        #*** Calculate the time to sleep for before running
        #***  packet loop again:

        if algorithm == 'flat-top':
            sleep_time = float(1/target_flow_rate) - \
                                            loop_min_overhead_time
        elif algorithm == 'make-good':
            outstanding_packets_in_interval = (target_flow_rate *
                increment_interval) - packets_sent_in_interval
            if outstanding_packets_in_interval > 0:
                numerator = float(time_remaining_in_interval - \
                                (1/target_flow_rate))
                denominator = outstanding_packets_in_interval
                if debug:
                    print "numerator is", numerator, "denominator is", \
                               denominator
                sleep_time = float(numerator / denominator) - \
                                      avg_overhead_time
                if debug:
                    print "sleep is", sleep_time

            else:
                sleep_time = time_remaining_in_interval
        else:
            print "Unknown algorithm type", algorithm, "Exiting...."
            sys.exit()

        if debug:
            print "d = ", sleep_time

        #*** Per-loop calcs for how long to sleep... zzzz
        loop_finish_time = time.time()
        if not prev_loop_finish_time:
            prev_loop_finish_time = loop_start_time
        #*** Calculate overheads:
        loop_overhead_time = (loop_finish_time - loop_start_time)
        if not loop_min_overhead_time:
            loop_min_overhead_time = loop_overhead_time
        elif loop_overhead_time < loop_min_overhead_time:
            loop_min_overhead_time = loop_overhead_time
        interval_overhead_sum += loop_overhead_time
        avg_overhead_time = float(interval_overhead_sum /
                                        packets_sent_in_interval)

        prev_loop_finish_time = loop_finish_time

        if sleep_time > 0:
            #*** Sleep for interval seconds:
            time.sleep(sleep_time)

        #*** Check if we need to up the target flow rate:
        if packets_sent_in_interval >= target_flow_rate * \
                                            increment_interval:
            #*** Start a new interval
            #*** Calculate actual average flow rate since last increase:
            actual_flow_rate = packets_sent_in_interval / \
                                 (loop_start_time - last_increment_time)

            #*** Increase target flow rate:
            target_flow_rate = target_flow_rate + flow_rate_increase
            #*** Print to screen:
            print "New target:", target_flow_rate, \
                       "Prev avg:", actual_flow_rate, \
                       "Prev max:", max_rate, \
                       "Prev min:", min_rate
            if output_file_enabled:
                if first_time and header_row:
                    #*** Write a header row to CSV:
                    header_csv = "time,"
                    if elapsed_time:
                        header_csv += "elapsed-time,"
                    header_csv += "next target-rate(pps)," \
                                  + "previous actual-rate(pps)," \
                                  + "previous interpacket max rate," \
                                  + "previous interpacket min rate," \
                                  + "\n"
                    with open(output_file, 'a') as the_file:
                        the_file.write(header_csv)
                    first_time = 0
                timenow = datetime.datetime.now()
                timestamp = timenow.strftime("%H:%M:%S")
                result_csv = str(timestamp) + ","
                if elapsed_time:
                    result_csv += str(time.time() - base_start_time) \
                        + ","
                result_csv += str(target_flow_rate) \
                    + "," + str(actual_flow_rate) \
                    + "," + str(max_rate) \
                    + "," + str(min_rate) \
                    + "\n"
                with open(output_file, 'a') as the_file:
                    the_file.write(result_csv)

            last_increment_time = loop_start_time
            max_rate = 0
            min_rate = 0
            interval_overhead_sum = 0
            loop_min_overhead_time = 0
            if target_flow_rate > max_flow_rate:
                print "reached maximum flow rate, exiting..."
                break
            prev_packets_sent = packets_sent

def warning_challenge():
    """
    Display a warning statement and ask for
    acceptance
    """
    print """
DIRE WARNING:
------------
THIS IS A NETWORK STRESS TOOL - DO NOT USE THIS
PROGRAM UNLESS YOU KNOW WHAT YOU ARE DOING AND
ARE AUTHORISED TO DO IT. THE LOAD GENERATED MAY
CAUSE NETWORK PERFORMANCE ISSUES!!!!!!!

If you assume all liability and wish to continue
then type yes:
"""
    answer = raw_input("> ")
    if answer == "yes":
        return True
    else:
        print "Exiting...."
        sys.exit()

def print_help():
    """
    Print out the help instructions
    """
    print """
Flow Incremental Load Test (filt)
---------------------------------

This code is used to stress test a network by
incrementally increasing a new flows/second load,
with results written to file for analysis over time.

Usage:
  python filt.py -t TARGET_IP [options]

Example usage:
  python filt.py <TBD>

Options:
 -h, --help                Display this help and exit
 -r, --initial-flow-rate   Initial new flow rate
                             (default is 1 new flow per second)
 -f, --flow-rate-increase  Increase in new flows per second per second
                             (default is 1 new flow/s/s)
 -m, --max-flow-rate       Maximum new flow rate before exiting
                             (default is 100 new flows per second)
 -t, --target-ip           Target IP address (required)
 -c, --increment-interval  Interval between incrementing flow rate
                             (default is 1 second)
     --bypass-warn         Bypass the warning message
 -p, --protocol            IP protocol number: 6 for TCP, 17 for UDP
 -d, --dport               Destination port number
 -w, --output-file         Specify an output filename
 -W                        Output results to default filename
                             default is format YYYYMMDD-HHMMSS.csv
 -b, --output-path         Specify path to output file directory
 -j  --no-header-row       Suppress writing header row into CSV
 -e  --elapsed-time        Write an elapsed time column into CSV
                             default is to not write this extra column
     --debug               Turn on debug
 -a  --algorithm           Select packet rate algorithm
                             default is 'make-good'
                             alternative is 'make-good'
 -v, --version             Output version information and exit

 Results are written in following CSV format (if -w is specified):
 <timestamp>,<target_rate>,<actual_rate>
 """
    return()

if __name__ == "__main__":
    #*** Run the main function with command line
    #***  arguments from position 1
    main(sys.argv[1:])

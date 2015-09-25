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

#*** Time stuff:
import datetime
import time

#*** Initial sleep time (seconds)
sleep_time = 0.1

#*** Sleep decrement (seconds)
sleep_decrement = 0.0001

finished = 0

output_file = "sleeptest_" + time.strftime("%Y%m%d-%H%M%S.csv")

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

    print "Target sleep:", sleep_time, " Actual Sleep:", actual_sleep, \
            " Discrepancy:", discrepancy
    result_csv = str(sleep_time) + "," + str(actual_sleep) + "," \
                    + str(discrepancy) + "\n"
    with open(output_file, 'a') as the_file:
                        the_file.write(result_csv)
    #*** Decrement sleep time:
    sleep_time = sleep_time - sleep_decrement




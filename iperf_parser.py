#!/usr/bin/env python3

import os
import re
import time
import json
from glob import iglob
from datetime import datetime
from collections import defaultdict
import logging

logging.basicConfig(level=logging.DEBUG)

def iperf_parser(logger, line):
    iperf3_tbl = defaultdict(list)

    logdate, payload = line.split('.log:')
    logname = logdate.split('-')

    # Convert the iso8601 date into a unix timestamp, assuming the timestamp
    # string is in the same timezone as the machine that's parsing it.
    date = "{year}-{month}-{day_time}".format(year=logname[2], month=logname[3], day_time=logname[4])
    timestamp = datetime.strptime(date, "%Y-%m-%dT%H:%M")
    timestamp = time.mktime(timestamp.timetuple())
    
    line = payload

    header = re.search('\[\sID\]\s(\w+)\s+(\w+)\s+(\w+)\s+(\w+)', line)
    info = re.search('\[\s+5\]\s+([0-9]*\.?[0-9]+-[0-9]*\.?[0-9]+)\s+sec\s+([0-9]*\.?[0-9]+)\s([M|G|K]Bytes)\s+([0-9]*\.?[0-9]+)\s+(\w+/sec)\s+\d+\s+[0-9]*\.?[0-9]+\s+([M|G|K]Bytes)', line)
    receiver = re.search('\[\s+5\]\s+([0-9]*\.?[0-9]+-[0-9]*\.?[0-9]+)\s+sec\s+([0-9]*\.?[0-9]+)\s([M|G|K]Bytes)\s+([0-9]*\.?[0-9]+)\s+(\w+/sec)\s+receiver', line)
    sender =   re.search('\[\s+5\]\s+([0-9]*\.?[0-9]+-[0-9]*\.?[0-9]+)\s+sec\s+([0-9]*\.?[0-9]+)\s([M|G|K]Bytes)\s+([0-9]*\.?[0-9]+)\s+(\w+/sec)\s+\d+\s+sender', line)

    if header:
        pass
    if info:
        pass
    if receiver:
        if receiver.group(3) == 'GBytes':
            iperf3_tbl["bitrate_receiver"].append(float(receiver.group(4)))
        else:
            iperf3_tbl["bitrate_receiver"].append(float(receiver.group(4))/1024)
    #if sender:
    #    if sender.group(3) == 'GBytes':
    #        iperf3_tbl["bitrate_sender"].append(float(sender.group(4)))
    #    else:
    #        iperf3_tbl["bitrate_sender"].append(float(sender.group(4))/1024)

    # Return the output as a tuple
    return ("hpc_networking", timestamp, iperf3_tbl['bitrate_receiver'][0], 
                                                                        {"metric_type": "gauge",
                                                                         "unit": "bytes"})

def test():
    # Set up the test input and expected output
    test_input = "logs/spartan-nci-2017-11-30T20:14.log:[  5]   0.00-10.10  sec   350 MBytes   291 Mbits/sec                  receiver"
    expected = ('hpc_networking', 1512033240.0, 0.2841796875, {'metric_type': 'gauge', 'unit': 'bytes'})

    # Call the parse function
    actual = iperf_parser(logging, test_input)

    # Validate the results
    assert expected == actual, "%s != %s" % (expected, actual)
    print('test passes')


if __name__ == '__main__':
    # For local testing, callable as "python /path/to/parsers.py"
    test()

    #print("machine, timestamp, ingress, egress")
    #for filename in iglob('/home/ubuntu/logs/spartan-novastor-2017-11-30T11:05.log'):
    #    data = parse_iperf(logging, filename)
    #    print(json.dumps(data))
        #print("{}, {}, {}, {}".format(data[0], data[1], data[2], data[3]))

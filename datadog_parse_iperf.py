#!/usr/bin/env python

import os
import re
import time
import json
from glob import iglob
from datetime import datetime
from collections import defaultdict
import logging

logging.basicConfig(level=logging.DEBUG)

def parse_iperf(logger, filename):
    iperf3_tbl = defaultdict(list)
    metric_name = 'spartan-novastor'

    with open(filename, 'r') as f:
        # Convert the iso8601 date into a unix timestamp, assuming the timestamp
        # string is in the same timezone as the machine that's parsing it.
        timestamp = datetime.strptime(os.path.basename(f.name), "{system}-%Y-%m-%dT%H:%M.log".format(system=metric_name))
        timestamp = time.mktime(timestamp.timetuple())

        # Failed test due to node down, therefore empty log file
        #fsize = os.stat(f.name).st_size
        if os.path.getsize(filename) != 1124:
            return (metric_name, timestamp, 0, 0, {"metric_type": "histogram", "unit": "bytes"})

        for line in f:
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
                if sender:
                    if sender.group(3) == 'GBytes':
                        iperf3_tbl["bitrate_sender"].append(float(sender.group(4)))
                    else:
                        iperf3_tbl["bitrate_sender"].append(float(sender.group(4))/1024)

    # Return the output as a tuple
    return (metric_name, timestamp, iperf3_tbl['bitrate_receiver'][0], iperf3_tbl['bitrate_sender'][0],
                                                                        {"metric_type": "histogram",
                                                                         "unit": "bytes"})

def test():
    # Set up the test input and expected output
    test_input = "spartan-novastor-2017-11-29T10:45.log"
    expected = ("spartan-novastor", 1511912700.0, 0.2001953125, 0.208984375, {"metric_type": "histogram", "unit": "bytes"})

    # Call the parse function
    actual = parse_iperf(logging, test_input)

    # Validate the results
    assert expected == actual, "%s != %s" % (expected, actual)
    print 'test passes'


if __name__ == '__main__':
    # For local testing, callable as "python /path/to/parsers.py"
    #test()
    for filename in iglob('iperf-runs/*.log'):
        data = parse_iperf(logging, filename)
        print(json.dumps(data))

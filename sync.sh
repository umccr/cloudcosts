#!/bin/bash
rsync -a --progress raijin:iperf-runs/*.log logs/
rsync -a --progress spartan:iperf-runs/*.log logs/

egrep receiver logs/*.log | grep nci > hpc_networks.log

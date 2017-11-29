#!/bin/bash
rsync -a --progress raijin:iperf-runs/*.log .
rsync -a --progress spartan:iperf-runs/*.log .

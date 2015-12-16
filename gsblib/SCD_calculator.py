#!/usr/bin/env python
# -*- coding: utf8 -*-
""" SCD_calculator: Will do something fancy"""
from __future__ import print_function, unicode_literals
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import os
import sys
import subprocess

__author__ = "Sébastien Buchoux"
__email__ = "sebastien.buchoux@gmail.com"
__copyright__ = "Copyright 2015, Sébastien Buchoux"
__license__ = "GPLv3"
__version__ = "1.0"


def populate_parser(parent_parser):
    parser = parent_parser.add_parser("trajorder",
                                      description="Process GROMACS trajectory to calculate "
                                                  "SCD along the trajectory",
                                      formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument("-n", help="Index group defining lipid chains", required=True,
                        dest="index_file")

    parser.add_argument("-f", help="Trajectory file", required=True,
                        dest="trajectory_file")

    parser.add_argument("-s", help="Topology file", required=True,
                        dest="topology_file")

    parser.add_argument("-t", help="Time frame to consider (in ns)", type=int, default=100,
                        dest="time_frame")

    parser.add_argument("-r", help="Time resolution (in ns)", type=int, default=50,
                        dest="resolution")

    parser.add_argument("-d", help="Path where results should be stored", default="Analysis/",
                        dest="target_dir")

    parser.add_argument("--force", help="Force recalculation", action="store_true", default=False)

    parser.set_defaults(func=run)


def run(args):
    target_dir = args.target_dir

    if not os.path.exists(target_dir):
        os.mkdir(target_dir)
    elif not os.path.isdir(target_dir):
        print("ERROR: '%s' exists but is not a directory!" % target_dir)
        sys.exit(1)

    time_frame = args.time_frame
    resolution = args.resolution
    index_file = args.index_file
    trajectory_file = args.trajectory_file
    topology_file = args.topology_file
    force = args.force
    basecmd = ["gmx", "order", "-n", index_file, "-nr", index_file, "-f", trajectory_file,
               "-s", topology_file, "-od"]

    basename = os.path.splitext(index_file)[0]

    must_continue = True
    current_time = 0
    while must_continue:
        # delete unused order.xvg
        try:
            os.remove("order.xvg")
        except OSError:
            pass

        target_path = os.path.join(target_dir, "SCD_%s_%05i_dt%i.xvg" % (basename, current_time,
                                                                         time_frame))

        cmd = list(basecmd)
        cmd.extend([target_path, "-b", "%i" % (current_time * 1000), "-e",
                    "%i" % ((current_time + time_frame) * 1000)])

        print("Running gmx order for %i to %i ns... " % (current_time, current_time+time_frame),
              end="")
        sys.stdout.flush()

        if os.path.exists(target_path) and not force:
            print("SKIPPED!")

        else:
            try:
                p = subprocess.Popen(cmd, stderr=subprocess.PIPE)
                stdoutdata, stderrdata = p.communicate()
                ret_val = p.returncode
            except KeyboardInterrupt:
                print("ABORTED!")
                break

            if ret_val == 0:
                print("OK")
            else:
                get_next = False
                reason = "Unknown"
                for line in stderrdata.splitlines():
                    if get_next:
                        reason = line
                        break
                    if line == "Fatal error:":
                        get_next = True

                print("FAILED! (Reason: %s)" % reason)
                must_continue = False

        current_time += resolution

    print("Done with gmx order!")



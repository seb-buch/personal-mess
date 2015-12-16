#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 12 21:06:51 2015

@author: sebastien
"""
from __future__ import print_function
from argparse import ArgumentDefaultsHelpFormatter
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import sys


def populate_parser(parent_parser):
    parser = parent_parser.add_parser("showxvg",
                                      description="Plot and show a .xvg file",
                                      formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument("xvgfile", help="Gromacs-generated .xvg file")

    parser.set_defaults(func=run)


def run(args):
    plt.style.use('ggplot')
    mpl.rc('lines', linewidth=2, markeredgewidth=1, markersize=10)
    mpl.rc('axes', labelsize='x-large', titlesize="xx-large")
    mpl.rc('xtick', labelsize="x-large")
    mpl.rc('ytick', labelsize="x-large")

    title = "Title"
    xaxis_title = "X axis"
    yaxis_title = "Y axis"
    x = []
    ys = []
    labels = []

    try:
        with open(args.xvgfile) as fp:
            for line in fp:
                line = line.strip()

                if line.startswith("#"):
                    continue

                if line.startswith("@"):
                    line = line.split()
                    if len(line) == 2:
                        continue

                    if line[1] == "title":
                        title = " ".join(line[2:]).strip("\"")
                    elif line[1] == "xaxis":
                        xaxis_title = " ".join(line[3:]).strip("\"")
                    elif line[1] == "yaxis":
                        yaxis_title = " ".join(line[3:]).strip("\"")
                    elif line[1].startswith("s") and line[2] == "legend":
                        labels.append(" ".join(line[3:]).strip("\""))
                else:
                    line = [float(val) for val in line.split()]
                    x.append(line[0])

                    for i, val in enumerate(line[1:]):
                        try:
                            ys[i].append(val)
                        except IndexError:
                            ys.append([val, ])
    except IOError:
        print("ERROR: Could not read '%s'" % sys.argv[1])
        sys.exit(1)
    except (ValueError, TypeError):
        print("ERROR: Invalid .xvg file")
        sys.exit(1)

    if len(labels) != 0:
        if len(ys) != len(labels):
            print("ERROR: Incomplete legend!")
            sys.exit(1)

    x = np.array(x)
    if len(x) > 500:
        marker = ""
    else:
        marker = "+"

    for i, vals in enumerate(ys):
        if len(labels) == 0:
            label = "value #%i" % (i + 1)
        else:
            label = labels[i]

        plt.plot(x, vals, label=label, marker=marker)

    if len(labels) != 0:
        plt.legend(loc="best")

    plt.xlabel(xaxis_title)
    plt.ylabel(yaxis_title)
    plt.title(title)
    plt.tight_layout()

    print("Plotting %s (backend: %s)..." % (args.xvgfile, mpl.backends.backend))
    plt.show()
    print("Done")

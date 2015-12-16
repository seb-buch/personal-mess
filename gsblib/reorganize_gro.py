#!/usr/bin/env python
# -*- coding: utf8 -*-
""" reorganize_gro: Will do something fancy"""
from __future__ import print_function
from argparse import ArgumentDefaultsHelpFormatter

__author__ = "Sébastien Buchoux"
__email__ = "sebastien.buchoux@gmail.com"
__copyright__ = "Copyright 2015, Sébastien Buchoux"
__license__ = "GPLv3"
__version__ = "1.0"


def populate_parser(parent_parser):
    parser = parent_parser.add_parser("reorganize",
                                      description="Read and reorganize a .gro file",
                                      formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument("-f", help=".gro file to reorganize", required=True,
                        dest="input_file")

    parser.add_argument("-o", help="Name of the reorganized output file (.gro file)",
                        required=True,
                        dest="output_file")

    parser.set_defaults(func=run)


def run(args):
    other_lines = []

    RESNAMES_IONS = ["NA+", "CL-", "ION"]
    RESNAME_SOLVENT = ["W", "PW", "SOL"]
    RESNAME_LIPIDS = ["DPPC", "DPPG", "DMPC"]
    RESNAME_OTHERS = ["DSCD", "DOCD"]
    KNOWN_RESNAMES = RESNAMES_IONS + RESNAME_SOLVENT + RESNAME_LIPIDS + RESNAME_OTHERS

    content = []

    residues = {}
    known_lines = {}
    known_order = []
    last_resid = -1

    fin = args.input_file
    fout = args.output_file
    with open(fin, "r") as fp:
        content += [fp.readline()]

        num_atoms = int(fp.readline())
        content += ["%i\n" % num_atoms]
        for i in range(num_atoms):
            line = fp.readline()
            resid = int(line[:5])
            resname = line[5:9].strip()

            if resid != last_resid:
                last_resid = resid
                try:
                    residues[resname] += 1
                except KeyError:
                    residues[resname] = 1

            if resname in KNOWN_RESNAMES:
                try:
                    known_lines[resname].append(line)
                except KeyError:
                    known_lines[resname] = [line, ]
                    known_order.append(resname)
            else:
                other_lines.append(line)

        box = fp.readline()

    with open(fout, "w") as fp:
        fp.writelines(content)
        fp.writelines(other_lines)
        for resname in known_order:
            fp.writelines(known_lines[resname])
        fp.write(box)

    print("%s reorganized and saved to %s" % (fin, fout))
    print("Useful for topology:")
    for resname in known_order:
        print("%s\t%i" % (resname, residues[resname]))

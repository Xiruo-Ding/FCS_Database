#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Collects and process flow QC data

@author: Daniel Herman MD, PhD
"""
__author__ = "Daniel Herman, MD"
__copyright__ = "Copyright 2014, Daniel Herman"
__license__ = "GPL v3"
__version__ = "1.0"
__maintainer__ = "Daniel Herman"
__email__ = "hermands@uw.edu"
__status__ = "Production"

from FlowAnal.database.FCS_database import FCSdatabase
from FlowAnal.FlowQC import FlowQC
from FlowAnal.QC_subroutines.Flow_Comparison import Flow_Comparison
from __init__ import add_filter_args

import logging
import os
log = logging.getLogger(__name__)


def build_parser(parser):
    parser.add_argument('anal',
                        help='Type of analysis',
                        choices=['compare', 'compensation'], type=str)
    parser.add_argument('--db', '-db', help='sqlite3 db with flow stats data \
    [default: db/fcs_stats.db]',
                        default="db/fcs_stats.db", type=str)
    parser.add_argument('--outdb', '-outdb', help='sqlite3 db to store output dfs \
    [default: db/fcs_stats.db]',
                        default="db/fcs_qc.db", type=str)
    parser.add_argument('-testing', '--testing',
                        action='store_true')
    parser.add_argument('-table-format', '--table-format', dest='table_format',
                        default='tall', type=str)
    parser.add_argument('--add-peaks', dest='add_peaks',
                        action='store_true')
    parser.add_argument('--add-beads', dest='add_beads',
                        action='store_true')
    parser.add_argument('--plot-1D-intensities', dest='plot_1D_intensities',
                        action='store_true')
    parser.add_argument('--npeaks', default=None, dest='npeaks', type=int)
    parser.add_argument('--cross-anal', '--crossanal', dest='crossanal',
                        action='store', default=None,
                        help='do paired analyses across tube types [tubes] or cytnums [cytnum]')
    parser.add_argument('--outp', '--prefix', dest='outp',
                        type=str, help='file prefix for output',
                        default='test_out')
    parser.add_argument('--workers', help='Number of cores to use for multiprocessing',
                        default=None,
                        type=int)
    parser.add_argument('--comparison', help='Type of comparison', default='global', type=str,
                        choices=["global", "peaks"])
    parser.add_argument('--restrict-to-pairs', dest='restrict_to_pairs',
                        help='Restrict samples to where have multiple samples per case',
                        action='store_true')
    parser.add_argument('--linear_align', '--linear-align', dest='linear_align',
                        action='store_true')
    parser.add_argument('-split', '--split_array_factor', default=None,
                        type=int)
    parser.add_argument('-name', '--name', default='test',
                        type=str)
    add_filter_args(parser)


def action(args):
        # Connect to database
        dbcon = FCSdatabase(db=args.db, rebuild=False)
        print "Processing database %s" % args.db

        a = FlowQC(dbcon=dbcon, make_qc_data=False)
        a.plot_beads(**vars(args))

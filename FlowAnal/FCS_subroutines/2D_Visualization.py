# -*- coding: utf-8 -*-
"""
Created on Fri 21 Nov 2014 10:59:16 AM PST
This will generate an image file containing the antigens which high comp issues

@author: David Ng, MD
"""
import matplotlib
matplotlib.use('Agg')  # Turn off interactive X11 stuff...
import matplotlib.pyplot as plt
import numpy as np

import logging
log = logging.getLogger(__name__)

schema = {'comp': {1: {1: (5, 10), 2: (6, 10)},
                   2: {1: (6, 5), 2: (7, 5), 3: (8, 5), 4: (9, 5)},
                   3: {1: (7, 6), 2: (8, 6), 3: (9, 6)},
                   4: {1: (11, 7), 2: (8, 7), 3: (9, 7)},
                   5: {1: (9, 8), 2: (13, 8)},
                   6: {1: (14, 9)},
                   7: {1: (12, 11), 2: (13, 11)},
                   8: {1: (13, 12), 2: (14, 12)},
                   9: {1: (14, 13)}}}


class Visualization_2D(object):
    def __init__(self, FCS, outfile, outfiletype, schema_choice='comp'):
        self.FCS = FCS
        self.filename = outfile
        self.filetype = outfiletype

        log.info('Plotting %s to %s' % (self.FCS.case_tube, outfile))
        self.display_projection(schema=schema_choice)

    def display_projection(self, schema_choice):
        self.walk_schema(schema=schema[schema_choice])
        self.setup_plotting()

    def setup_plotting(self):
        fig = plt.gcf()
        fig.set_size_inches(12, 20)
        fig.tight_layout()
        fig.savefig(self.filename, dpi=500, bbox_inches='tight', filetype=self.filetype)

    def walk_schema(self, schema_i):
        """
        dict keyed on row, column with value of parameter x, y
        """

        for i, value in schema_i.iteritems():
            for j, items in value.iteritems():
                plt.subplot2grid((9, 4), (i-1, j-1))
                self.plot_2d_hist(items[0], items[1])

        plt.subplot2grid((9, 4), (8, 3))
        self.plot_2d_hist(4, 14)

    def plot_2d_hist(self, x, y, downsample=0.2):
        x_lb = self.FCS.parameters.iloc[:, x-1].loc['Channel_Name']
        y_lb = self.FCS.parameters.iloc[:, y-1].loc['Channel_Name']

        x_pts = self.FCS.data.iloc[:, x-1]
        y_pts = self.FCS.data.iloc[:, y-1]
        indicies = np.random.choice(x_pts.index, int(downsample*len(x_pts)))

        plt.plot(x_pts[indicies], y_pts[indicies], 'b.', markersize=1, alpha=0.5)
        plt.xlabel(x_lb)
        plt.ylabel(y_lb)
        plt.xlim(0, 1)
        plt.ylim(0, 1)
        plt.xticks([])
        plt.yticks([])

        plt.gca().set_aspect('equal', adjustable='box')


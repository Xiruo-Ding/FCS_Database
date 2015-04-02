import glob
from os.path import splitext, split, join


def itermodules(subcommands_path, root=__name__):

    commands = [x for x in [splitext(split(p)[1])[0]
                            for p in glob.glob(join(subcommands_path, '*.py'))]
                if not x.startswith('_')]

    for command in commands:
        yield command, __import__('%s.%s' % (root, command), fromlist=[command])


def add_filter_args(parser):
    """ Adds the query filter arguments to parser """

    parser.add_argument('-tubes', '--tubes', help='List of tube types to select',
                        nargs='+', action='store',
                        default=None, type=str)
    parser.add_argument('-antigens', '--antigens', help='List of antigens to select',
                        nargs='+', action='store',
                        default=None, type=str)
    parser.add_argument('-Channel_Name', '--Channel-Name',
                        help='List of Channel_Name\'s to select',
                        nargs='+', action='store',
                        default=None, type=str)
    parser.add_argument('-Channel_Number', '--Channel-Number',
                        help='List of Channel_Number\'s to select',
                        nargs='+', action='store',
                        default=None, type=int)
    parser.add_argument('-dates', '--daterange',
                        help='Start and end dates to bound selection of cases \
                        [Year-Month-Date Year-Month-Date]',
                        nargs=2, action='store', type=str)
    parser.add_argument('-cases', '--cases', help='List of cases to select',
                        nargs='+', action='store',
                        default=None, type=str)
    parser.add_argument('-specimens', '--specimens', help='List of specimen types to select',
                        nargs='+', action='store',
                        default=None, type=str)
    parser.add_argument('-cytnum', '--cytnum',
                        help='List of cytnums (cytometer numbers) to include',
                        nargs='+', action='store',
                        default=None, type=str)
    parser.add_argument('-case_tube_idxs', '--case_tube_idxs',
                        help='List of case_tube_idxs to select',
                        nargs='+', action='store',
                        default=None, type=str)
    parser.add_argument('-rand', '--random-order',
                        dest='random_order',
                        help='Return database results in random order',
                        default=False,
                        action='store_true')
    parser.add_argument('--date-order',
                        dest='date_order',
                        help='Return database results in date order',
                        default=False,
                        action='store_true')
    parser.add_argument('--limit', '--record-n',
                        dest='record_n',
                        help='Number of records for database to return',
                        default=None, type=int)
    parser.add_argument('--total_events', '--total-events', dest='total_events',
                        help='Minimum event count to accept',
                        default=None, type=int)


def add_process_args(parser):
    """ Adds the FCS file arguments to parser """
    parser.add_argument('--comp_flag', '--comp-flag',
                        help='Comp Mode',
                        default='table',
                        choices=['table', 'none'],
                        type=str)
    parser.add_argument('--singlet_flag', '--singlet-flag',
                        help='Singlet gate mode',
                        default='none',
                        choices=['fixed', 'auto', 'none'],
                        type=str)
    parser.add_argument('--viable_flag', '--viability-flag',
                        help='Viablity gate mode',
                        default='none',
                        choices=['fixed', 'auto', 'none'],
                        type=str)
    parser.add_argument('--gates1d', default=[], nargs='+',
                        action='store', help='1D gating (list)',
                        type=str)

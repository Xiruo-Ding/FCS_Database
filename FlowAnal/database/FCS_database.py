""" Class for FCS database """

import logging
import pandas as pd
from sqlalchemy import inspect
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from hsqr.database.database import SqliteConnection
from hsqr.lab_pred import Lab_pred_table

from query_database import queryDB
from FlowAnal.__init__ import package_data
from FlowAnal.database.FCS_declarative import *
from FlowAnal.FCS import FCS

log = logging.getLogger(__name__)


class FCSdatabase(SqliteConnection):
    """ Object interface for Flow cytometry database

    Provides an object for FCS database, inheriting from general
    SqliteConnection
    """

    def __init__(self, db, interrupt=5, rebuild=False, build='alchemy'):
        log.debug('initializing FCSdatabase')
        self.tables = ['PmtTubeCases', 'TubeCases', 'Cases', 'TubeTypesInstances',
                       'Antigens', 'Fluorophores', 'MetaTable']
        super(FCSdatabase, self).__init__(db=db, tables=self.tables, build=build)

        if build == 'sql' and rebuild is True:
            self.create()
        elif build == 'alchemy':
            self.create_alchem(rebuild=rebuild)

    def create_alchem(self, rebuild=False):
        """ Drop and recreate FCS database from sqlalchemy statements """

        Base.metadata.bind = self.engine
        self.Session = sessionmaker(bind=self.engine)

        if rebuild is True:
            log.info("Dropping existing data in DB [%s]" % self.db_file)
            Base.metadata.drop_all()
            Base.metadata.create_all()

            # Add creation datetime
            s = self.Session()
            m = MetaTable(creation_date=datetime.now())
            s.add(m)
            s.commit()
            s.close()
        else:
            Base.metadata.create_all()

        if self.enforce_foreign_keys:
            self.enforce_foreign_keys()
        self.meta = Base.metadata
        self.insp = inspect(self.engine)

        self.engine.conn = self.engine.connect()
        if rebuild is True:
            self.engine.conn.execute("ANALYZE")

        # Capture datetime
        self.creation_date = queryDB(self, getCreationDate=True).results

    def create(self, files=['setup_hpmeta.sql']):
        """ Drop and recreate FCS database from <files> """
        self.drop_all()
        for file in files:
            self.run_sql_file(file, dir='FlowAnal/database/sqlite')
        self.engine.conn.execute("ANALYZE")

    def query(self, out_file=None, exporttype='dict_dict', **kwargs):
        """ Query database and return results according to <exporttype>

        Keyword arguments:
        exporttype -- ['dict_dict', 'df']
        outfile -- file to write out a pandas dataframe

        Optional arguments:
        getfiles -- Use queryDB.getfiles() to find files based on criteria
        tubes -- <list> Select set based on tube types
        daterange -- <list> [X,X] Select set based on date between daterange
        """
        if out_file:
            q = queryDB(self, exporttype='df', **kwargs)
            log.info('Printing out df to %s', out_file)
            q.results.to_csv(out_file, index=False, index_label=None, encoding='utf-8')
            return 0
        else:
            return queryDB(self, exporttype=exporttype, **kwargs)

    def exportTubeTypes(self, **kwargs):
        """ Export TubeTypesInstances to csv (for review) """

        a = self.sql2pd(table='TubeTypesInstances')

        out_file = 'FlowAnal/data/tube_types.tmp'
        if kwargs['file'] is not None:
            out_file = kwargs['file']

        try:
            a.to_csv(out_file, index=False)
            log.info('Exported TubeTypesInstances to data/tube_types.tmp')
        except:
            raise 'Failed to export'

    def importTubeTypes(self, **kwargs):
        """
        Import TubeTypesInstances from csv and overwrite existing TubeTypeInstances
        and TubeTypes tables in db
        """

        # Load csv file
        in_file = package_data(fname='tube_types.csv')
        if kwargs['file'] is not None:
            in_file = kwargs['file']
        a = pd.read_csv(in_file)

        # Replace tubeTypes
        s = self.Session()
        self.meta.tables['TubeTypes'].delete()
        print "WARNING: deletion of TubeTypes not working currently (TODO)"
        s.close()
        tube_types = list(a.tube_type.unique())
        self.add_list(tube_types, 'TubeTypes')

        # Replace TubeTypesInstances
        s = self.Session()
        self.meta.tables['TubeTypesInstances'].delete()
        s.close()
        self.add_df(df=a, table='TubeTypesInstances')

    def removeCases(self, df=None, ll=None):
        """ Method to remove a set of cases from the database based on a dataframe (or list of lists)

        df --
        ll -- list of [case, case_tube_idx, error_message]
        """

        if ll is not None:
            a = pd.DataFrame.from_records(data=ll)
        elif df is not None:
            a = df
        else:
            raise ValueError('No cases specified to remove, must provide df or ll')

        print a
        quit()

    def addCustomCaseData(self, file, whittle=True):
        """ Method to load file (tab-text) into database table CustomCaseData

        This must include <case_number> and <category> columns
        Note: this will overwrite existing data
        """

        a = Lab_pred_table(db=self, file=file)

        # ### Handle column names ###
        a.dat.columns = [c.lower() for c in a.dat.columns.values]
        a_cols = a.dat.columns.tolist()

        # Convert 'CASE*' => 'case_number'
        case_index = next((index for index, value in enumerate(a_cols)
                           if value[:4] == 'case'), None)
        if case_index is not None:
            a_cols[case_index] = 'case_number'

        db_cols = CustomCaseData.__mapper__.columns.keys()
        cols = [c for c in a_cols if c.lower() in db_cols]

        # Add second column if only captured 1 column and rename to <category>
        if (len(db_cols) > 1) and (len(cols) == 1):
            cols.append(db_cols[1])
            a_cols[1] = cols[1]

        a.dat.columns = a_cols

        # ### If one of columns matches use it ###
        if (len(cols) > 0):
            log.info('Adding file %s to db %s' % (file, self.db_file))

            a.dat = a.dat[cols]

            # Identify cases in custom data but not in meta db
            db_case_list = zip(*queryDB(self, getCases=True, not_flagged=False).results)[0]
            cases_missing_in_db = a.dat.case_number.loc[~a.dat.case_number.isin(db_case_list)].\
                               tolist()

            # Write custom data
            a.dat.to_sql('CustomCaseData', con=self.engine,
                         if_exists='replace', index=False)

            # Add empty FCS objects to db for each in cases_to_exclude
            for c in cases_missing_in_db:
                log.info('Making empty FCS for {}'.format(c))
                fFCS = FCS(case_number=c,
                           flag='CustomData_ONLY',
                           error_message='Added to db because in custom list but not in metadb')
                fFCS.meta_to_db(db=self, add_lists=True)
        else:
            raise ValueError("File %s does not have columns 'case_number' and 'category'" % (file))

    def set_flag(self, case_tube_idx, flag, error_message):

        s = self.Session()

        TubeCase_i = s.query(TubeCases).\
                     filter(TubeCases.case_tube_idx == case_tube_idx).\
                     one()
        TubeCase_i.flag = flag
        TubeCase_i.error_message = error_message
        s.commit()
        log.info('Set case_tube_idx #{} to flag [{}]'.format(case_tube_idx, flag))

        s.close()


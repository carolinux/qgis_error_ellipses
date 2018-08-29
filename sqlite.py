from pyspatialite import dbapi2 as sqlite3

import os


def get_geometry_wildcards(geom_columns):
    if not geom_columns:
        return []
    else:
        return map(lambda col_info: 'GeomFromText(?,  {})'.format(col_info[2]), geom_columns)         


def df_to_sqlite(dataframe, db_name, tbl_name, index_col=None, geom_columns=None):
    """ Saves a dataframe as an sqlite database with an optional index"""

    if os.path.exists(db_name):
        os.remove(db_name)
 
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()                                 
 
    cur.execute("drop table if exists {}".format(tbl_name))

    if geom_columns:
        geom_column_names = map(lambda x: x[0], geom_columns)
        non_geom_columns = filter(lambda x: x not in geom_column_names, dataframe.columns)
    else:
        geom_column_names = []
        non_geom_columns = dataframe.columns

    wildcards = ','.join(['?'] * len(non_geom_columns) + get_geometry_wildcards(geom_columns))              
    data = [tuple(x) for x in dataframe[non_geom_columns+geom_column_names].values]
 
    col_str = '"' + '","'.join(non_geom_columns) + '"'
    cur.execute("create table {} ({})".format(tbl_name, col_str))
    if geom_columns:
        print ("Initializing metadata tables")
        # this initializes spatial metadata tables (necessary for addgeometrycolumn to work)
        cur.execute("SELECT InitSpatialMetaData(1)")
        for col,col_type,srid in geom_columns:
            print("Adding geometry column {}".format(col))
            cur.execute("SELECT AddGeometryColumn('{}', '{}', {}, '{}', 'XY')".format(tbl_name, col, srid, col_type))
 
    print("Inserting values")
    print wildcards
    cur.executemany("insert into {} values({})".format(tbl_name, wildcards), data)

    if index_col:
        print("Creating index")
        cur.execute("CREATE UNIQUE INDEX `idx_UNIQUE` ON `{}` (`{}` ASC)".format(tbl_name, index_col))
 
    conn.commit()
    conn.close()

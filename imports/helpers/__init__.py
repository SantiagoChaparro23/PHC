from django.db import connection

def get_urls_metrics(tables_with_column:str = None, more_recent:bool = False, year = None, cursor = None):
    """Summary

    Get urls from files from metrics, some filters can be applied
    
    Args:
        tables_with_column (str, optional): Get urls of metrics files containing 'tables_with_column' in their tables.
        more_recent (bool, optional): Get more recent url from every metric
        year (int or str, optional): Get only urls from a specific year
        cursor (CursorDebugWrapper, optional): Django cursor, if not entered, one is initialized
    
    Returns:
        list of tuples: Every tuple have the next info:
            url_file, year_file, period, metric_id, format, name_table
    """
    
    if cursor is None:
        cursor = connection.cursor()
    else:
        pass


    sql_str = ''
    add_str_end = ''

    # Assemble string in function of parameters
    #   For more_recent
    if more_recent:

        sql_str += '''
            SELECT DISTINCT ON (metric_id) url_file, year_file, period, metric_id, format, name_table, imports_urlsfilesmetric.id as id_metric
            FROM imports_urlsfilesmetric

            INNER JOIN imports_metric
            ON imports_urlsfilesmetric.metric_id = imports_metric.id            
        '''

        add_str_end += '''
            ORDER BY metric_id, year_file DESC, period DESC
        '''

    else:
        sql_str += '''
            SELECT url_file, year_file, period, metric_id, format, name_table, records_periodicity, imports_urlsfilesmetric.id as id_metric
            FROM imports_urlsfilesmetric

            INNER JOIN imports_metric
            ON imports_urlsfilesmetric.metric_id = imports_metric.id            
        '''

    #   for tables_with_column
    if tables_with_column is not None:

        sql_str += f'''
            RIGHT OUTER JOIN (
                    -- Get ids of metrics with resource_id in his table
                    SELECT id FROM imports_metric
                    RIGHT OUTER JOIN (
                                      -- Get name of tables with resource_id
                                      SELECT table_name FROM information_schema.columns
                                      WHERE column_name = '{tables_with_column}') AS info_tab_name
                    ON name_table = info_tab_name.table_name
                ) AS id_tabs_metric
            ON imports_urlsfilesmetric.metric_id = id_tabs_metric.id
        '''

    else:
        pass

    #   for year
    if year is not None:

        sql_str += f'''
            WHERE year_file={year}
        '''

    else:
        pass

    # Execute code and return results
    cursor.execute(sql_str + add_str_end)

    return cursor.fetchall()




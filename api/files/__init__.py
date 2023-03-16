

generalize_query_code ="""
DROP FUNCTION IF EXISTS time_series_generalized_query;

CREATE OR REPLACE FUNCTION time_series_generalized_query(id_component integer, periodicity integer, resample_method text, 
                                                         start_date date, end_date date,
                                                         id_direct_filters integer[], str_indirect_filters text[])
/*
    Generalize function for time series from mec, can select component from a metric, resample to wished periodicity
    and use 2 types of filters, by ids of elements in the table or strings from related features to the elements from the table

        args:
            id_component: numeric id of component of metric to query, this id must exist in imports_component table
            periodicity: integer that represent a periodicity, avalaible periodicitys are:
                            1, decade,      2, year,        3, quarter,
                            4, month,       5, week,        6, day,
                            7, hour
                            
            resample_method: name function to use in resampling phase, where gonna group records with a same date.
                             this string function can be:
                                                sum,    min,    max,    avg,    other with similar behavior
                                                
            id_direct_filters: array of ids from elements in the table, every component represent a type of filter,
                               if you not gonna use a filter, use -1 integer instead in that component.
                               Each component of array mean the next:
                                    0 : agent_id            1 : ciiu_id
                                    2 : fuel_id             3 : hydrological_region_id
                                    4 : market_id           5 : river_id
                                    6 : subactivity_id                      

            str_indirect_filters: array of strings with values to use in filters, this indirect filters are from
                                  features of elements as shipping_type for resources or activity for agents.
                                  if you not gonna use a filter, use 'NULL' text instead in that component.
                                  Each component of array mean the next:
                                    0 : detail, agent field             1 : activity, agent field
                                    2 : name, resource field            3 : generation_type, resource field
                                    4 : shipping_type, resource field
                                  

*/
RETURNS TABLE(-- Time serie
              dts timestamp[], 
              vls float8[],
    
              -- Extra data
              unt text,
              average float8,
              median float8,
              maximum float8,
              minimum float8,
              percentile_05 float8,
              percentile_95 float8,
              standard_deviation float8      
             ) AS $$

    DECLARE
        -- For querys and steps in data processing
        --      data about component and his metric
        name_tbl text;
        name_col text;
        rcrds_periodicity integer;
        sql_periodicity text;
        
        --      for iterate
        dte date;
        val float8;
        recrd record;
        col_name text;
        i integer;
        hr text;
        txt text;
        rw text[];
        
        --      constant arrays or related
        data_indirect_filters text[][] := array[['1', 'INNER JOIN imports_agent ON %s.agent_id = imports_agent.id', 'imports_agent.detail'],
                                                ['2', 'INNER JOIN imports_agent ON %s.agent_id = imports_agent.id', 'imports_agent.activity'],
                                                ['3', 'INNER JOIN imports_resource ON %s.resource_id = imports_resource.id', 'imports_resource.name'],
                                                ['4', 'INNER JOIN imports_resource ON %s.resource_id = imports_resource.id', 'imports_resource.generation_type'],
                                                ['5', 'INNER JOIN imports_resource ON %s.resource_id = imports_resource.id', 'imports_resource.shipping_type']];
                                              
        direct_filters_pairs text[][] := array[['1', 'agent_id'], ['2', 'ciiu_id'], ['3', 'fuel_id'], ['4', 'hydrological_region_id'], 
                                               ['5', 'market_id'], ['6', 'river_id'], ['7', 'subactivity_id']];
                                               
        periodicitys_pairs text[][] := array[['1', 'decade'], ['2', 'year'], ['3', 'quarter'], ['4', 'month'], ['5', 'week'], ['6', 'day'], ['7', 'hour']];
        
        str_sum_hours_cols text := 'hour_0 + hour_1 + hour_2 + hour_3 + hour_4 + hour_5 + hour_6 + hour_7 + hour_8 + hour_9 + hour_10 + hour_11 + hour_12 + hour_13 + hour_14 + hour_15 + hour_16 + hour_17 + hour_18 + hour_19 + hour_20 + hour_21 + hour_22 + hour_23';
        
        enum_hours_cols text[][] := array[['0', 'hour_0'], ['1', 'hour_1'], ['2', 'hour_2'], ['3', 'hour_3'], ['4', 'hour_4'], ['5', 'hour_5'], 
                                          ['6', 'hour_6'], ['7', 'hour_7'], ['8', 'hour_8'], ['9', 'hour_9'], ['10', 'hour_10'], ['11', 'hour_11'], 
                                          ['12', 'hour_12'], ['13', 'hour_13'], ['14', 'hour_14'], ['15', 'hour_15'], ['16', 'hour_16'], ['17', 'hour_17'], 
                                          ['18', 'hour_18'], ['19', 'hour_19'], ['20', 'hour_20'], ['21', 'hour_21'], ['22', 'hour_22'], ['23', 'hour_23']];
       

        -- about sql code
        sql_final_query text;
        sql_code_where text;
        sql_code_joins text;
        where_added bool;
        
        -- for histogram
        max_val float8;
        min_val float8;
        
        -- To return
        unt text;
        compnent text;

        -- var of develop
        var_x integer;
        var_f float8;
        dta record; 

    BEGIN
        -- Get info of component and metric
        SELECT component, unit, name_table, name_column, records_periodicity
        INTO compnent, unt, name_tbl, name_col, rcrds_periodicity
        FROM imports_component
        INNER JOIN imports_metric
        ON imports_component.metric_id = imports_metric.id
        WHERE imports_component.id = id_component;
        
        ---------------------------------------------------------------------------------------------------------
        -- Validate arguments -----------------------------------------------------------------------------------
        ---------------------------------------------------------------------------------------------------------       
        /* Validate periodicity from argument and table to query
            If for example:
                periodicity='hour'=7, rcrds_periodicity='day'=6
                
                then raise exception, the min periodicity for query that
                records is 'day'
        */
        IF rcrds_periodicity < periodicity THEN
            RAISE EXCEPTION 'Periodicity of component records: %, Wish periodicity: %', rcrds_periodicity, periodicity
                  USING HINT = 'Wish periodicity must be equal or grower that periodicity of component records';
        END IF;
        
        -- If periodicity are ok, get sql equivalen for periodicty, we gonna use for query forward      
        FOREACH rw SLICE 1 IN ARRAY periodicitys_pairs
        LOOP
            IF rw[1] = periodicity::text THEN
                sql_periodicity = rw[2];
            END IF;         
        END LOOP;
        
        ---------------------------------------------------------------------------------------------------------
        -- Build where filters ----------------------------------------------------------------------------------
        ---------------------------------------------------------------------------------------------------------
        /* 
           Take all from id_direct_filters and str_indirect_filters arrays

           id_direct_filters       
               Each component of id_direct_filters array is a id, the order is the next:
               a value of -1 means that not gonna use this filter
                    direct_filters 
                        0 : id_agent
                        1 : id_ciiu
                        2 : id_fuel
                        3 : id_hidrologic_region
                        4 : id_market
                        5 : id_river
                        6 : id_sub_activity
                name resource is not here due to a resource can have some different versions, so the name of resource
                not is unique in the resources table.
                        
            str_indirect_filters
               Each component of str_indirect_filters array is a text to use in a where clause, the order is the next:
               a value of NULL means that not gonna use this filter
                    direct_filters 
                        0 : detail, agent field
                        1 : activity, agent field
                        2 : name, resource field
                        3 : generation_type, resource field
                        4 : shipping_type, resource field
        */
        sql_code_where := ''; -- String to save all the where sentences to use in final query
        where_added := False; -- Indicate if the 'where' clause was used, in that case we gonna use 'and' instead
        
        --------------------------------------------------------------
        -- Add direct filters, dont require joins --------------------
        --------------------------------------------------------------
        FOREACH rw SLICE 1 IN ARRAY direct_filters_pairs
        LOOP
        
            -- Take integer for index corresponding component in id_direct_filters
            i := CAST(rw[1] AS INTEGER);
            
            -- If is != -1 then this is a id for use in filtering
            IF id_direct_filters[i] != -1  THEN
            
                -- This col name must be in the table to query, this is ie. id_fuel, id_sub_activity, etc
                col_name := rw[2];
                
                -- Add Where clause or And
                IF NOT where_added THEN
                
                    sql_code_where := sql_code_where || FORMAT('WHERE %I.%I = %s
                    ', name_tbl, col_name, CAST(id_direct_filters[i] AS TEXT));

                    where_added := True;
                
                ELSE
                    sql_code_where := sql_code_where || FORMAT('AND %I.%I = %s
                    ', name_tbl, col_name, CAST(id_direct_filters[i] AS TEXT));    
                
                END IF;
                
            END IF;

        END LOOP;
        
        --------------------------------------------------------------
        -- Add indirect filters, require joins -----------------------
        --------------------------------------------------------------
                
        -- Create a temporal table to keep used filters and strings for each one 
        DROP TABLE IF EXISTS indirect_filters_to_use;
        CREATE TEMP TABLE indirect_filters_to_use (
            index_arr INTEGER,
            join_sql TEXT,
            where_sql TEXT
        );

        -- Add to indirect_filters_to_use data of filters to use
        FOR i IN SELECT * FROM generate_series(1, array_length(str_indirect_filters, 1)+1)
        LOOP
        
            -- If is != 'NULL' then this is a feature to use in filtering
            IF str_indirect_filters[i] != 'NULL' THEN   
            
                INSERT INTO indirect_filters_to_use(index_arr, join_sql, where_sql)
                VALUES (CAST(data_indirect_filters[i][1] AS INTEGER), 
                        data_indirect_filters[i][2], 
                        data_indirect_filters[i][3]);
            END IF;

        END LOOP;
        
        -- Assemble final string
        --      Add joins
        sql_code_joins := '';
        FOR txt IN SELECT DISTINCT join_sql FROM indirect_filters_to_use
        LOOP
            sql_code_joins := sql_code_joins || FORMAT(txt, name_tbl) || ' ';
        END LOOP;
        

        --      Add where's
        FOR i, txt IN SELECT index_arr, where_sql FROM indirect_filters_to_use
        LOOP

            -- Add Where clause or And
            IF NOT where_added THEN

                sql_code_where := sql_code_where || FORMAT('WHERE %s = ''%s''
                ', txt, str_indirect_filters[i]);

                where_added := True;

            ELSE
                sql_code_where := sql_code_where || FORMAT('AND %s = ''%s''
                ', txt, str_indirect_filters[i]);      

            END IF;         

        END LOOP;
        
        -- Add date filters
        IF NOT where_added THEN

            sql_code_where := sql_code_where || FORMAT('WHERE date BETWEEN ''%s'' AND ''%s''
            ', start_date, end_date);

            where_added := True;

        ELSE
            sql_code_where := sql_code_where || FORMAT('AND date BETWEEN ''%s'' AND ''%s''
            ', start_date, end_date);

        END IF;

    
        

        ---------------------------------------------------------------------------------------------------------
        -- Get time serie of component, query with filters ------------------------------------------------------
        ---------------------------------------------------------------------------------------------------------

        -- Create a temporal table to keep dates and values from time serie
        DROP TABLE IF EXISTS tranpose_time_serie;
        CREATE TEMP TABLE tranpose_time_serie (
            dates timestamp,
            vals float8
        );  
        
        -- Query case depends on the component metric structure and periodicity
        CASE
        
            -- For components with format 0-24 where all table is a component, ----------
            -- by default his periodicity is 'hourly'                          ----------
            -- If wish periodicity is 'hourly' do not resample, but 'tranpose' data -------             
            -- TRANSPOSE: We are call tranpose to process from join all columns from all hours in only one column
            --            so we have as result 2 columns, one for datetimes and other for values<
            WHEN name_col = 'all' THEN 
                RAISE NOTICE 'HOURLY tranpose';

                -- Create temporal table to save all tranpose data, before we sort this and save in another table
                DROP TABLE IF EXISTS unsorted_tranpose_time_serie;
                CREATE TEMP TABLE unsorted_tranpose_time_serie (
                    ds timestamp,
                    vs float8
                );              
                

                -- Insert tranpose rows in table tranpose_time_serie, here we apply filters
                FOREACH rw SLICE 1 IN ARRAY enum_hours_cols
                LOOP                   
                    
                    sql_final_query := FORMAT('
                        INSERT INTO unsorted_tranpose_time_serie (ds, vs)
                        SELECT CAST(date::text||'' ''||%s||'':00:00'' AS TIMESTAMP) as dates , %I(%I)
                        FROM %I
                        %s
                        %s
                        GROUP BY dates
                        ', rw[1], resample_method, rw[2], name_tbl, sql_code_joins, sql_code_where);

                    EXECUTE sql_final_query;
                    

                END LOOP;
                

                -- This table 
                DROP TABLE IF EXISTS middle_tranpose_time_serie;
                CREATE TEMP TABLE middle_tranpose_time_serie (
                    dates_m timestamp,
                    vals_m float8
                );
                
                --  Query again for sort all dates
                INSERT INTO middle_tranpose_time_serie (dates_m, vals_m)
                SELECT ds, vs 
                FROM unsorted_tranpose_time_serie
                ORDER BY ds;                
                
                
                -- The data is ready in this point if user wish sql_periodicity = 'hour'
                -- So... only pass data from 'middle_tranpose_time_serie' to 'tranpose_time_serie'
                -- where 'tranpose_time_serie' is the table to return
                IF sql_periodicity = 'hour' THEN
                    -- Do nothing
                    RAISE NOTICE 'HOURLY, not resample';
                    
                    --  Query again for sort all dates
                    INSERT INTO tranpose_time_serie (dates, vals)
                    SELECT dates_m, vals_m
                    FROM middle_tranpose_time_serie
                    ORDER BY dates_m;                       
                
                -- The data require resample process
                -- in this resample process we are resampling all values for each day
                -- and all values from all days for each period 'sql_periodicity' (month, year, etc)
                ELSE    
                    RAISE NOTICE 'NOT HOURLY, resample';
                    
                    sql_final_query := FORMAT('
                       INSERT INTO tranpose_time_serie (dates, vals)
                       SELECT DATE_TRUNC(''%I'', dates_m::timestamp) as dates, %I(vals_m)
                       FROM middle_tranpose_time_serie
                       GROUP BY dates
                       ORDER BY dates                          
                       ', sql_periodicity, resample_method, sql_periodicity);

                    --  RAISE NOTICE '(%)', sql_final_query;

                    EXECUTE sql_final_query;                    
                
                END IF;

                
            -----------------------------------------------------------------------------
            -- For components that only have a column -----------------------------------
            -- dont need additional steps, only query -----------------------------------           
            ELSE 
            
                RAISE NOTICE 'NOT HOURLY';

                sql_final_query :=  FORMAT('
                   INSERT INTO tranpose_time_serie (dates, vals)
                   SELECT DATE_TRUNC(''%I'', date::timestamp) as dates, %I(%I)
                   FROM %I
                   %s
                   %s
                   GROUP BY dates
                   ORDER BY dates
                   ',sql_periodicity, resample_method, name_col, name_tbl, sql_code_joins, sql_code_where);
                   
                EXECUTE sql_final_query;

            END CASE;
            
            
        ---------------------------------------------------------------------------------------------------------
        -- Calculate extra elements and return table results ----------------------------------------------------
        ---------------------------------------------------------------------------------------------------------

        -- Calculate final elements and return            
        RETURN QUERY 
            SELECT -- Time serie
                   ARRAY(SELECT dates FROM tranpose_time_serie), 
                   ARRAY(SELECT vals FROM tranpose_time_serie),
                   
                   -- Extra data
                   unt,
                   (SELECT AVG(tranpose_time_serie.vals) FROM tranpose_time_serie),
                   (SELECT PERCENTILE_DISC(0.5) WITHIN GROUP (ORDER BY tranpose_time_serie.vals) FROM tranpose_time_serie),
                   (SELECT max(tranpose_time_serie.vals) FROM tranpose_time_serie),
                   (SELECT min(tranpose_time_serie.vals) FROM tranpose_time_serie),
                   (SELECT PERCENTILE_DISC(0.05) WITHIN GROUP (ORDER BY tranpose_time_serie.vals) FROM tranpose_time_serie),
                   (SELECT PERCENTILE_DISC(0.95) WITHIN GROUP (ORDER BY tranpose_time_serie.vals) FROM tranpose_time_serie),
                   (SELECT stddev_samp(tranpose_time_serie.vals) FROM tranpose_time_serie);

    END;
$$ 
LANGUAGE plpgsql;

SELECT * from time_series_generalized_query({}, {}, '{}', '{}', '{}', ARRAY{}, ARRAY{});


"""
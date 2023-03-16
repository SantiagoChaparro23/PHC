import psycopg2
import pandas as pd
import numpy as np
class sddp_case:
    def __init__(self, project_id):
        self.project_id = project_id
        self.db_connection = psycopg2.connect(host='127.0.0.1',
            port = "5432",
            user='postgres',
            password = 'postgres',
            database = "desarrollo")
        sql_query = """SELECT * FROM configuration_sddp_project WHERE id = {} ORDER BY id ASC """.format(project_id)
        pandas_query = pd.read_sql_query(sql_query, self.db_connection)
        project_data = pd.DataFrame(pandas_query)
        self.name = project_data['name'][0]
        self.description = project_data['description'][0]
        self.year_init_optimization = int(project_data['year_init_optimization'][0])
        self.year_end_optimization = int(project_data['year_end_optimization'][0])
        self.periodicity_auction = project_data['periodicity_auction'][0]
        self.regasification_init = project_data['regasification_init'][0]
        self.status = project_data['status'][0]
        self.file = project_data['file'][0]
        self.created_by = project_data['create_by_id'][0]
        self.file = project_data['file'][0]
        self.fuel_price_option = project_data['fuel_price_option_id'][0]
        self.growing_rate_id = project_data['growing_rate_id'][0]

    def calculate_max_new_capacity_table(self):
        sql_query = """ SELECT * FROM configuration_sddp_maxnewcapacity WHERE project_id = {} ORDER BY year ASC """.format(self.project_id)
        pandas_query = pd.read_sql_query(sql_query, self.db_connection)
        initial_max_new_capacity = pd.DataFrame(pandas_query)
        initial_max_new_capacity = initial_max_new_capacity.drop(columns='project_id')
        initial_max_new_capacity = initial_max_new_capacity.drop(columns='id')
        storage_data_frame = pd.DataFrame()
        for year in range(self.year_init_optimization, self.year_end_optimization):
            filtered_data = initial_max_new_capacity.where(initial_max_new_capacity["year"] > year).dropna()
            filtered_data = filtered_data.iloc[[0]]
            filtered_data['year'] = year
            storage_data_frame = pd.concat([storage_data_frame, filtered_data])
        storage_data_frame.reset_index(inplace= True, drop=True)
        self.calculated_max_new_capacity = storage_data_frame

    def calculate_meta_matrix_table(self):
        sql_query =  """ SELECT * FROM configuration_sddp_maxnewcapacity WHERE project_id = {} ORDER BY year ASC """.format(self.project_id)
        pandas_query = pd.read_sql_query(sql_query, self.db_connection)
        initial_meta_matrix = pd.DataFrame(pandas_query)
        initial_meta_matrix = initial_meta_matrix.iloc[1:]
        poly_regresion = {}
        result_dataframe = pd.DataFrame()
        for tech in initial_meta_matrix.columns[2:]:
            poly_regresion[tech] = np.polyfit(initial_meta_matrix["year"].values, initial_meta_matrix[tech].values, 3)
        result_dataframe['year'] = pd.Series(list(range(self.year_init_optimization,self.year_end_optimization)))
        for tech in initial_meta_matrix.columns[2:]:
            result_dataframe[tech] = pd.Series(
                np.polyval(poly_regresion[tech],
                list(range(self.year_init_optimization,self.year_end_optimization))))
        self.calculated_meta_matix = result_dataframe

    def calculate_LCOE_table(self):
        sql_query =  """ SELECT * FROM configuration_sddp_lcoeenergycost WHERE project_id = {} ORDER BY year ASC """.format(self.project_id)
        pandas_query = pd.read_sql_query(sql_query, self.db_connection)
        initial_lcoe = pd.DataFrame(pandas_query)
        poly_regresion = {}
        result_dataframe = pd.DataFrame()
        for tech in initial_lcoe.columns[2:]:
            poly_regresion[tech] = np.polyfit(initial_lcoe["year"].values, initial_lcoe[tech].values, 1)
        result_dataframe['year'] = pd.Series(list(range(self.year_init_optimization,self.year_end_optimization)))
        for tech in initial_lcoe.columns[2:]:
            result_dataframe[tech] = pd.Series(
                np.polyval(poly_regresion[tech],
                list(range(self.year_init_optimization,self.year_end_optimization))))
        self.calculated_lcoe = result_dataframe

    def calculate_date_plants(self):
        #name, reliability_obligation, long_term_contract, start_at
        sql_query =  """ 
        SELECT configuration_sddp_futureplants.name, reliability_obligation, long_term_contract, start_at, configuration_sddp_planttype.name AS tecno FROM configuration_sddp_futureplants   
        INNER JOIN configuration_sddp_planttype  ON configuration_sddp_futureplants.plant_type_id = configuration_sddp_planttype.id
        WHERE project_id = {} """.format(self.project_id)
        
        pandas_query = pd.read_sql_query(sql_query, self.db_connection)
        future_plants = pd.DataFrame(pandas_query)
        future_plants_result_dict = {'Nombre planta': [], 'fecha': [], 'Tipo': [], 'Asignacion': [], 'Archivo': []}
        for index, data in future_plants.iterrows():
            if not np.isnan(data['reliability_obligation']):
                future_plants_result_dict['Nombre planta'].append(data['name'])
                future_plants_result_dict['fecha'].append(data['start_at'].strftime("%d/%m/%Y"))
                future_plants_result_dict['Tipo'].append(data['tecno'])
                future_plants_result_dict['Asignacion'].append('CxC')
                future_plants_result_dict['Archivo'].append(data['tecno'])
            elif not np.isnan(data['long_term_contract']):
                future_plants_result_dict['Nombre planta'].append(data['name'])
                future_plants_result_dict['fecha'].append(data['start_at'].strftime("%d/%m/%Y"))
                future_plants_result_dict['Tipo'].append(data['tecno'])
                future_plants_result_dict['Asignacion'].append('CLP')
                future_plants_result_dict['Archivo'].append(data['tecno'])
        self.future_plantas_entry_table = pd.DataFrame.from_dict(future_plants_result_dict)

    def calculate_initialization_data(self):
        sql_query =  """ SELECT * FROM configuration_sddp_planttype"""
        pandas_query = pd.read_sql_query(sql_query, self.db_connection)
        plant_type_dataframe = pd.DataFrame(pandas_query)

        sql_query =  """ SELECT * FROM configuration_sddp_existingplants WHERE project_id = {} """"".format(self.project_id)
        pandas_query = pd.read_sql_query(sql_query, self.db_connection)
        existing_plants_data_frame = pd.DataFrame(pandas_query)
        aux_result = []
        for index, data in plant_type_dataframe.iterrows():
            aux_result.append(existing_plants_data_frame['nominal_power'].where(
                existing_plants_data_frame['plant_type_id'] == data['id']).dropna().sum())
        plant_type_dataframe['initial_cap'] = aux_result
        print(plant_type_dataframe)
        self.initial_capacity = plant_type_dataframe

    def calculate_demand_vs_enficc_table(self):
        #Not complete

        sql_query =  """ SELECT * FROM configuration_sddp_planttype"""
        pandas_query = pd.read_sql_query(sql_query, self.db_connection)
        plant_type_dataframe = pd.DataFrame(pandas_query)

        sql_query =  """ SELECT * FROM configuration_sddp_additionalcapacity"""
        pandas_query = pd.read_sql_query(sql_query, self.db_connection)
        additional_capacity_dataframe = pd.DataFrame(pandas_query)

        sql_query =  """ SELECT * FROM configuration_sddp_futureplants"""
        pandas_query = pd.read_sql_query(sql_query, self.db_connection)
        future_plants_dataframe = pd.DataFrame(pandas_query)
        future_plants_dataframe.fillna(0, inplace=True)

        sql_query =  """ SELECT * FROM configuration_sddp_existingplants"""
        pandas_query = pd.read_sql_query(sql_query, self.db_connection)
        existing_plants_dataframe = pd.DataFrame(pandas_query)
        existing_plants_dataframe.fillna(0, inplace= True)

        sql_query =  """ SELECT * FROM configuration_sddp_demand"""
        pandas_query = pd.read_sql_query(sql_query, self.db_connection)
        demand_dataframe = pd.DataFrame(pandas_query)

        aux_result = []
        init_value = existing_plants_dataframe['reliability_obligation'].sum() + existing_plants_dataframe['long_term_contract'].sum()
        for index, data in demand_dataframe.iterrows():
            aux = init_value
            filtered_future_plants = future_plants_dataframe.where(data['demand_at'] > future_plants_dataframe['start_at']).dropna()
            aux += filtered_future_plants['reliability_obligation'].sum() + filtered_future_plants['long_term_contract'].sum()
        # print(aux)
        # demand_dataframe['Enficc'] = aux_result
        # print(demand_dataframe)
if __name__ == "__main__":
    object = sddp_case(1)
    # object.calculate_max_new_capacity_table()
    # object.calculate_meta_matrix_table()
    # object.calculate_LCOE_table()
    # object.calculate_date_plants()
    # object.calculate_initialization_data()
    # object.calculate_demand_vs_enficc_table()
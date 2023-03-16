import os
import shutil

import numpy as np
import pandas as pd

from sddp.models import Generation, Project, Demand, Db, MarginalCostDemand, ReturnRate, WeightBlocks


def vna(tasa, arr_valores, desfase=0):
    """
    Se implementa porque la version de numpy da diferente a la de excel, la formula usada aqui 
    es la usada en la funcion VNA de excel encontrada en esta pagina:
        https://support.microsoft.com/es-es/office/vna-función-vna-8672cb67-2576-4d07-b67b-ac28acf2a568?ns=excel&version=16&syslcid=3082&uilcid=3082&appver=zxl160&helpid=xlmain11.chm60059&ui=es-es&rs=es-es&ad=es

    Los parametros son los mismos excepto por:
        desfase: int : desfase en el exponente que acompaña la tasa, es aplicado debido a que en los beneficios 
                       operativos el vna es calculado desde el año de la ultima tasa reconocida y no desde donde se tienen datos

    """
    return sum([arr_valores[i]/((1+tasa)**(i+1+desfase)) for i in range(len(arr_valores))])


def quartil_sddp(k, x):
    # funcion de ayuda para los cuartiles calculados como en el sddp,
    # donde se toma el kesimo valor menor, que en este caso es k

    x = np.sort(x.values.T)
    return x[k]


def aplicar_pesos(df_pesos, x):
    # Aplicar pesos correspondientes a la base de datos a los bloques

    pesos = df_pesos['weight'].values
    x = np.sum(x*pesos)/np.sum(pesos)

    return x       


def using_Grouper(df):
    # Tomado de:
    # https://stackoverflow.com/questions/15799162/resampling-within-a-pandas-multiindex
    # Solucion mas veloz en comparacion con otras 2 expuestas
    level_values = df.index.get_level_values
    return (df.groupby([pd.Grouper(freq='Y', level=0)]+[level_values(1)]).sum())


class OperatingProfitCalculations(object):
    """docstring for OperatingProfitCalculations
    
    Container for calculated data from operating profits
    
    Attributes:
        graphics (dict): Dict for save data related to graphics
        metadata (dict): Dict to save data of interest that are not from graphs or tables
        raw_data (dict): Dict for save generate data from OperatingProfitCalculator, ready for
                         proccess and generate data for graphics, tables and etc
        tables (dict)  : Dict for save data related to tables
    
    Deleted Attributes:
        grap_and_tab (dict): Dict for save data to use in graphics and tables
    """
    def __init__(self):
        super(OperatingProfitCalculations, self).__init__()

        self.tables = dict()
        self.graphics = dict()
        self.raw_data = dict()
        self.metadata = dict()

        self.metadata['month_list'] = [
            'Enero', 'Febrero', 'Marzo', 'Abril',
            'Mayo', 'Junio', 'Julio', 'Agosto',
            'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
            ]


class OperatingProfitCalculator(object):
    """docstring for OperatingProfitCalculator

    Calculator for operating profits
    
    Attributes:
        arg (TYPE): Description
    """
    def __init__(self):
        super(OperatingProfitCalculator, self).__init__()


    def calculate_operating_profit(self, parameters, opc):

        self.parameters = parameters

        # Are valid parameters?
        self.__check_parameters()

        # Get require extra data from database, time series, constans, etc
        db_parameters = self.__get_db_parameters()


        # Perform calculations 
        df_tasas_reconocidas, año_inicio_simulacion, tasa = self.__calculate_rate_to_use()

        (df_cmg_caso_base, df_cmg_proyecto, 
         df_pb_caso_base, df_pb_proyecto, 
         df_demanda) = self.__prepare_db_parameters(db_parameters)

        df_delta_alt1 = self.__calculate_delta(df_cmg_caso_base, df_cmg_proyecto)

        df_ben_alt1_bloque, df_demanda = self.__calculate_profits_alt1_block(df_delta_alt1, df_demanda)

        df_ben_alt1_mes = self.__calculate_profits_alt1_monthly(df_ben_alt1_bloque)

        opc.raw_data['vpn'] = self.__calculate_monthly_vpn(df_ben_alt1_mes, tasa)

        df_ben_alt1_año = self.__calculate_profits_alt1_yearly(df_ben_alt1_mes)

        (cantidad_simulaciones, df_vpn_anual, desfase_vna, 
         opc.raw_data['df_estadisticas_grafica_bel_alt1_año'],
         opc.raw_data['estadisticas_descriptivas_vpn_anual_primer_año']) = self.__calculate_yearly_vpn(df_ben_alt1_año, año_inicio_simulacion)

        (opc.raw_data['tabla1_anualidad_beneficios'],
         opc.raw_data['tabla2_anualidad_beneficios']) = self.__calculate_annual_benefits(df_ben_alt1_año, df_vpn_anual, desfase_vna, 
                                                                                         opc.raw_data['estadisticas_descriptivas_vpn_anual_primer_año'])


        opc.raw_data['tabla_grafica_beneficios'] = self.__calculate_consolidated_profit(df_ben_alt1_bloque)

        opc.raw_data['tabla_grafica_delta'] = self.__calculate_delta_consolidation(df_delta_alt1)

        (opc.raw_data['tabla_grafica_costo_marginal_cb'],
         opc.raw_data['tabla_grafica_costo_marginal_pr'],
         opc.raw_data['tabla_costo_marginal_promedio']) = self.__calculate_marginal_costs(df_cmg_caso_base, df_cmg_proyecto, 
                                                                                        df_pb_caso_base, df_pb_proyecto, cantidad_simulaciones)

        (opc.raw_data['tabla_generacion_grafica_mensual'],
         opc.raw_data['tabla_generacion_anual']) = self.__calculate_generation_with_project_data(db_parameters, 
                                                                                                 opc.raw_data['tabla_grafica_costo_marginal_pr'], 
                                                                                                 cantidad_simulaciones)

        # Add to opc extra data that not belong to tables or graphics but is wished for engineers
        opc.metadata['df_ben_alt1_año'] = df_ben_alt1_año
        opc.metadata['df_ben_alt1_mes'] = df_ben_alt1_mes
        opc.metadata['tasas_reconocidas'] = df_ben_alt1_mes


        return opc


    def __check_parameters(self):

        list_necessary_parameters = ['USDCOP', 
                                     'FECHA_ENTRADA_OPERACION', 
                                     'FECHA_LIMITE_OPERACION',
                                     'FACTOR_DEMANDA',
                                     'ID_BD_CASO_BASE',
                                     'ID_BD_PROYECTO',
                                     'DF_TASAS_RECONOCIDAS',
                                     'ID_PROYECTO',
                                     'PLANTA_PROYECTO'
                                     ]
        for param in list_necessary_parameters:

            try:
                self.parameters[param]

            except KeyError as e:
                raise KeyError(param, ' not founded in parameters dict')


    def __get_db_parameters(self):

        # Get extra data from databases from project
        #   Marginal cost base case
        cmg_base_case = pd.DataFrame(
                                list(MarginalCostDemand.objects
                                                        .filter(db_id=self.parameters['ID_BD_CASO_BASE'])
                                                        .values('date', 'block', 'serie', 'value'))
                        )
        cmg_base_case.columns = ['fecha', 'bloque', 'serie', 'valor']

        #   Marginal cost project
        cmg_proj = pd.DataFrame(
                            list(MarginalCostDemand.objects
                                                   .filter(db_id=self.parameters['ID_BD_PROYECTO'])
                                                   .values('date', 'block', 'serie', 'value'))
                    )
        cmg_proj.columns = ['fecha', 'bloque', 'serie', 'valor']
        

        #   Block weights: MODIFY IF WISH SOMETHING LIKE ReturnRate's
        weights = pd.DataFrame(list(WeightBlocks.objects.all().values('block', 'weight'))).set_index('block')

        #   Demand project
        demand = pd.DataFrame(
                        list(Demand.objects
                                    .filter(project_id=self.parameters['ID_PROYECTO'])
                                    .values('date', 'block', 'value'))
                    )
        demand.columns = ['fecha', 'bloque', 'valor']


        #   Planta generation
        generation = pd.DataFrame(
                            list(Generation.objects
                                           .filter(db_id=self.parameters['ID_BD_PROYECTO'])
                                           .values('date', 'block', 'serie', 'value'))
                    )
        
        if len(generation) > 0:
            generation.columns = ['fecha', 'bloque', 'serie', 'valor']


        db_parameters = {'cmg_base_case': cmg_base_case,
                         'cmg_proj'     : cmg_proj,
                         'weights'      : weights,
                         'demand'       : demand,
                         'generation'   : generation
                        }

        return db_parameters


    def __calculate_rate_to_use(self):


        # Calcular la tasa a emplear:
        df_tasas_reconocidas = self.parameters['DF_TASAS_RECONOCIDAS']

        df_tasas_reconocidas['Tasa reconocida'] = df_tasas_reconocidas['Tasa reconocida'].astype(np.float64)
        df_tasas_reconocidas['Año'] = df_tasas_reconocidas['Año'].astype(np.float64)

        df_tasas_reconocidas.set_index(['Año'], inplace=True)
        df_tasas_reconocidas.sort_index(inplace=True)


        if self.parameters['FECHA_ENTRADA_OPERACION'].year in df_tasas_reconocidas.index:
            tasa_retorno = df_tasas_reconocidas.loc[self.parameters['FECHA_ENTRADA_OPERACION'].year, 'Tasa reconocida']
        else:
            tasa_retorno = df_tasas_reconocidas.iloc[-1, 0]

        tasa = (1+tasa_retorno)**(1/12) - 1


        año_inicio_simulacion = df_tasas_reconocidas.index[0]

        return df_tasas_reconocidas, año_inicio_simulacion, tasa


    def __prepare_db_parameters(self, db_parameters):

        # Obtener datos requeridos de la base de datos -------------------------------------------------------------------------
        # Obtener los costos marginales del caso base y del proyecto 
        #   Se sabe que se necesita el costo marginal de la bd1 (Caso base) y bd2 (Proyecto)
        df_cmg_caso_base = db_parameters['cmg_base_case']
        df_cmg_proyecto  = db_parameters['cmg_proj']

        #   dfs de pesos por bloque para ambas bases de datos
        df_pb_caso_base = db_parameters['weights']
        df_pb_proyecto  = db_parameters['weights']

        # Crear multi-index
        df_cmg_caso_base.set_index(['fecha', 'bloque', 'serie'], inplace=True)    
        df_cmg_proyecto.set_index(['fecha', 'bloque', 'serie'], inplace=True)     

        # Obtener demanda del proyecto
        df_demanda = db_parameters['demand']

        df_demanda['valor'] = df_demanda['valor']*self.parameters['FACTOR_DEMANDA']

        return df_cmg_caso_base, df_cmg_proyecto, df_pb_caso_base, df_pb_proyecto, df_demanda


    def __calculate_delta(self, df_cmg_caso_base, df_cmg_proyecto):

        df_delta_alt1 = (df_cmg_caso_base - df_cmg_proyecto)         # Resta de costos marginales
        df_delta_alt1[df_delta_alt1 <= 0 ] = 0                       # Tomar solo los valores mayores a 0
        df_delta_alt1 = df_delta_alt1*self.parameters['USDCOP']/1000 # Multiplicar por factor de divisa
        df_delta_alt1.sort_index(inplace=True)                       # Ordenar Multiindex

        return df_delta_alt1


    def __calculate_profits_alt1_block(self, df_delta_alt1, df_demanda):


        # Calcular ben_alt1_bloque -----------------------------------------------------------------------------------------------
        df_ben_alt1_bloque = df_delta_alt1.copy()             # Esta df se obtiene a partir del delta, por lo tanto usarla como inicio
        #   Para tomar solo las filas entre los rangos de operacion, se debe agregar la columna fecha como columna
        #   nuevamente, reiniciar el indice permite esto y su posterior toma de datos
        df_ben_alt1_bloque.reset_index(inplace=True)          
        df_ben_alt1_bloque = df_ben_alt1_bloque[(df_ben_alt1_bloque['fecha'] >= self.parameters['FECHA_ENTRADA_OPERACION']) & 
                                                (df_ben_alt1_bloque['fecha'] <= self.parameters['FECHA_LIMITE_OPERACION'])]

        df_demanda = df_demanda[(df_demanda['fecha'] >= self.parameters['FECHA_ENTRADA_OPERACION']) & 
                                (df_demanda['fecha'] <= self.parameters['FECHA_LIMITE_OPERACION'])]                                        


        #   Multiplicar por la df_demanda segun las fechas y bloques
        df_ben_alt1_bloque.set_index(['fecha', 'bloque'], inplace=True)
        df_demanda.set_index(['fecha', 'bloque'], inplace=True)

        #   Aplicar sort en el index para facilitar la multiplicacion entre ambas columnas de valor de las dataframes
        df_delta_alt1.sort_index(inplace=True)
        df_demanda.sort_index(inplace=True)


        df_ben_alt1_bloque['valor'] = df_ben_alt1_bloque['valor']*df_demanda['valor']

        return df_ben_alt1_bloque, df_demanda


    def __calculate_profits_alt1_monthly(self, df_ben_alt1_bloque):

        # Calcular ben_alt1_mes -----------------------------------------------------------------------------------------------
        #   En esta df se unifican los valores de los bloques de cada mes, en un unico valor correspondiente a mes en que
        #   se encuentran los bloques por medio de una sumatoria
        df_ben_alt1_mes = df_ben_alt1_bloque.copy()          # Esta df se obtiene a partir de self.__df_ben_alt1_bloque, por lo tanto usarla como inicio
        df_ben_alt1_mes.set_index('serie', append=True, inplace=True)

        #   Aplicar la sumatoria requerida para obtener la df requerida
        df_ben_alt1_mes = df_ben_alt1_mes.groupby(level=['fecha', 'serie']).sum()

        return df_ben_alt1_mes


    def __calculate_monthly_vpn(self, df_ben_alt1_mes, tasa):


        # Calcular VPN mensual ------------------------------------------------------------------------------------------------
        df_vpn_mes = df_ben_alt1_mes.copy()            # Esta df se obtiene a partir de self.__df_ben_alt1_mes, por lo tanto usarla como inicio

        #   Seleccionar y calular la tasa a usar en el calculo
        df_vpn_mes = df_vpn_mes.groupby(level=['serie']).agg(lambda x: vna(tasa, x))/1000  # LINEA QUE DA LIGERAMENTE DIFERENTE, ACLARAR

        #   RESULTADOS DE PESTAÑA self.__df_ben_alt1_mes: ESTADISITICAS DESCRIPTIVAS
        vpn = {
            'minimo'  :df_vpn_mes['valor'].min(),
            'per_05'  :df_vpn_mes['valor'].quantile(.05),
            'mediana' :df_vpn_mes['valor'].median(),
            'per_95'  :df_vpn_mes['valor'].quantile(.95),
            'maximo'  :df_vpn_mes['valor'].max(),
        }

        return vpn


    def __calculate_profits_alt1_yearly(self, df_ben_alt1_mes):


        # Calcular Ben_alt1_año ------------------------------------------------------------------------------------------------
        df_ben_alt1_año = df_ben_alt1_mes.copy()    # Esta df se obtiene a partir de self.__df_ben_alt1_mes, por lo tanto usarla como inicio

        # Aplicar Resample a un año sin modificar el segundo indice que corresponde a "series"
        df_ben_alt1_año = using_Grouper(df_ben_alt1_año)

        return df_ben_alt1_año


    def __calculate_yearly_vpn(self, df_ben_alt1_año, año_inicio_simulacion):


        # Calcular VPN anual ------------------------------------------------------------------------------------------------
        #   A diferencia de la del mes, primero se calcula la del ultimo año y se utilizan estos datos 
        #   para ir calculando las de años anteriores
        # self.__df_vpn_anual = pd.DataFrame(index=self.__DF_TASAS_RECONOCIDAS.index, columns=list(set(self.__df_ben_alt1_año.index.get_level_values(1))))
        df_vpn_anual = pd.DataFrame(index=list(set(df_ben_alt1_año.index.get_level_values(1))), 
                                    columns=self.parameters['DF_TASAS_RECONOCIDAS'].index)


        #   Calcular VPN del ultimo año
        ultima_tasa_reconocida = self.parameters['DF_TASAS_RECONOCIDAS'].iloc[-1, 0]


        #   Calcular desfase de años entre el inicio de los datos de la simulacion y la ultima tasa reconocida
        año_inicio_datos    = int(str(df_ben_alt1_año.index.get_level_values(0)[0])[:4])
        año_ultima_tasa_rec = self.parameters['DF_TASAS_RECONOCIDAS'].index[-1]
        desfase_vna         = año_inicio_datos - año_ultima_tasa_rec

        #       Realizar calculo del vpn del ultimo año
        df_vpn_anual.iloc[:, -1] = df_ben_alt1_año.groupby(level=['serie']).agg(lambda x: vna(ultima_tasa_reconocida, x, desfase=desfase_vna)).values

        #   Calcular VPN de los años previos
        #       Se aplica un reversed porque para los calculos del vpn del año requerido se requieren los calculos del año siguiente
        #       aunque esto no aplica para el ultimo año, que se calcula en los pasos previos a este proceso 
        for i in reversed(range(len(df_vpn_anual.columns[:-1]))):
            i_año_actual    = df_vpn_anual.columns[i]
            i_año_siguiente = df_vpn_anual.columns[i+1]


            # El año tiene un valor para la serie en df_ben_alt1_año?
            # Si es asi entonces iterar sobre toda la columna
            if i_año_actual in df_ben_alt1_año.index:
                # PROBAR ESTA PARTE -----------------------------------------PROBAR ESTA PARTE ----------------- PROBAR ESTA PARTE --------------
                arr_vpn_año = valor_df_ben_alt1_año.loc[:, i_año_actual]

            # De lo contrario asumir que las componentes para todas las series son 0
            else:
                arr_vpn_año = np.zeros(len(df_vpn_anual.index)).T

            # Indexar tasa
            tasa_año = self.parameters['DF_TASAS_RECONOCIDAS'].iloc[i, 0]

            # Calcular vpn para el año de la iteracion
            df_vpn_anual.iloc[:, i] = arr_vpn_año + df_vpn_anual.loc[:, i_año_siguiente].values/(1+tasa_año)

        # Division por 1000 que se aplica en el archivo de excel donde esta el ejemplo de beneficios operativos
        df_vpn_anual = df_vpn_anual/1000


        # Calcular estadisticas descriptivas para el primer año de simulacion
        # estos resultados se usan mas adelante, por eso se ponen en una serie
        #   PERCENTILES SON CALCULADOS DE FORMA EXTRAÑA AQUI, DIFIEREN DEL CALCULADO POR PANDAS, AQUI
        #   ARROJAN UN VALOR QUE SE ENCUENTRA EN la df_vpn_anual
        lista_valores_vpn_año_inicio = list(df_vpn_anual[año_inicio_simulacion].values)
        lista_valores_vpn_año_inicio.sort()

        #       Valor usado para calcular los percentiles
        cantidad_simulaciones = len(df_vpn_anual)
        #       Si queres saber porque el "-1", preguntale a excel y el como toma el 5to menor y mayor de una lista, y la mediana
        i_mn = round(cantidad_simulaciones*0.01) - 1
        i_05 = round(cantidad_simulaciones*0.05) - 1
        i_md = round(cantidad_simulaciones*0.5) - 1
        i_95 = round(cantidad_simulaciones*0.95) - 1
        i_mx = round(cantidad_simulaciones*0.98) - 1


        estadisticas_descriptivas_vpn_anual_primer_año = pd.Series()
        # estadisticas_descriptivas_vpn_anual_primer_año['min']     = df_vpn_anual[AÑO_INICIO_SIMULACION].min()
        estadisticas_descriptivas_vpn_anual_primer_año['min']     = lista_valores_vpn_año_inicio[i_mn]
        estadisticas_descriptivas_vpn_anual_primer_año['per_05']  = lista_valores_vpn_año_inicio[i_05]
        estadisticas_descriptivas_vpn_anual_primer_año['mediana'] = lista_valores_vpn_año_inicio[i_md]
        estadisticas_descriptivas_vpn_anual_primer_año['per_95']  = lista_valores_vpn_año_inicio[i_95]
        estadisticas_descriptivas_vpn_anual_primer_año['max']     = lista_valores_vpn_año_inicio[i_mx]


        estadisticas_descriptivas_vpn_anual_primer_año['i_per_05']  = list(df_vpn_anual[df_vpn_anual[año_inicio_simulacion] == estadisticas_descriptivas_vpn_anual_primer_año['per_05']].index)[0]
        estadisticas_descriptivas_vpn_anual_primer_año['i_mediana'] = list(df_vpn_anual[df_vpn_anual[año_inicio_simulacion] == estadisticas_descriptivas_vpn_anual_primer_año['mediana']].index)[0]
        estadisticas_descriptivas_vpn_anual_primer_año['i_per_95']  = list(df_vpn_anual[df_vpn_anual[año_inicio_simulacion] == estadisticas_descriptivas_vpn_anual_primer_año['per_95']].index)[0]

        # Calcular estadisticas descriptivas usadas para construir la grafica de ben_alt1_año
        df_estadisticas_grafica_bel_alt1_año = pd.DataFrame(index=np.arange(1, 18) , columns=['clase', 'frecuencia', '%_acumulado', 'can_menores', '%'])
        df_estadisticas_grafica_bel_alt1_año.loc[1, 'clase']      = np.round(estadisticas_descriptivas_vpn_anual_primer_año['min']/10 - 1)*10
        df_estadisticas_grafica_bel_alt1_año.loc[1, 'frecuencia'] = 0
        df_estadisticas_grafica_bel_alt1_año.loc[1, 'can_menores'] = 0
        df_estadisticas_grafica_bel_alt1_año.loc[1, '%_acumulado'] = 0
        df_estadisticas_grafica_bel_alt1_año.loc[1, '%'] = 0

        #   Valor sin descripcion usado en los calculos de esta tabla
        valor_x = np.round((estadisticas_descriptivas_vpn_anual_primer_año['max'] - df_estadisticas_grafica_bel_alt1_año.loc[1, 'clase'])/15)

        for i in range(2, 18):
            if i is 17:
                df_estadisticas_grafica_bel_alt1_año.loc[17, 'clase'] = np.inf
            else:
                df_estadisticas_grafica_bel_alt1_año.loc[i, 'clase'] = df_estadisticas_grafica_bel_alt1_año.loc[i - 1, 'clase'] + valor_x
            df_estadisticas_grafica_bel_alt1_año.loc[i, 'can_menores'] = len(df_vpn_anual[df_vpn_anual[año_inicio_simulacion] < df_estadisticas_grafica_bel_alt1_año.loc[i, 'clase']])
            

        for i in range(2, 18):    
            df_estadisticas_grafica_bel_alt1_año.loc[i, 'frecuencia'] = df_estadisticas_grafica_bel_alt1_año.loc[i, 'can_menores'] - df_estadisticas_grafica_bel_alt1_año.loc[i-1, 'can_menores']

        for i in range(2, 18):    
            df_estadisticas_grafica_bel_alt1_año.loc[i, '%'] = df_estadisticas_grafica_bel_alt1_año.loc[i, 'frecuencia']/df_estadisticas_grafica_bel_alt1_año['frecuencia'].sum()

        for i in range(2, 18):    
            df_estadisticas_grafica_bel_alt1_año.loc[i, '%_acumulado'] = df_estadisticas_grafica_bel_alt1_año.loc[:i, '%'].sum()*100

        #   Agregar tabla de graficas a datos para entregar
        # datos_entrega['df_estadisticas_grafica_bel_alt1_año']           = df_estadisticas_grafica_bel_alt1_año
        # datos_entrega['estadisticas_descriptivas_vpn_anual_primer_año'] = estadisticas_descriptivas_vpn_anual_primer_año

        # opc.df_estadisticas_grafica_bel_alt1_año = df_estadisticas_grafica_bel_alt1_año
        # opc.estadisticas_descriptivas_vpn_anual_primer_año = estadisticas_descriptivas_vpn_anual_primer_año
        # opc.cantidad_simulaciones = cantidad_simulaciones

        # return cantidad_simulaciones, df_vpn_anual, desfase_vna, opc
        return (cantidad_simulaciones, df_vpn_anual, desfase_vna, 
                df_estadisticas_grafica_bel_alt1_año, 
                estadisticas_descriptivas_vpn_anual_primer_año)


    def __calculate_annual_benefits(self, df_ben_alt1_año, df_vpn_anual, desfase_vna, estadisticas_descriptivas_vpn_anual_primer_año):


        # Calcular Anualidad beneficios ------------------------------------------------------------------------------------------------
        #   Calcular tabla de etapas con estadisticas descriptivas, que se encuentra en la parte inferior izquierda de la pestaña correspondiente

        tabla_etapas_est_desc = pd.DataFrame(index=df_ben_alt1_año.index.get_level_values(0).unique(), 
                                             columns=('05PSS', 'Mediana', '95PSS'))

        #   Agregar valores a las tablas, usando la Serie que posee per_05, mediana y per_95, por lo que se requieren los indices encontrados en el paso previo
        tabla_etapas_est_desc.loc[:, '05PSS']  =  df_ben_alt1_año.iloc[(df_ben_alt1_año.index.get_level_values(1) == int(estadisticas_descriptivas_vpn_anual_primer_año['i_per_05'])), 0].values
        tabla_etapas_est_desc.loc[:, 'Mediana'] = df_ben_alt1_año.iloc[(df_ben_alt1_año.index.get_level_values(1) == int(estadisticas_descriptivas_vpn_anual_primer_año['i_mediana'])), 0].values
        tabla_etapas_est_desc.loc[:, '95PSS']  = df_ben_alt1_año.iloc[(df_ben_alt1_año.index.get_level_values(1) == int(estadisticas_descriptivas_vpn_anual_primer_año['i_per_95'])), 0].values


        #   Calcular tabla sin nombre de la esquina superior izq.
        #   Este proceso es analogo al calculo de la tabla del VNA, por lo que empieza en la ultima fila y va retrocediendo en los años
        df_tasas_reconocidas = self.parameters['DF_TASAS_RECONOCIDAS']
        tabla_si = pd.DataFrame(index=df_tasas_reconocidas.index, columns=('05PSS', 'Mediana', '95PSS'))

        tabla_si.iloc[-1, 0] = vna(df_tasas_reconocidas.iloc[-1, 0], tabla_etapas_est_desc['05PSS'], desfase_vna)
        tabla_si.iloc[-1, 1] = vna(df_tasas_reconocidas.iloc[-1, 0], tabla_etapas_est_desc['Mediana'], desfase_vna)
        tabla_si.iloc[-1, 2] = vna(df_tasas_reconocidas.iloc[-1, 0], tabla_etapas_est_desc['95PSS'], desfase_vna)

        #       Calcular filas anteriores
        for i in reversed(range(len(tabla_si.index[:-1]))):
            i_año_actual    = df_vpn_anual.columns[i]
            i_año_siguiente = df_vpn_anual.columns[i+1]


            # El año tiene un valor para la serie en tabla_etapas_est_desc?
            # Si es asi entonces iterar sobre toda la columna
            if i_año_actual in tabla_etapas_est_desc.index:
                # PROBAR ESTA PARTE -----------------------------------------PROBAR ESTA PARTE ----------------- PROBAR ESTA PARTE --------------
                arr_eed_05 = tabla_etapas_est_desc.at[i_año_actual, '05PSS']
                arr_eed_md = tabla_etapas_est_desc.at[i_año_actual, 'Mediana']
                arr_eed_95 = tabla_etapas_est_desc.at[i_año_actual, '95PSS']

            # De lo contrario asumir que las componentes para todas las series son 0
            else:
                arr_eed_05 = 0
                arr_eed_md = 0
                arr_eed_95 = 0


            # Indexar tasa
            tasa_año = df_tasas_reconocidas.loc[i_año_actual, 'Tasa reconocida']

            # Calcular vpn para el año de la iteracion
            tabla_si.loc[i_año_actual, '05PSS']   = arr_eed_05 + tabla_si.at[i_año_siguiente, '05PSS']/(1+tasa_año)
            tabla_si.loc[i_año_actual, 'Mediana'] = arr_eed_md + tabla_si.at[i_año_siguiente, 'Mediana']/(1+tasa_año)
            tabla_si.loc[i_año_actual, '95PSS']   = arr_eed_95 + tabla_si.at[i_año_siguiente, '95PSS']/(1+tasa_año)


        tabla_si = tabla_si/1000

        #   LA TABLA DE ETAPA, CUAL ES LA ETAPA QUE SE DEBE TOMAR? SOLO CORRESPONDE A UNA FILA DE LA TABLA_SI
        # datos_entrega['tabla1_anualidad_beneficios'] = tabla_si
        # datos_entrega['tabla2_anualidad_beneficios'] = tabla_etapas_est_desc

        # opc.tabla1_anualidad_beneficios = tabla_si
        # opc.tabla2_anualidad_beneficios = tabla_etapas_est_desc

        tabla1_anualidad_beneficios = tabla_si
        tabla2_anualidad_beneficios = tabla_etapas_est_desc        

        return tabla1_anualidad_beneficios, tabla2_anualidad_beneficios


    def __calculate_consolidated_profit(self, df_ben_alt1_bloque):


        # Calcular Consolidado de Beneficios ------------------------------------------------------------------------------------------------

        # Calcular tabla para graficar directamente para todas las series sin necesidad de una tabla intermedia como en la muestra
        # de los beneficios operativos
        #     Inicializar tabla de datos de promedios de consolidados beneficios
        #                                             mes                      bloque
        tabla_grafica_beneficios = pd.DataFrame(index=np.arange(1,13), columns=np.arange(1,6)).astype(np.float64)

        #     Calcular promedios
        for m in tabla_grafica_beneficios.index:

            # Calcular promedios de los diferentes bloques para un mes en especifico
            promedios_bloque = df_ben_alt1_bloque[df_ben_alt1_bloque.index.get_level_values(0).month == m].groupby(level=['bloque']).mean()

            # Pasar promedios de los bloques para el mes especifico a las celdas correspondientes en la tabla_grafica_beneficios
            for b in tabla_grafica_beneficios.columns:
                tabla_grafica_beneficios.at[m, b] = promedios_bloque.at[b, 'valor']

        #     Aplicar division por 1000 y redondear la dataframe completa a 2 decimales como en el excel de muestra
        tabla_grafica_beneficios /= 1000
        tabla_grafica_beneficios = tabla_grafica_beneficios.round(decimals=2)

        #   Agregar tabla de graficas a datos para entregar
        # datos_entrega['tabla_grafica_beneficios'] = tabla_grafica_beneficios
        # opc.tabla_grafica_beneficios = tabla_grafica_beneficios

        return tabla_grafica_beneficios


    def __calculate_delta_consolidation(self, df_delta_alt1):



        # Calcular Consolidado de Delta ------------------------------------------------------------------------------------------------

        # Calcular tabla para graficar directamente para todas las series sin necesidad de una tabla intermedia como en la muestra
        # de los beneficios operativos
        #     Inicializar tabla de datos de promedios de consolidados beneficios
        #                                             mes                      bloque
        tabla_grafica_delta = pd.DataFrame(index=np.arange(1,13), columns=np.arange(1,6)).astype(np.float64)

        df_delta_alt1 = df_delta_alt1[(self.parameters['FECHA_ENTRADA_OPERACION'] <= df_delta_alt1.index.get_level_values(0)) &
                                      (self.parameters['FECHA_LIMITE_OPERACION'] >= df_delta_alt1.index.get_level_values(0))]


        #     Calcular promedios
        for m in tabla_grafica_delta.index:

            # Calcular promedios de los diferentes bloques para un mes en especifico
            promedios_bloque = df_delta_alt1[df_delta_alt1.index.get_level_values(0).month == m].groupby(level=['bloque']).mean()

            # Pasar promedios de los bloques para el mes especifico a las celdas correspondientes en la tabla_grafica_beneficios
            for b in tabla_grafica_delta.columns:
                tabla_grafica_delta.at[m, b] = promedios_bloque.at[b, 'valor']

        #     Aplicar division por 1000 y redondear la dataframe completa a 2 decimales como en el excel de muestra
        tabla_grafica_delta = tabla_grafica_delta.round(decimals=2)


        #   Agregar tabla de graficas a datos para entregar
        # datos_entrega['tabla_grafica_delta'] = tabla_grafica_delta
        # opc.tabla_grafica_delta = tabla_grafica_delta

        return tabla_grafica_delta
        

    def __calculate_marginal_costs(self, df_cmg_caso_base, df_cmg_proyecto, df_pb_caso_base, df_pb_proyecto, cantidad_simulaciones):


        # Calcular grafica de costo marginal sin y con proyecto ------------------------------------------------------------------------
        #   Si queres saber porque el "-1", preguntale a excel y el como toma el 5to menor y mayor de una lista, y la mediana
        i_05 = round(cantidad_simulaciones*0.10) - 1
        i_95 = round(cantidad_simulaciones*0.90)

        tabla_costo_marginal_cb = df_cmg_caso_base.copy()
        tabla_costo_marginal_pr = df_cmg_proyecto.copy()

        tabla_costo_marginal_cb = self.__calculate_base_case_marg_cost(tabla_costo_marginal_cb, df_cmg_caso_base, df_pb_caso_base, i_05, i_95)
        tabla_costo_marginal_pr = self.__calculate_project_marg_cost(tabla_costo_marginal_pr, df_cmg_proyecto, df_pb_proyecto, i_05, i_95)

        tabla_costo_marginal_promedio = self.__calculate_mean_marg_cost(tabla_costo_marginal_cb, tabla_costo_marginal_pr)

        return tabla_costo_marginal_cb, tabla_costo_marginal_pr, tabla_costo_marginal_promedio


    def __calculate_base_case_marg_cost(self, tabla_costo_marginal_cb, df_cmg_caso_base, df_pb_caso_base, i_05, i_95):


        #   __________________________________________________________________________________________________________________________
        #   Calcular Tabla para costo marginal para el caso base _____________________________________________________________________
        #   __________________________________________________________________________________________________________________________
        tabla_costo_marginal_cb = tabla_costo_marginal_cb.groupby(level=['fecha', 'bloque']).mean()
        tabla_costo_marginal_cb.rename(columns={'valor': 'prom'}, inplace=True)


        # tabla_costo_marginal_cb['q_sup2'] = self.__df_cmg_caso_base.groupby(level=['fecha', 'bloque']).quantile(0.95)
        tabla_costo_marginal_cb['q_sup'] = df_cmg_caso_base.groupby(level=['fecha', 'bloque']).agg(lambda x: quartil_sddp(i_95, x)).values
        tabla_costo_marginal_cb['q_inf'] = df_cmg_caso_base.groupby(level=['fecha', 'bloque']).agg(lambda x: quartil_sddp(i_05, x)).values


        # Aplicar pesos
        tabla_costo_marginal_cb_copia    = tabla_costo_marginal_cb.copy()    
        tabla_costo_marginal_cb          = pd.DataFrame(tabla_costo_marginal_cb_copia['prom'].groupby(level=['fecha']).agg(lambda x: aplicar_pesos(df_pb_caso_base, x)))
        tabla_costo_marginal_cb['q_sup'] = tabla_costo_marginal_cb_copia['q_sup'].groupby(level=['fecha']).agg(lambda x: aplicar_pesos(df_pb_caso_base, x))
        tabla_costo_marginal_cb['q_inf'] = tabla_costo_marginal_cb_copia['q_inf'].groupby(level=['fecha']).agg(lambda x: aplicar_pesos(df_pb_caso_base, x))

        # opc.tabla_grafica_costo_marginal_cb = tabla_costo_marginal_cb

        return tabla_costo_marginal_cb


    def __calculate_project_marg_cost(self, tabla_costo_marginal_pr, df_cmg_proyecto, df_pb_proyecto, i_05, i_95):


        #   __________________________________________________________________________________________________________________________
        #   Calcular Tabla para costo marginal para el proyecto ______________________________________________________________________
        #   __________________________________________________________________________________________________________________________
        tabla_costo_marginal_pr = tabla_costo_marginal_pr.groupby(level=['fecha', 'bloque']).mean()
        tabla_costo_marginal_pr.rename(columns={'valor': 'prom'}, inplace=True)


        # tabla_costo_marginal_cb['q_sup2'] = self.__df_cmg_caso_base.groupby(level=['fecha', 'bloque']).quantile(0.95)
        tabla_costo_marginal_pr['q_sup'] = df_cmg_proyecto.groupby(level=['fecha', 'bloque']).agg(lambda x: quartil_sddp(i_95, x)).values
        tabla_costo_marginal_pr['q_inf'] = df_cmg_proyecto.groupby(level=['fecha', 'bloque']).agg(lambda x: quartil_sddp(i_05, x)).values


        # Aplicar pesos
        tabla_costo_marginal_pr_copia    = tabla_costo_marginal_pr.copy()    
        tabla_costo_marginal_pr          = pd.DataFrame(tabla_costo_marginal_pr_copia['prom'].groupby(level=['fecha']).agg(lambda x: aplicar_pesos(df_pb_proyecto, x)))
        tabla_costo_marginal_pr['q_sup'] = tabla_costo_marginal_pr_copia['q_sup'].groupby(level=['fecha']).agg(lambda x: aplicar_pesos(df_pb_proyecto, x))
        tabla_costo_marginal_pr['q_inf'] = tabla_costo_marginal_pr_copia['q_inf'].groupby(level=['fecha']).agg(lambda x: aplicar_pesos(df_pb_proyecto, x))

        # opc.tabla_grafica_costo_marginal_pr = tabla_costo_marginal_pr

        return tabla_costo_marginal_pr


        # datos_entrega['tabla_grafica_costo_marginal_cb'] = tabla_costo_marginal_cb
        # datos_entrega['tabla_grafica_costo_marginal_pr'] = tabla_costo_marginal_pr


    def __calculate_mean_marg_cost(self, tabla_costo_marginal_cb, tabla_costo_marginal_pr):

        # Calcular tabla_costo_marginal_promedio
        tabla_costo_marginal_promedio = tabla_costo_marginal_cb.groupby(tabla_costo_marginal_cb.index.year).mean()
        tabla_costo_marginal_promedio = pd.DataFrame(tabla_costo_marginal_promedio['prom'])
        tabla_costo_marginal_promedio.rename(columns={'prom': 'Sin proyecto'}, inplace=True)

        tabla_costo_marginal_promedio['Con proyecto'] = tabla_costo_marginal_pr.groupby(tabla_costo_marginal_pr.index.year).mean()['prom']

        # datos_entrega['tabla_costo_marginal_promedio'] = tabla_costo_marginal_promedio.round(2)

        
        # opc.tabla_costo_marginal_promedio = tabla_costo_marginal_promedio

        return tabla_costo_marginal_promedio


    def __calculate_generation_with_project_data(self, db_parameters, tabla_costo_marginal_pr, cantidad_simulaciones):

        #   __________________________________________________________________________________________________________________________
        #   Calcular Tabla y Grafica de generacion con los datos de la planta del proyecto  __________________________________________
        #   __________________________________________________________________________________________________________________________

        if len(db_parameters['generation']) > 1:

            # Crear el multi-indice
            df_planta_proyecto = db_parameters['generation']
            df_planta_proyecto.set_index(['fecha', 'bloque', 'serie'], inplace=True)   


            tabla_grafica_mensual = df_planta_proyecto.groupby(level=['fecha']).sum()/100

            # Calcular las 3 columnas de la tabla anual
            #   Columna de promedio
            tabla_anual           = (df_planta_proyecto.groupby(level=['fecha']).sum().groupby(tabla_costo_marginal_pr.index.year).sum()/100).round(1)

            #   Columna de quartil superior/inferior
            #       Si queres saber porque el "-1", preguntale a excel y el como toma el 5to menor y mayor de una lista, y la mediana
            i_05 = round(cantidad_simulaciones*0.10) - 1
            i_95 = round(cantidad_simulaciones*0.90)

            df_intermedia = df_planta_proyecto.groupby([df_planta_proyecto.index.get_level_values(0), 'serie']).sum()

            q_sup = df_intermedia.groupby(df_intermedia.index.get_level_values(0)).agg(lambda x: quartil_sddp(i_95, x))
            tabla_anual['q_sup'] = q_sup.groupby(q_sup.index.year).sum().values

            q_inf = df_intermedia.groupby(df_intermedia.index.get_level_values(0)).agg(lambda x: quartil_sddp(i_05, x))
            tabla_anual['q_inf'] = q_inf.groupby(q_inf.index.year).sum().values    

            # Agregar tablas recien calculadas a los datos a entregar
            tabla_generacion_grafica_mensual = tabla_grafica_mensual
            tabla_generacion_anual           = tabla_anual.round(1).rename(columns={'valor':'prom'}).reset_index()

        else:
            # Agregar tablas recien calculadas a los datos a entregar
            tabla_generacion_grafica_mensual = pd.DataFrame(columns=['fecha', 'prom', 'q_sup', 'q_inf'])
            tabla_generacion_anual           = pd.DataFrame(columns=['fecha', 'prom', 'q_sup', 'q_inf'])


        return tabla_generacion_grafica_mensual, tabla_generacion_anual


def tranponer_df_beneficios(df_beneficios):
    """
        Transpone la df para que quede en el siguiente formato

              serie1 serie2 serie3 ... serieN
        fecha1
        fecha2
        fecha3
        ...
        fechaN


        Se aplica numba para agalizar el proceso de tranpocision en gran medida

    """

    df_beneficios.reset_index(inplace=True, drop=False)

    # print(df_beneficios)


    # Dado que numba no recibe datos de tipo timestamp, se procede a convertirlos a unix
    # df_beneficios['fecha'] = (df_beneficios['fecha'] - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s')

    fechas = df_beneficios['fecha'].unique()
    series = df_beneficios['serie'].unique()


    matriz_valores =  transpocision_numba(fechas, series, df_beneficios['valor'].values)

    # print(matriz_valores)


    # fechas = df_beneficios.index.get_level_values(0)
    # series = df_beneficios.index.get_level_values(1)

    df = pd.DataFrame(matriz_valores ,index=fechas, columns=series)

    # print(df.iloc[:, :10])


            

    return df


# @jit(nopython=True, fastmath = True, parallel = False, nogil=True, cache=False)
def transpocision_numba(fechas, series, valores):

    # print(fechas, series, valores)
    # print(len(fechas), len(series), len(valores))

    # Se inicializan los datos que tendra la df_final con el numero de filas que tendra
    # tendra 6 columnas debido a que sus columnas seran ['fecha', 'bloque', 'serie', 'id_bd', 'ubicacion', 'valor']
    matriz_final = np.full((len(fechas), len(series)), np.nan, dtype=np.float64)

    # Counter usado para iterar sobre cada fila de la df_final
    counter = 0

    for i in range(len(fechas)):
        
        for s in series:

            # print(len(valores), counter, s)
            # print(valores[counter])
            # print()

            matriz_final[i][s-1] = valores[counter]
            counter += 1


    return matriz_final


class PreparerFinalDataOperatingProfits(object):
    """docstring for PreparerFinalDataOperatingProfits"""


    def __init__(self):
        super(PreparerFinalDataOperatingProfits, self).__init__


    def prepare_final_data(self, parameters, opc):

        if not isinstance(opc, OperatingProfitCalculations):
            raise TypeError('Input data must be a OperatingProfitCalculations container')

        t1, t2, t3, t4 = self.__get_tables(opc.raw_data, parameters['AÑO_CALCULOS'])
        opc.tables['vpn']                   = t1
        opc.tables['annuity_benefits']      = t2
        opc.tables['average_marginal_cost'] = t3
        opc.tables['generation_plant']      = t4

        df_fig1, df_ann1 =self.__get_figure1(opc.raw_data)
        opc.graphics['histogram_of_operating_profit_graph'] = df_fig1
        opc.graphics['histogram_of_operating_profit_annotation'] = df_ann1

        df_fig2, df_fig3 = self.__get_figure2_3(opc.raw_data)
        opc.graphics['average_profits_per_demand_block'] = df_fig2
        opc.graphics['average_delta_marginal_cost_per_block_of_demand'] = df_fig3

        df_fig4, df_fig5 = self.__get_figure4_5(opc.raw_data)
        opc.graphics['marginal_cost_without_project'] = df_fig4
        opc.graphics['marginal_cost_with_project'] = df_fig5

        df_fig6 = self.__get_figure6(opc.raw_data)
        opc.graphics['generation_plant'] = df_fig6

        return opc

    def __get_tables(self, raw_data, AÑO_CALCULOS):

        # VPN
        t1 = raw_data['tabla1_anualidad_beneficios'].astype(np.float64).round(3)
        t1 = t1.reset_index().rename(columns={'index':'Año'})
        t1 = t1.loc[t1['Año']==AÑO_CALCULOS, :]

        # Anualidad beneficios
        t2 = raw_data['tabla2_anualidad_beneficios'].round(3)    
        t2['Año'] = [v.year for v in t2.index]
        t2 = t2[['Año', '05PSS', 'Mediana', '95PSS']]

        # Costo Marginal Promedio
        t3 = raw_data['tabla_costo_marginal_promedio']
        t3 = t3.reset_index().rename(columns={'fecha':'Año'}).round(3)

        # Generación planta
        t4 = raw_data['tabla_generacion_anual'].round(3)
        t4.rename(columns={'fecha':'Año', 'prom':'Prom', 'q_sup':'Q. Sup', 'q_inf':'Q. Inf'}, inplace=True)

        return t1, t2, t3, t4

    def __get_figure1(self, raw_data):

        # Figure 1
        #   data from x axis
        x = list(str(v) for v in raw_data['df_estadisticas_grafica_bel_alt1_año']['clase'].values)
        x[-1] = 'Mayor...'

        #   data from y axis
        frec  = raw_data['df_estadisticas_grafica_bel_alt1_año']['frecuencia'].values
        accum = raw_data['df_estadisticas_grafica_bel_alt1_año']['%_acumulado'].values

        #   assemble df for fig
        data = {
            'class'                 :x, 
            'frecuency'             :frec, 
            'accumulated_percentage':accum
        }
        df_fig1 = pd.DataFrame(data=data)

        # Annotations from figure 1
        vals = ['${} MIL MILLONES'.format(round(raw_data['estadisticas_descriptivas_vpn_anual_primer_año']['per_05'], 1)),
                '${} MIL MILLONES'.format(round(raw_data['estadisticas_descriptivas_vpn_anual_primer_año']['mediana'], 1)),
                '${} MIL MILLONES'.format(round(raw_data['estadisticas_descriptivas_vpn_anual_primer_año']['per_95'], 1))
        ]

        df_ann1 = pd.DataFrame(vals, index=['95 PSS', 'MEDIANA', '05 PSS']).T

        return df_fig1, df_ann1
        
    def __get_figure2_3(self, raw_data):
        df_fig2 = raw_data['tabla_grafica_beneficios']
        df_fig3 = raw_data['tabla_grafica_delta']
        return df_fig2, df_fig3

    def __get_figure4_5(self, raw_data):

        def common_step(df):
            return (df.rename(columns={'prom':'Prom', 'q_sup':'Q. Sup', 'q_inf':'Q. Inf'})
                      .reset_index().rename(columns={'fecha':'date'}))

        df_fig4 = common_step(raw_data['tabla_grafica_costo_marginal_cb'])
        df_fig5 = common_step(raw_data['tabla_grafica_costo_marginal_pr'])

        return df_fig4, df_fig5

    def __get_figure6(self, raw_data):
        df_fig6 = (raw_data['tabla_generacion_grafica_mensual'].reset_index()
                                                               .rename(columns={'fecha':'date', 'valor':'value'}))
        return df_fig6


class OperatingProfitDataWriter(object):

    def __init__(self):
        super(OperatingProfitDataWriter, self).__init__

    def write_data(self, opc, path_name):

        # Create empty folder, here we gonna save xlsx files and svg figures
        temporal_folder = path_name.split('.')[0]
        os.makedirs(temporal_folder)

        # Write data in xlsx files
        self.__write_results(opc, temporal_folder)
        self.__write_graphics_data(opc, temporal_folder)
        self.__write_additional_data(opc, temporal_folder)
        self.__write_figures(opc, temporal_folder)

        # Save all in a .zip and delete temporal folder
        shutil.make_archive(temporal_folder, 'zip', temporal_folder)
        shutil.rmtree(temporal_folder)

    @staticmethod
    def __write_results(opc, temporal_folder):

        # Write results tables in a xlsx file
        filename = 'resultados.xlsx'
        excel_writer = pd.ExcelWriter(os.path.join(temporal_folder, filename), engine="xlsxwriter")

        opc.tables['vpn'].to_excel(excel_writer, 
                                   sheet_name='VPN', 
                                   index=False)

        opc.tables['annuity_benefits'].to_excel(excel_writer, 
                                                sheet_name='Anualidad beneficios', 
                                                index=False)

        opc.tables['average_marginal_cost'].to_excel(excel_writer, 
                                                     sheet_name='Costo Marginal Promedio', 
                                                     index=False)

        opc.tables['generation_plant'].to_excel(excel_writer, 
                                                sheet_name='Generación planta', 
                                                index=False)

        opc.metadata['tasas_reconocidas'].to_excel(excel_writer, 
                                                   sheet_name='Tasas reconocidas', 
                                                   index=True)

        excel_writer.save()        

    @staticmethod
    def __write_graphics_data(opc, temporal_folder):

        # Write data from graphics in a xlsx file
        filename = 'datos_graficas.xlsx'
        excel_writer = pd.ExcelWriter(os.path.join(temporal_folder, filename), engine="xlsxwriter")

        opc.graphics['average_profits_per_demand_block'].index = opc.metadata['month_list']
        opc.graphics['average_delta_marginal_cost_per_block_of_demand'].index = opc.metadata['month_list']

        opc.graphics['histogram_of_operating_profit_graph'].to_excel(excel_writer, 
                            sheet_name='Histograma', 
                            index=False)

        opc.graphics['histogram_of_operating_profit_annotation'].to_excel(excel_writer, 
                            sheet_name='Estadisticas histograma', 
                            index=False)

        opc.graphics['average_profits_per_demand_block'].to_excel(excel_writer, 
                            sheet_name='Prom de Benef Bloq dem', 
                            index=True)

        opc.graphics['average_delta_marginal_cost_per_block_of_demand'].to_excel(excel_writer, 
                            sheet_name='Prm Delt cost marg Bloq dem', 
                            index=True)

        opc.graphics['marginal_cost_without_project'].to_excel(excel_writer, 
                            sheet_name='Costo marginal - Sin proyecto', 
                            index=True)

        opc.graphics['marginal_cost_with_project'].to_excel(excel_writer, 
                            sheet_name='Costo marginal - Con proyecto', 
                            index=True)

        opc.graphics['generation_plant'].to_excel(excel_writer, 
                            sheet_name='Gen mensual planta proy', 
                            index=True)

        excel_writer.save()     
    
    def __write_additional_data(self, opc, temporal_folder):

        # Write additional data wished by engineers in a xlsx file
        filename = 'datos_adicionales.xlsx'
        excel_writer = pd.ExcelWriter(os.path.join(temporal_folder, filename), engine="xlsxwriter")

        # Convert to other format wished by engineers
        df_ben_alt1_mes_trans = self.__tranpose_df_profits(opc.metadata['df_ben_alt1_mes'])
        df_ben_alt1_año_trans = self.__tranpose_df_profits(opc.metadata['df_ben_alt1_año'])

        df_ben_alt1_mes_trans.to_excel(excel_writer, sheet_name='Beneficios mensuales', index=True)
        df_ben_alt1_año_trans.to_excel(excel_writer, sheet_name='Beneficios anuales', index=True)

        excel_writer.save()

    def __tranpose_df_profits(self, df_beneficios):
        """
            Transpone la df para que quede en el siguiente formato

                  serie1 serie2 serie3 ... serieN
            fecha1
            fecha2
            fecha3
            ...
            fechaN

        """

        df_beneficios.reset_index(inplace=True, drop=False)

        fechas = df_beneficios['fecha'].unique()
        series = df_beneficios['serie'].unique()

        matriz_valores = self.__transpose(fechas, series, df_beneficios['valor'].values)

        df = pd.DataFrame(matriz_valores, index=fechas, columns=series)

        return df

    @staticmethod
    def __transpose(fechas, series, valores):

        # Se inicializan los datos que tendra la df_final con el numero de filas que tendra
        # tendra 6 columnas debido a que sus columnas seran ['fecha', 'bloque', 'serie', 'id_bd', 'ubicacion', 'valor']
        matriz_final = np.full((len(fechas), len(series)), np.nan, dtype=np.float64)

        # Counter usado para iterar sobre cada fila de la df_final
        counter = 0

        for i in range(len(fechas)):
            for s in series:

                matriz_final[i][s-1] = valores[counter]
                counter += 1


        return matriz_final

    def __write_figures(self, opc, temporal_folder):
        pass

    def __figure1(self, opc, temporal_folder):
        pass

    def __figure2(self, opc, temporal_folder):

        dct_colores = {1: 'rgb(83, 127, 181)',
                       2: 'rgb(56, 165, 44)',
                       3: 'rgb(4, 95, 165)',
                       4: 'rgb(135, 98, 156)',
                       5: 'rgb(73, 170, 195)'
                       }


        figure_2 = go.Figure(data=[go.Bar(name=f'Bloque {i}', x=lista_meses, y=datos['tabla_grafica_beneficios'][i], marker_color=dct_colores[i]) 
                                for i in datos['tabla_grafica_beneficios'].columns]
                            )

        # Change the bar mode
        figure_2.update_layout(barmode='group', 
                                # title_text='Promedio de Beneficios por Bloque de demada [Miles de Millones de COP]',
                                xaxis={"title": "Mes",
                                       "autorange": True,
                                       "type": "category",
                                       'showline':True, 'linewidth':1, 'linecolor':'black', 'mirror':False,
                                       'gridcolor': 'white'},                            
                                yaxis={"title": 'Miles de Millones de COP',
                                        'showline':True, 
                                        'linewidth':0.5, 
                                        'linecolor':'black', 
                                        'gridcolor': '#f3f4f3'},
                                paper_bgcolor='white',
                                plot_bgcolor='white',
                                title_text='Promedio de Beneficios por Bloque de demanda',
                                title_x=0.5,
                                margin=margin,
                                hovermode="closest",
                                legend={
                                    "x": -0.0228945952895,
                                    "y": -0.189563896463,
                                    "orientation": "h",
                                    "yanchor": "top",
                                },                                                
                                font={"family": 'Arial', "size": 12})

        return figure_2

    def __figure3(self, opc, temporal_folder):

        dct_colores = {1: 'rgb(83, 127, 181)',
                       2: 'rgb(56, 165, 44)',
                       3: 'rgb(4, 95, 165)',
                       4: 'rgb(135, 98, 156)',
                       5: 'rgb(73, 170, 195)'
                       }


        figure_3 = go.Figure(data=[go.Bar(name=f'Bloque {i}', x=lista_meses, y=datos['tabla_grafica_delta'][i], marker_color=dct_colores[i]) 
                                for i in datos['tabla_grafica_delta'].columns]
                            )

        # Change the bar mode
        figure_3.update_layout(barmode='group', 
                                # title_text='Promedio Delta costo marginal por Bloque de demada [COP/kWh]',
                                xaxis={"title": "Mes",
                                       "autorange": True,
                                       "type": "category",
                                       'showline':True, 'linewidth':1, 'linecolor':'black', 'mirror':False,
                                       'gridcolor': 'white'},                            
                                yaxis={"title": 'COP/kWh',
                                        'showline':True, 
                                        'linewidth':0.5, 
                                        'linecolor':'black', 
                                        'gridcolor': '#f3f4f3'},
                                paper_bgcolor='white',
                                plot_bgcolor='white',
                                title_text='Promedio Delta costo marginal por Bloque de demanda',
                                title_x=0.5,
                                margin=margin,
                                hovermode="closest",
                                legend={
                                    "x": -0.0228945952895,
                                    "y": -0.189563896463,
                                    "orientation": "h",
                                    "yanchor": "top",
                                },                                                           
                                font={"family": 'Arial', "size": 12}                           
                           )
        return figure_3

    def __figure4(self, opc, temporal_folder):

        datos['tabla_grafica_costo_marginal_cb'].rename(columns={'prom':'Prom', 'q_sup':'Q. Sup', 'q_inf':'Q. Inf'}, inplace=True)
        x = datos['tabla_grafica_costo_marginal_cb'].index

        dct_colores = {'Prom':'#0261A1', 'Q. Sup':'#ED7D31', 'Q. Inf':'#38A52B'}

        figure_4 = go.Figure(data=[go.Scatter(name=i, x=x, y=datos['tabla_grafica_costo_marginal_cb'][i], marker_color=dct_colores[i]) 
                                for i in datos['tabla_grafica_costo_marginal_cb'].columns]
                            )

        figure_4.update_layout(barmode='group', 
                                # title_text='Promedio Delta costo marginal por Bloque de demada [COP/kWh]',
                                xaxis={"title": "Año",
                                       "autorange": True,
                                       'showline':True, 'linewidth':1, 'linecolor':'black', 'mirror':False,
                                       'gridcolor': 'white'},                            
                                yaxis={"title": 'USD/MWh',
                                        'showline':True, 
                                        'linewidth':0.5, 
                                        'linecolor':'black', 
                                        'gridcolor': '#f3f4f3'},
                                paper_bgcolor='white',
                                plot_bgcolor='white',
                                title_text='Costo marginal - Sin proyecto',
                                title_x=0.5,
                                margin=margin,
                                hovermode="closest",
                                legend={
                                    "x": -0.0228945952895,
                                    "y": -0.189563896463,
                                    "orientation": "h",
                                    "yanchor": "top",
                                },                                                           
                                font={"family": 'Arial', "size": 12}                           
                               )


        figure_4.update_xaxes(
            tickangle = -90,
            dtick = "M6",  
            tickformat= "%m/%Y"
        )

        return figure_4

    def __figure5(self, opc, temporal_folder):

        datos['tabla_grafica_costo_marginal_pr'].rename(columns={'prom':'Prom', 'q_sup':'Q. Sup', 'q_inf':'Q. Inf'}, inplace=True)
        x = datos['tabla_grafica_costo_marginal_cb'].index

        dct_colores = {'Prom':'#0261A1', 'Q. Sup':'#ED7D31', 'Q. Inf':'#38A52B'}

        figure_5 = go.Figure(data=[go.Scatter(name=i, x=x, y=datos['tabla_grafica_costo_marginal_pr'][i], marker_color=dct_colores[i])
                                for i in datos['tabla_grafica_costo_marginal_pr'].columns]
                            )

        figure_5.update_layout(barmode='group',
                                # title_text='Promedio Delta costo marginal por Bloque de demada [COP/kWh]',
                                xaxis={"title": "Año",
                                       "autorange": True,
                                       'showline':True, 'linewidth':1, 'linecolor':'black', 'mirror':False,
                                       'gridcolor': 'white'},
                                yaxis={"title": 'USD/MWh',
                                        'showline':True,
                                        'linewidth':0.5,
                                        'linecolor':'black',
                                        'gridcolor': '#f3f4f3'},
                                paper_bgcolor='white',
                                plot_bgcolor='white',
                                title_text='Costo marginal - Con proyecto',
                                title_x=0.5,
                                margin=margin,
                                hovermode="closest",
                                legend={
                                    "x": -0.0228945952895,
                                    "y": -0.189563896463,
                                    "orientation": "h",
                                    "yanchor": "top",
                                },
                                font={"family": 'Arial', "size": 12}
                               )

        figure_5.update_xaxes(
            tickangle = -90,
            dtick = "M6",
            tickformat= "%m/%Y"
        )   

        return figure_5                               

    def __figure6(self, opc, temporal_folder):

        x = datos['tabla_generacion_grafica_mensual'].index
        figure_6 = go.Figure(data=[go.Scatter(name=i, x=x, y=datos['tabla_generacion_grafica_mensual'][i], marker_color='#0261A1') 
                                for i in datos['tabla_generacion_grafica_mensual'].columns]
                            )

        figure_6.update_layout(barmode='group', 
                                # title_text='Promedio Delta costo marginal por Bloque de demada [COP/kWh]',
                                xaxis={"title": "Año",
                                       "autorange": True,
                                       'showline':True, 'linewidth':1, 'linecolor':'black', 'mirror':False,
                                       'gridcolor': 'white'},
                                yaxis={"title": 'GWh',
                                        'showline':True, 
                                        'linewidth':0.5, 
                                        'linecolor':'black', 
                                        'gridcolor': '#f3f4f3'},
                                paper_bgcolor='white',
                                plot_bgcolor='white',
                                margin=margin,
                                title_text=f'Generación planta {planta_proyecto}',
                                title_x=0.5,
                                hovermode="closest",
                                legend={
                                    "x": -0.0228945952895,
                                    "y": -0.189563896463,
                                    "orientation": "h",
                                    "yanchor": "top",
                                },                         
                                font={"family": 'Arial', "size": 12}
                               )

        figure_6.update_xaxes(
            tickangle = -90,
            dtick = "M6",
            tickformat= "%m/%Y"
        )       

        return figure_6

    @staticmethod
    def __write_figure(self, pathname, figure):

        figure.write_image(os.path.join(folder_temporal, 'histograma.jpg'), 
                           engine='kaleido', 
                           width=600, 
                           height=350, 
                           scale=1)


# singleton patterns, only require a instance
operating_profit_calculator = OperatingProfitCalculator()
preparer_final_data_operating_profits = PreparerFinalDataOperatingProfits()





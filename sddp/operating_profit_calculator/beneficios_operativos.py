# from apps.sddp.data_processes import ordenador as pc
import numpy as np
import pandas as pd


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


# Calcular beneficios operativos
def calcular_beneficios_operativos(parametros, db_parameters):

    # Revisar que todos los parametros necesarios para los calculos hayan sido ingresados
    USDCOP                  = parametros['USDCOP']
    # AÑO_INICIO_SIMULACION   = parametros['AÑO_INICIO_SIMULACION']
    FECHA_ENTRADA_OPERACION = pd.Timestamp(parametros['FECHA_ENTRADA_OPERACION'])
    FECHA_LIMITE_OPERACION  = pd.Timestamp(parametros['FECHA_LIMITE_OPERACION'])
    FACTOR_DEMANDA          = parametros['FACTOR_DEMANDA']
    ID_BD_CASO_BASE         = parametros['ID_BD_CASO_BASE']
    ID_BD_PROYECTO          = parametros['ID_BD_PROYECTO']     
    DF_TASAS_RECONOCIDAS    = parametros['DF_TASAS_RECONOCIDAS']
    ID_PROYECTO             = parametros['ID_PROYECTO']
    PLANTA_PROYECTO         = parametros['PLANTA_PROYECTO']


    # Calcular la tasa a emplear:
    DF_TASAS_RECONOCIDAS['Tasa reconocida'] = DF_TASAS_RECONOCIDAS['Tasa reconocida'].astype(np.float64)
    DF_TASAS_RECONOCIDAS['Año'] = DF_TASAS_RECONOCIDAS['Año'].astype(np.float64)
    print('DF_TASAS_RECONOCIDAS_ antes')
    print(DF_TASAS_RECONOCIDAS)
    DF_TASAS_RECONOCIDAS.set_index(['Año'], inplace=True)
    DF_TASAS_RECONOCIDAS.sort_index(inplace=True)
    print('DF_TASAS_RECONOCIDAS_ despues')
    print(DF_TASAS_RECONOCIDAS)
    print()

    if FECHA_ENTRADA_OPERACION.year in DF_TASAS_RECONOCIDAS.index:
        TASA_RETORNO = DF_TASAS_RECONOCIDAS.loc[FECHA_ENTRADA_OPERACION.year, 'Tasa reconocida']
    else:
        TASA_RETORNO = DF_TASAS_RECONOCIDAS.iloc[-1, 0]

    # print('TASA_RETORNO')
    # print(TASA_RETORNO)
    # print()

    TASA = (1+TASA_RETORNO)**(1/12) - 1


    AÑO_INICIO_SIMULACION = DF_TASAS_RECONOCIDAS.index[0]


    # Diccionario donde se almacenaran todos los datos que se van a entregar
    datos_entrega = dict()

    # Obtener datos requeridos de la base de datos -------------------------------------------------------------------------
    # Obtener los costos marginales del caso base y del proyecto 
    #   Se sabe que se necesita el costo marginal de la bd1 (Caso base) y bd2 (Proyecto)
    df_cmg_caso_base = db_parameters['cmg_base_case']# pc.obtener_tabla_variable_bd('sddp.costo_marginal_demanda', ID_BD_CASO_BASE)
    df_cmg_proyecto  = db_parameters['cmg_proj']# pc.obtener_tabla_variable_bd('sddp.costo_marginal_demanda', ID_BD_PROYECTO)
    #   dfs de pesos por bloque para ambas bases de datos
    print('dfs de pesos por bloque para ambas bases de datos')
    # print(pc.obtener_tabla_variable_bd('sddp.pesos_bloques', ID_BD_CASO_BASE))
    # print(pc.obtener_tabla_variable_bd('sddp.pesos_bloques', ID_BD_PROYECTO))
    df_pb_caso_base = db_parameters['weights']# pc.obtener_tabla_variable_bd('sddp.pesos_bloques', ID_BD_CASO_BASE).set_index(1)
    df_pb_proyecto  = db_parameters['weights']# pc.obtener_tabla_variable_bd('sddp.pesos_bloques', ID_BD_PROYECTO).set_index(1)

    # print('df_cmg_caso_base, ID_BD_PROYECTO: ', ID_BD_CASO_BASE)
    # print(df_cmg_caso_base)
    #   Colocar como indices las columnas de fecha, bloque y serie, eliminar columna de id_bd
    # del df_cmg_caso_base[3]
    # del df_cmg_proyecto[3]
    # nuevos_nombres = {0:'fecha',
    #                   1:'bloque',
    #                   2:'serie',
    #                   4:'valor'}
    # df_cmg_caso_base.rename(columns=nuevos_nombres, inplace=True)
    # df_cmg_proyecto.rename(columns=nuevos_nombres, inplace=True)


    df_cmg_caso_base.set_index(['fecha', 'bloque', 'serie'], inplace=True)    
    df_cmg_proyecto.set_index(['fecha', 'bloque', 'serie'], inplace=True)     

    # Obtener demanda del proyecto
    print(ID_PROYECTO)
    df_demanda = db_parameters['demand']#pc.obtener_tabla_variable_proyecto('sddp.demanda', ID_PROYECTO)
    # del df_demanda[2]
    # nuevos_nombres = {0:'fecha',
    #                   1:'bloque',
    #                   3:'valor'}
    # df_demanda.rename(columns=nuevos_nombres, inplace=True)
    df_demanda['valor'] = df_demanda['valor']*FACTOR_DEMANDA

    print('DF_TASAS_RECONOCIDAS: ', DF_TASAS_RECONOCIDAS.dtypes)
    print(DF_TASAS_RECONOCIDAS.head())
    print()
    print('df_cmg_caso_base: ', df_cmg_caso_base.dtypes)
    print(df_cmg_caso_base.head())
    print()
    print('df_cmg_proyecto: ', df_cmg_proyecto.dtypes)
    print(df_cmg_proyecto.head())
    print()
    print('df_pb_caso_base: ', df_pb_caso_base.dtypes)
    print(df_pb_caso_base.head())
    print()
    print('df_pb_proyecto: ', df_pb_proyecto.dtypes)
    print(df_pb_proyecto.head())
    print()
    print('df_demanda: ', df_demanda.dtypes)
    print(df_demanda.head())
    print()

    # Calcular delta --------------------------------------------------------------------------------------------------------
    df_delta_alt1 = (df_cmg_caso_base - df_cmg_proyecto)  # Resta de costos marginales
    df_delta_alt1[ df_delta_alt1 <= 0 ] = 0               # Tomar solo los valores mayores a 0
    df_delta_alt1 = df_delta_alt1*USDCOP/1000             # Multiplicar por factor de divisa
    df_delta_alt1.sort_index(inplace=True)                # Ordenar Multiindex



    # Calcular ben_alt1_bloque -----------------------------------------------------------------------------------------------
    df_ben_alt1_bloque = df_delta_alt1.copy()             # Esta df se obtiene a partir del delta, por lo tanto usarla como inicio
    #   Para tomar solo las filas entre los rangos de operacion, se debe agregar la columna fecha como columna
    #   nuevamente, reiniciar el indice permite esto y su posterior toma de datos
    df_ben_alt1_bloque.reset_index(inplace=True)          
    df_ben_alt1_bloque = df_ben_alt1_bloque[(df_ben_alt1_bloque['fecha'] >= FECHA_ENTRADA_OPERACION) & 
                                            (df_ben_alt1_bloque['fecha'] <= FECHA_LIMITE_OPERACION)]

    df_demanda = df_demanda[(df_demanda['fecha'] >= FECHA_ENTRADA_OPERACION) & 
                            (df_demanda['fecha'] <= FECHA_LIMITE_OPERACION)]                                        


    #   Multiplicar por la df_demanda segun las fechas y bloques
    df_ben_alt1_bloque.set_index(['fecha', 'bloque'], inplace=True)
    df_demanda.set_index(['fecha', 'bloque'], inplace=True)

    #   Aplicar sort en el index para facilitar la multiplicacion entre ambas columnas de valor de las dataframes
    df_delta_alt1.sort_index(inplace=True)
    df_demanda.sort_index(inplace=True)


    df_ben_alt1_bloque['valor'] = df_ben_alt1_bloque['valor']*df_demanda['valor']


    # Calcular ben_alt1_mes -----------------------------------------------------------------------------------------------
    #   En esta df se unifican los valores de los bloques de cada mes, en un unico valor correspondiente a mes en que
    #   se encuentran los bloques por medio de una sumatoria
    df_ben_alt1_mes = df_ben_alt1_bloque.copy()          # Esta df se obtiene a partir de df_ben_alt1_bloque, por lo tanto usarla como inicio
    df_ben_alt1_mes.set_index('serie', append=True, inplace=True)

    #   Aplicar la sumatoria requerida para obtener la df requerida
    df_ben_alt1_mes = df_ben_alt1_mes.groupby(level=['fecha', 'serie']).sum()


    # Calcular VPN mensual ------------------------------------------------------------------------------------------------
    df_vpn_mes = df_ben_alt1_mes.copy()            # Esta df se obtiene a partir de df_ben_alt1_mes, por lo tanto usarla como inicio

    #   Seleccionar y calular la tasa a usar en el calculo
    df_vpn_mes = df_vpn_mes.groupby(level=['serie']).agg(lambda x: vna(TASA, x))/1000  # LINEA QUE DA LIGERAMENTE DIFERENTE, ACLARAR

    #   RESULTADOS DE PESTAÑA df_ben_alt1_mes: ESTADISITICAS DESCRIPTIVAS
    minimo  = df_vpn_mes['valor'].min()
    per_05  = df_vpn_mes['valor'].quantile(.05)
    mediana = df_vpn_mes['valor'].median()
    per_95  = df_vpn_mes['valor'].quantile(.95)
    maximo  = df_vpn_mes['valor'].max()


    # Calcular Ben_alt1_año ------------------------------------------------------------------------------------------------
    df_ben_alt1_año = df_ben_alt1_mes.copy()    # Esta df se obtiene a partir de df_ben_alt1_mes, por lo tanto usarla como inicio

    def using_Grouper(df):
        # Tomado de:
        # https://stackoverflow.com/questions/15799162/resampling-within-a-pandas-multiindex
        # Solucion mas veloz en comparacion con otras 2 expuestas
        level_values = df.index.get_level_values
        return (df.groupby([pd.Grouper(freq='Y', level=0)]+[level_values(1)]).sum())

    # Aplicar Resample a un año sin modificar el segundo indice que corresponde a "series"
    df_ben_alt1_año = using_Grouper(df_ben_alt1_año)


    # Calcular VPN anual ------------------------------------------------------------------------------------------------
    #   A diferencia de la del mes, primero se calcula la del ultimo año y se utilizan estos datos 
    #   para ir calculando las de años anteriores
    # df_vpn_anual = pd.DataFrame(index=DF_TASAS_RECONOCIDAS.index, columns=list(set(df_ben_alt1_año.index.get_level_values(1))))
    df_vpn_anual = pd.DataFrame(index=list(set(df_ben_alt1_año.index.get_level_values(1))), columns=DF_TASAS_RECONOCIDAS.index)


    #   Calcular VPN del ultimo año
    ultima_tasa_reconocida = DF_TASAS_RECONOCIDAS.iloc[-1, 0]


    #   Calcular desfase de años entre el inicio de los datos de la simulacion y la ultima tasa reconocida
    año_inicio_datos    = int(str(df_ben_alt1_año.index.get_level_values(0)[0])[:4])
    año_ultima_tasa_rec = DF_TASAS_RECONOCIDAS.index[-1]
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
        tasa_año = DF_TASAS_RECONOCIDAS.iloc[i, 0]

        # Calcular vpn para el año de la iteracion
        df_vpn_anual.iloc[:, i] = arr_vpn_año + df_vpn_anual.loc[:, i_año_siguiente].values/(1+tasa_año)

    # Division por 1000 que se aplica en el archivo de excel donde esta el ejemplo de beneficios operativos
    df_vpn_anual = df_vpn_anual/1000


    # Calcular estadisticas descriptivas para el primer año de simulacion
    # estos resultados se usan mas adelante, por eso se ponen en una serie
    #   PERCENTILES SON CALCULADOS DE FORMA EXTRAÑA AQUI, DIFIEREN DEL CALCULADO POR PANDAS, AQUI
    #   ARROJAN UN VALOR QUE SE ENCUENTRA EN la df_vpn_anual
    lista_valores_vpn_año_inicio = list(df_vpn_anual[AÑO_INICIO_SIMULACION].values)
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


    estadisticas_descriptivas_vpn_anual_primer_año['i_per_05']  = list(df_vpn_anual[df_vpn_anual[AÑO_INICIO_SIMULACION] == estadisticas_descriptivas_vpn_anual_primer_año['per_05']].index)[0]
    estadisticas_descriptivas_vpn_anual_primer_año['i_mediana'] = list(df_vpn_anual[df_vpn_anual[AÑO_INICIO_SIMULACION] == estadisticas_descriptivas_vpn_anual_primer_año['mediana']].index)[0]
    estadisticas_descriptivas_vpn_anual_primer_año['i_per_95']  = list(df_vpn_anual[df_vpn_anual[AÑO_INICIO_SIMULACION] == estadisticas_descriptivas_vpn_anual_primer_año['per_95']].index)[0]

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
        df_estadisticas_grafica_bel_alt1_año.loc[i, 'can_menores'] = len(df_vpn_anual[df_vpn_anual[AÑO_INICIO_SIMULACION] < df_estadisticas_grafica_bel_alt1_año.loc[i, 'clase']])
        

    for i in range(2, 18):    
        df_estadisticas_grafica_bel_alt1_año.loc[i, 'frecuencia'] = df_estadisticas_grafica_bel_alt1_año.loc[i, 'can_menores'] - df_estadisticas_grafica_bel_alt1_año.loc[i-1, 'can_menores']

    for i in range(2, 18):    
        df_estadisticas_grafica_bel_alt1_año.loc[i, '%'] = df_estadisticas_grafica_bel_alt1_año.loc[i, 'frecuencia']/df_estadisticas_grafica_bel_alt1_año['frecuencia'].sum()

    for i in range(2, 18):    
        df_estadisticas_grafica_bel_alt1_año.loc[i, '%_acumulado'] = df_estadisticas_grafica_bel_alt1_año.loc[:i, '%'].sum()*100

    #   Agregar tabla de graficas a datos para entregar
    datos_entrega['df_estadisticas_grafica_bel_alt1_año']           = df_estadisticas_grafica_bel_alt1_año
    datos_entrega['estadisticas_descriptivas_vpn_anual_primer_año'] = estadisticas_descriptivas_vpn_anual_primer_año

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
    tabla_si = pd.DataFrame(index=DF_TASAS_RECONOCIDAS.index, columns=('05PSS', 'Mediana', '95PSS'))

    tabla_si.iloc[-1, 0] = vna(DF_TASAS_RECONOCIDAS.iloc[-1, 0], tabla_etapas_est_desc['05PSS'], desfase_vna)
    tabla_si.iloc[-1, 1] = vna(DF_TASAS_RECONOCIDAS.iloc[-1, 0], tabla_etapas_est_desc['Mediana'], desfase_vna)
    tabla_si.iloc[-1, 2] = vna(DF_TASAS_RECONOCIDAS.iloc[-1, 0], tabla_etapas_est_desc['95PSS'], desfase_vna)

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
        tasa_año = DF_TASAS_RECONOCIDAS.loc[i_año_actual, 'Tasa reconocida']

        # Calcular vpn para el año de la iteracion
        tabla_si.loc[i_año_actual, '05PSS']   = arr_eed_05 + tabla_si.at[i_año_siguiente, '05PSS']/(1+tasa_año)
        tabla_si.loc[i_año_actual, 'Mediana'] = arr_eed_md + tabla_si.at[i_año_siguiente, 'Mediana']/(1+tasa_año)
        tabla_si.loc[i_año_actual, '95PSS']   = arr_eed_95 + tabla_si.at[i_año_siguiente, '95PSS']/(1+tasa_año)


    tabla_si = tabla_si/1000

    #   LA TABLA DE ETAPA, CUAL ES LA ETAPA QUE SE DEBE TOMAR? SOLO CORRESPONDE A UNA FILA DE LA TABLA_SI
    datos_entrega['tabla1_anualidad_beneficios'] = tabla_si

    datos_entrega['tabla2_anualidad_beneficios'] = tabla_etapas_est_desc


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
    datos_entrega['tabla_grafica_beneficios'] = tabla_grafica_beneficios

    # Calcular Consolidado de Delta ------------------------------------------------------------------------------------------------

    # Calcular tabla para graficar directamente para todas las series sin necesidad de una tabla intermedia como en la muestra
    # de los beneficios operativos
    #     Inicializar tabla de datos de promedios de consolidados beneficios
    #                                             mes                      bloque
    tabla_grafica_delta = pd.DataFrame(index=np.arange(1,13), columns=np.arange(1,6)).astype(np.float64)

    df_delta_alt1 = df_delta_alt1[(FECHA_ENTRADA_OPERACION <= df_delta_alt1.index.get_level_values(0)) &
                                  (FECHA_LIMITE_OPERACION >= df_delta_alt1.index.get_level_values(0))]


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
    datos_entrega['tabla_grafica_delta'] = tabla_grafica_delta
    
    # ELEMENTOS DE OTROS ARCHIVOS --------------------------------------------------------------------------------------------------
    # Calcular grafica de costo marginal sin y con proyecto ------------------------------------------------------------------------

    #   Funciones usadas en los groupby
    def quartil_sddp(k, x):
        # funcion de ayuda para los cuartiles calculados como en el sddp,
        # donde se toma el kesimo valor menor, que en este caso es k

        x = np.sort(x.values.T)
        return  x[k]

    def aplicar_pesos(df_pesos, x):
        # Aplicar pesos correspondientes a la base de datos a los bloques

        pesos = df_pesos['weight'].values
        x = np.sum(x*pesos)/np.sum(pesos)

        return  x          


    #   Si queres saber porque el "-1", preguntale a excel y el como toma el 5to menor y mayor de una lista, y la mediana
    i_05 = round(cantidad_simulaciones*0.05) - 1
    i_95 = round(cantidad_simulaciones*0.95)

    tabla_costo_marginal_cb = df_cmg_caso_base.copy()
    tabla_costo_marginal_pr = df_cmg_proyecto.copy()

    #   __________________________________________________________________________________________________________________________
    #   Calcular Tabla para costo marginal para el caso base _____________________________________________________________________
    #   __________________________________________________________________________________________________________________________
    tabla_costo_marginal_cb = tabla_costo_marginal_cb.groupby(level=['fecha', 'bloque']).mean()
    tabla_costo_marginal_cb.rename(columns={'valor': 'prom'}, inplace=True)


    # tabla_costo_marginal_cb['q_sup2'] = df_cmg_caso_base.groupby(level=['fecha', 'bloque']).quantile(0.95)
    tabla_costo_marginal_cb['q_sup'] = df_cmg_caso_base.groupby(level=['fecha', 'bloque']).agg(lambda x: quartil_sddp(i_95, x)).values
    tabla_costo_marginal_cb['q_inf'] = df_cmg_caso_base.groupby(level=['fecha', 'bloque']).agg(lambda x: quartil_sddp(i_05, x)).values


    # Aplicar pesos
    tabla_costo_marginal_cb_copia    = tabla_costo_marginal_cb.copy()    
    tabla_costo_marginal_cb          = pd.DataFrame(tabla_costo_marginal_cb_copia['prom'].groupby(level=['fecha']).agg(lambda x: aplicar_pesos(df_pb_caso_base, x)))
    tabla_costo_marginal_cb['q_sup'] = tabla_costo_marginal_cb_copia['q_sup'].groupby(level=['fecha']).agg(lambda x: aplicar_pesos(df_pb_caso_base, x))
    tabla_costo_marginal_cb['q_inf'] = tabla_costo_marginal_cb_copia['q_inf'].groupby(level=['fecha']).agg(lambda x: aplicar_pesos(df_pb_caso_base, x))


    #   __________________________________________________________________________________________________________________________
    #   Calcular Tabla para costo marginal para el proyecto ______________________________________________________________________
    #   __________________________________________________________________________________________________________________________
    tabla_costo_marginal_pr = tabla_costo_marginal_pr.groupby(level=['fecha', 'bloque']).mean()
    tabla_costo_marginal_pr.rename(columns={'valor': 'prom'}, inplace=True)


    #       Si queres saber porque el "-1", preguntale a excel y el como toma el 5to menor y mayor de una lista, y la mediana
    i_05 = round(cantidad_simulaciones*0.05) - 1
    i_95 = round(cantidad_simulaciones*0.95)


    # tabla_costo_marginal_cb['q_sup2'] = df_cmg_caso_base.groupby(level=['fecha', 'bloque']).quantile(0.95)
    tabla_costo_marginal_pr['q_sup'] = df_cmg_proyecto.groupby(level=['fecha', 'bloque']).agg(lambda x: quartil_sddp(i_95, x)).values
    tabla_costo_marginal_pr['q_inf'] = df_cmg_proyecto.groupby(level=['fecha', 'bloque']).agg(lambda x: quartil_sddp(i_05, x)).values


    # Aplicar pesos
    tabla_costo_marginal_pr_copia    = tabla_costo_marginal_pr.copy()    
    tabla_costo_marginal_pr          = pd.DataFrame(tabla_costo_marginal_pr_copia['prom'].groupby(level=['fecha']).agg(lambda x: aplicar_pesos(df_pb_proyecto, x)))
    tabla_costo_marginal_pr['q_sup'] = tabla_costo_marginal_pr_copia['q_sup'].groupby(level=['fecha']).agg(lambda x: aplicar_pesos(df_pb_proyecto, x))
    tabla_costo_marginal_pr['q_inf'] = tabla_costo_marginal_pr_copia['q_inf'].groupby(level=['fecha']).agg(lambda x: aplicar_pesos(df_pb_proyecto, x))


    datos_entrega['tabla_grafica_costo_marginal_cb'] = tabla_costo_marginal_cb
    datos_entrega['tabla_grafica_costo_marginal_pr'] = tabla_costo_marginal_pr

    # Calcular tabla_costo_marginal_promedio
    tabla_costo_marginal_promedio = tabla_costo_marginal_cb.groupby(tabla_costo_marginal_cb.index.year).mean()
    tabla_costo_marginal_promedio = pd.DataFrame(tabla_costo_marginal_promedio['prom'])
    tabla_costo_marginal_promedio.rename(columns={'prom': 'Sin proyecto'}, inplace=True)

    tabla_costo_marginal_promedio['Con proyecto'] = tabla_costo_marginal_pr.groupby(tabla_costo_marginal_pr.index.year).mean()['prom']

    datos_entrega['tabla_costo_marginal_promedio'] = tabla_costo_marginal_promedio.round(2)



    #   __________________________________________________________________________________________________________________________
    #   Calcular Tabla y Grafica de generacion con los datos de la planta del proyecto  __________________________________________
    #   __________________________________________________________________________________________________________________________

    # if PLANTA_PROYECTO is not None:
    if False:

        # Obtener datos de generacion sobre la planta del proyecto
        #   Consultar datos y tomar solo las columnas que necesitamos
        sentencia_consulta = f"WHERE planta='{PLANTA_PROYECTO}'"
        df_planta_proyecto = pc.obtener_tabla('sddp.generacion', sentencia=sentencia_consulta)
        dict_rename = {0:'fecha', 1:'bloque', 3:'serie', 6:'valor'}
        df_planta_proyecto.rename(columns=dict_rename, inplace=True)

        # Crear el multi-indice
        df_planta_proyecto = df_planta_proyecto[['fecha', 'bloque', 'serie', 'valor']]
        df_planta_proyecto.set_index(['fecha', 'bloque', 'serie'], inplace=True)   


        tabla_grafica_mensual = df_planta_proyecto.groupby(level=['fecha']).sum()/100

        # Calcular las 3 columnas de la tabla anual
        #   Columna de promedio
        tabla_anual           = (df_planta_proyecto.groupby(level=['fecha']).sum().groupby(tabla_costo_marginal_pr.index.year).sum()/100).round(1)

        #   Columna de quartil superior/inferior
        #       Si queres saber porque el "-1", preguntale a excel y el como toma el 5to menor y mayor de una lista, y la mediana
        i_05 = round(cantidad_simulaciones*0.05) - 1
        i_95 = round(cantidad_simulaciones*0.95) 

        df_intermedia = df_planta_proyecto.groupby([df_planta_proyecto.index.get_level_values(0), 'serie']).sum()

        q_sup = df_intermedia.groupby(df_intermedia.index.get_level_values(0)).agg(lambda x: quartil_sddp(i_95, x))
        tabla_anual['q_sup'] = q_sup.groupby(q_sup.index.year).sum().values

        q_inf = df_intermedia.groupby(df_intermedia.index.get_level_values(0)).agg(lambda x: quartil_sddp(i_05, x))
        tabla_anual['q_inf'] = q_inf.groupby(q_inf.index.year).sum().values    

        # Agregar tablas recien calculadas a los datos a entregar
        datos_entrega['tabla_generacion_grafica_mensual'] = tabla_grafica_mensual
        datos_entrega['tabla_generacion_anual']           = tabla_anual.round(1).rename(columns={'valor':'prom'}).reset_index()

    else:
        # Agregar tablas recien calculadas a los datos a entregar
        datos_entrega['tabla_generacion_grafica_mensual'] = pd.DataFrame(columns=['fecha', 'prom', 'q_sup', 'q_inf'])
        datos_entrega['tabla_generacion_anual']           = pd.DataFrame(columns=['fecha', 'prom', 'q_sup', 'q_inf'])


    # Datos que no se usan para graficar pero que son de interes y son adjuntados en lo descargado ------------------------------ 
    datos_entrega['df_ben_alt1_año'] = df_ben_alt1_año
    datos_entrega['df_ben_alt1_mes'] = df_ben_alt1_mes

    return datos_entrega






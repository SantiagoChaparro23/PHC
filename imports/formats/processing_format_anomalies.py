import sys

import numpy as np

np.set_printoptions(threshold=sys.maxsize)


def anomaly_1(data, headers):

    headers[1] = '0'

    return data, headers


def anomaly_2(data, headers):

    empty_arr = np.full((1, data.shape[0]), '')

    headers.insert(3, 'Combustible')

    new_data = np.insert(data, 3, empty_arr, axis=1)

    return new_data, headers    


class FormatAnomalyProcessor(object):
    """
        Selector from functions for format specific anomalies in files from xm
    """

    __MAP_URL2ANOMALY_FUNCTION = {

        'http://portalbissrs.xm.com.co/trpr/Histricos/Precios/Costo_Marginal_Despacho_Programado_(%24kwh)_2013.xlsx': anomaly_1,
        'http://portalbissrs.xm.com.co/oferta/Histricos/Generaci%C3%B3n/Generacion_(kWh)_2002.xlsx': anomaly_2,
        'http://portalbissrs.xm.com.co/oferta/Histricos/Generaci%C3%B3n/Generacion_(kWh)_2001.xlsx': anomaly_2,
        'http://portalbissrs.xm.com.co/oferta/Histricos/Generaci%C3%B3n/Generacion_(kWh)_2004.xlsx': anomaly_2,
        'http://portalbissrs.xm.com.co/oferta/Histricos/Generaci%C3%B3n/Generacion_(kWh)_2005.xlsx': anomaly_2
    }

    def __init__(self):
        pass

    def remove_anomaly(self, url, data, headers):
        """
            Apply processing if the file is among the registered anomalies in __MAP_URL2ANOMALY_FUNCTION
        """

        if url in self.__MAP_URL2ANOMALY_FUNCTION.keys():
            print('Fixing anomaly in ', url, ' with function: ', self.__MAP_URL2ANOMALY_FUNCTION[url].__name__)
            data, headers = self.__MAP_URL2ANOMALY_FUNCTION[url](data, headers)

        else:
            pass

        return data, headers
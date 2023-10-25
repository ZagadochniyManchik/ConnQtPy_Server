from decoder import *
import pickle


def parser(data):
    items_data = data.split(b'<END>')[:-1]
    method = pdecode(items_data[-1])
    data_for_method = pdecode(items_data[0])
    return method, data_for_method

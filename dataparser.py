from decoder import *
import pickle


# function to pars data into method and data for it and give it to handler
def parser(data):
    items_data = data.split(b'<END>')[:-1]
    method = pdecode(items_data[-1])
    data_for_method = pdecode(items_data[0])
    return method, data_for_method

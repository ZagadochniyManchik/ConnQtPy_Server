import pickle
# decoder and encoder using pickle


def pencode(data):
    return pickle.dumps(data)


def pdecode(data):
    return pickle.loads(data)


if __name__ == '__main__':
    ...
    # static = [1, 2, 3]
    # print(static)
    # static_encode = pencode([1, 2, 3])
    # print(static_encode)
    # static_decode = pdecode(static_encode)
    # print(static_decode)
    # print(f'{static} == {static_decode}: {static == static_decode}')
    # if static == static_decode:
    #     print('Test #1 complete')
    # else:
    #     print('Test #1 not complete')
    #     exit()
    # static_encode_for_send = static_encode + b'<END>' + pencode('<COUNT-NUMBERS>') + b'<END>'
    # print(static_encode_for_send)
    # items_static_encode_for_send = static_encode_for_send.split(b'<END>')[:-1]
    # print(items_static_encode_for_send)
    # method = pdecode(items_static_encode_for_send[-1])
    # data = pdecode(items_static_encode_for_send[0])
    # print(f"Method: {method}\nData: {data}")

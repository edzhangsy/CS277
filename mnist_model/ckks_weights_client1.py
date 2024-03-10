import tenseal as ts
import ast
import sys
import json
import pickle

# Specify the file path of the pickle file
pickle_file_path = '../mnist_model/ckks/context.pkl'

# Read the pickle file
with open(pickle_file_path, 'rb') as pickle_file:
    # server_context = pickle.load(pickle_file)
    server_context = pickle_file.read()

# print(server_context)
context = ts.context_from(server_context)

weight0 = []
bias0 = []
weight2 = []
bias2 = []

result0 = []
result1 = []
result2 = []
result3 = []

result_param = {
    0: result0,
    1: result1,
    2: result2,
    3: result3,
}

keys_list = ['linear_relu_stack.0.weight', 'linear_relu_stack.0.bias', 'linear_relu_stack.2.weight', 'linear_relu_stack.2.bias']

for count in range(len(keys_list)):
    with open('../mnist_model/state/torch_weights'+str(count)+'.json', 'r') as json_file:
        if count == 0:
            weight0 = ast.literal_eval(json_file.read())
        elif count == 1:
            bias0 = ast.literal_eval(json_file.read())
        elif count == 2:
            weight2 = ast.literal_eval(json_file.read())
        elif count == 3:
            bias2 = ast.literal_eval(json_file.read())

weight0_enc = ts.ckks_tensor(context, weight0)
bias0_enc = ts.ckks_tensor(context, bias0)
weight2_enc = ts.ckks_tensor(context, weight2)
bias2_enc = ts.ckks_tensor(context, bias2)

result_param[0] = weight0_enc.serialize()
result_param[1] = bias0_enc.serialize()
result_param[2]= weight2_enc.serialize()
result_param[3] = bias2_enc.serialize()

# Serialize data to bytes using pickle
# serialized_data_bytes = pickle.dumps(data_to_serialize)

# Now you can store or transmit serialized_data_bytes as bytes
# For example, if you want to save it to a file:
for count in range(len(keys_list)):
    with open('../mnist_model/ckks/ckks_weights'+str(count)+'.pkl', 'wb') as file:
        file.write(result_param[count])
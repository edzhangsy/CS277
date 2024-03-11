import tenseal as ts
import ast
import sys
import json
import pickle
from ckks_init import private_context

def decrypt(enc):
    return enc.decrypt().tolist()

def prepare_input_tensor(context: bytes, ckks_tensor: bytes) -> ts.CKKSTensor:
    #try:
    ctx = ts.context_from(context)
    enc_x = ts.ckks_tensor_from(ctx, ckks_tensor)
    #except:
    #    raise DeserializationError("cannot deserialize context or ckks_vector")
    #try:
    _ = ctx.galois_keys()
    #except:
    #    raise InvalidContext("the context doesn't hold galois keys")

    return enc_x

# Specify the file path of the pickle file
pickle_file_path = '../mnist_model/ckks/context.pkl'

# Read the pickle file
with open(pickle_file_path, 'rb') as pickle_file:
    # server_context = pickle.load(pickle_file)
    server_context = pickle_file.read()

# print(server_context)
context = ts.context_from(server_context)

weight0_c1 = []
bias0_c1 = []
weight2_c1 = []
bias2_c1 = []

weight0_c2 = []
bias0_c2 = []
weight2_c2 = []
bias2_c2 = []

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

###################### REDUNDANCY OF CKKS_WEIGHTS_CLIENT{i}.py
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

for count in range(len(keys_list)):
    with open('../mnist_model/ckks/ckks_weights'+str(count)+'.pkl', 'wb') as file:
        file.write(result_param[count])
########################################################################################
for count in range(len(keys_list)):
    with open('../mnist_model/state/torch_weights'+str(count+4)+'.json', 'r') as json_file:
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
    with open('../mnist_model/ckks/ckks_weights'+str(count+4)+'.pkl', 'wb') as file:
        file.write(result_param[count])
########################################################################################
for count in range(len(keys_list)):
    with open('../mnist_model/ckks/ckks_weights'+str(count)+'.pkl', 'rb') as pickle_file:
        if count == 0:
            weight0_c1 = pickle_file.read()
        elif count == 1:
            bias0_c1 = pickle_file.read()
        elif count == 2:
            weight2_c1 = pickle_file.read()
        elif count == 3:
            bias2_c1 = pickle_file.read()
            
for count in range(len(keys_list)):
    with open('../mnist_model/ckks/ckks_weights'+str(count+4)+'.pkl', 'rb') as pickle_file:
        if count == 0:
            weight0_c2 = pickle_file.read()
        elif count == 1:
            bias0_c2 = pickle_file.read()
        elif count == 2:
            weight2_c2 = pickle_file.read()
        elif count == 3:
            bias2_c2 = pickle_file.read()

weight0_enc_c1 = ts.ckks_tensor_from(private_context, weight0_c1)
bias0_enc_c1 = ts.ckks_tensor_from(private_context, bias0_c1)
weight2_enc_c1 = ts.ckks_tensor_from(private_context, weight2_c1)
bias2_enc_c1 = ts.ckks_tensor_from(private_context, bias2_c1)
weight0_enc_c2 = ts.ckks_tensor_from(private_context, weight0_c2)
bias0_enc_c2 = ts.ckks_tensor_from(private_context, bias0_c2)
weight2_enc_c2 = ts.ckks_tensor_from(private_context, weight2_c2)
bias2_enc_c2 = ts.ckks_tensor_from(private_context, bias2_c2)

result_param[0] = weight0_enc_c1 + weight0_enc_c2
result_param[0] = result_param[0] * 0.5
result_param[1] = bias0_enc_c1 + bias0_enc_c2
result_param[1] = result_param[1] * 0.5
result_param[2] = weight2_enc_c1 + weight2_enc_c2
result_param[2] = result_param[2] * 0.5
result_param[3] = bias2_enc_c1 + bias2_enc_c2
result_param[3] = result_param[3] * 0.5

for count in range(len(keys_list)):
    with open('../mnist_model/aggregate/ckks_weights'+str(count)+'.json', 'w') as json_file:
        json.dump(decrypt(result_param[count]), json_file)
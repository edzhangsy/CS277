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
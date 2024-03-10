import tenseal as ts
import ast
import sys
import json
import pickle

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

# Setup TenSEAL context
context = ts.context(
            ts.SCHEME_TYPE.CKKS,
            poly_modulus_degree=8192,
            coeff_mod_bit_sizes=[60, 40, 40, 60]
            #coeff_mod_bit_sizes=[40, 21, 21, 21, 21, 21, 21, 40]
          )
context.generate_galois_keys()
context.global_scale = 2**40
#context.global_scale = 2**21

# # Specify the file path of the pickle file
# pickle_file_path = '../mnist_model/ckks/sk.pkl'

# # Read the pickle file
# with open(pickle_file_path, 'rb') as pickle_file:
#     # server_context = pickle.load(pickle_file)
#     serialized_sk = pickle_file.read()
    
# # Specify the file path of the pickle file
# pickle_file_path = '../mnist_model/ckks/context.pkl'

# # Read the pickle file
# with open(pickle_file_path, 'rb') as pickle_file:
#     # server_context = pickle.load(pickle_file)
#     server_context = pickle_file.read()
    
# # Deserialize the secret key
# sk = ts.deserialize(serialized_sk)

# # print(server_context)
# context = ts.context_from(server_context)

# # Attach the secret key to the context
# context.create_ckks_context(sk)

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

weight0_enc_c1 = ts.ckks_tensor_from(context, weight0_c1)
bias0_enc_c1 = ts.ckks_tensor_from(context, bias0_c1)
weight2_enc_c1 = ts.ckks_tensor_from(context, weight2_c1)
bias2_enc_c1 = ts.ckks_tensor_from(context, bias2_c1)
weight0_enc_c2 = ts.ckks_tensor_from(context, weight0_c2)
bias0_enc_c2 = ts.ckks_tensor_from(context, bias0_c2)
weight2_enc_c2 = ts.ckks_tensor_from(context, weight2_c2)
bias2_enc_c2 = ts.ckks_tensor_from(context, bias2_c2)

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
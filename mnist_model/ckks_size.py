import tenseal as ts
import ast
import sys
import json
import torch

def decrypt(enc):
    return enc.decrypt().tolist()

def prepare_input_vector(context: bytes, ckks_vector: bytes) -> ts.CKKSVector:
    try:
        ctx = ts.context_from(context)
        enc_x = ts.ckks_vector_from(ctx, ckks_vector)
    except:
        raise DeserializationError("cannot deserialize context or ckks_vector")
    try:
        _ = ctx.galois_keys()
    except:
        raise InvalidContext("the context doesn't hold galois keys")

    return enc_x

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


context = ts.context(
            ts.SCHEME_TYPE.CKKS,
            poly_modulus_degree=8192,
            coeff_mod_bit_sizes=[60, 40, 40, 60]
            #coeff_mod_bit_sizes=[40, 21, 21, 21, 21, 21, 21, 40]
          )
context.generate_galois_keys()
context.global_scale = 2**40
#context.global_scale = 2**21

v1 = [0, 1, 2, 3, 4]
v2 = [4, 3, 2, 1, 0]
a1 = [1,1,1,1,1,1,1,1,1,1]

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
    with open('./state/torch_weights'+str(count)+'.json', 'r') as json_file:
        #print(json_file.read())
        #ast.literal_eval(json_file.read())
        if count == 0:
            weight0 = ast.literal_eval(json_file.read())
        elif count == 1:
            bias0 = ast.literal_eval(json_file.read())
        elif count == 2:
            weight2 = ast.literal_eval(json_file.read())
        elif count == 3:
            bias2 = ast.literal_eval(json_file.read())

# Convert it to a PyTorch tensor
plaintext_data = torch.tensor(bias0, dtype=torch.float32)

# Get the size in bytes of the PyTorch tensor
size_in_bytes = plaintext_data.element_size() * plaintext_data.nelement()

print("Size in bytes:", size_in_bytes)

bias0_enc = ts.ckks_tensor(context, bias0)
# Serialize the encrypted tensor to a bytearray
serialized_data = bias0_enc.serialize()

# Get the size in bytes of the serialized data
size_in_bytes = len(serialized_data)

print("Size in bytes:", size_in_bytes)
################################################################################
# Convert it to a PyTorch tensor
plaintext_data = torch.tensor(weight0, dtype=torch.float32)

# Get the size in bytes of the PyTorch tensor
size_in_bytes = plaintext_data.element_size() * plaintext_data.nelement()

print("Size in bytes:", size_in_bytes)

### Chuncking for Large Files

# weight0_enc = ts.ckks_tensor(context, weight0)
# # Serialize the encrypted tensor to a bytearray
# serialized_data = weight0_enc.serialize()

# protobuf_data = serialized_data
# # Split the serialized data into chunks (you can adjust the chunk size according to your needs)
# chunk_size = 1024  # Set your desired chunk size
# chunks = [protobuf_data[i:i + chunk_size] for i in range(0, len(protobuf_data), chunk_size)]

# # Deserialize each chunk and create a PyTorch tensor
# result_tensors = 0
# for chunk in chunks:
#     # chunk_tensor = ProtobufSerializer().deserialize(chunk)
#     # result_tensors.append(chunk_tensor)
#     result_tensors += len(chunk)

# print("Size in bytes:", result_tensors)

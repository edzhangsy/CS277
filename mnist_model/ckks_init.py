import tenseal as ts
import ast
import sys
import json
import pickle

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

# We prepare the context for the server, by making it public(we drop the secret key)
server_context = context.copy()
private_context = context.copy()
sk = context.secret_key()
# print(dir(sk))
# sk.data.save('./secret.txt')
# print(type(server_context))
# print(dir(sk.data.data))
# sk.data.load(server_context, './secret.txt')

server_context.make_context_public()

# Context and ciphertext serialization
server_context = server_context.serialize()
# Serialize data to bytes using pickle
# serialized_data_bytes = pickle.dumps(data_to_serialize)

# Now you can store or transmit serialized_data_bytes as bytes
# For example, if you want to save it to a file:
with open('../mnist_model/ckks/context.pkl', 'wb') as file:
    file.write(server_context)
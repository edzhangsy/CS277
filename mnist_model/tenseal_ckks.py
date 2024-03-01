import tenseal as ts
import ast
import sys
from torch.utils.data import Dataset
from json import JSONEncoder
import json

def decrypt(enc):
    return enc.decrypt().tolist()

class EncodeTensor(JSONEncoder,Dataset):
    def default(self, obj):
        if isinstance(obj, torch.Tensor):
            return obj.cpu().detach().numpy().tolist()
        return super(EncodeTensor, self).default(obj)

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

### Encryption
print(bias2)

weight0_encrypted = ts.ckks_tensor(context, weight0)
bias0_encrypted = ts.ckks_tensor(context, bias0)
weight2_encrypted = ts.ckks_tensor(context, weight2)
bias2_encrypted = ts.ckks_tensor(context, bias2)

result_param[0] = weight0_encrypted + weight0_encrypted
#print("Plain equivalent: {} * {}\nDecrypted result: {}.".format(weight0, weight0, decrypt(result0)))
#with open('./aggregate/ckks_weights0.json', 'w') as json_file:
#    json.dump(decrypt(result0), json_file)

result_param[1] = bias0_encrypted + bias0_encrypted
#print("Plain equivalent: {} * {}\nDecrypted result: {}.".format(bias0, bias0, decrypt(result1)))
#with open('./aggregate/ckks_weights1.json', 'w') as json_file:
#        json.dump(decrypt(result1), json_file)

result_param[2] = weight2_encrypted + weight2_encrypted
#print("Plain equivalent: {} * {}\nDecrypted result: {}.".format(weight2, weight2, decrypt(result2)))
#with open('./aggregate/ckks_weights2.json', 'w') as json_file:
#        json.dump(decrypt(result2), json_file)

result_param[3] = bias2_encrypted + bias2_encrypted
#print("Plain equivalent: {} * {}\nDecrypted result: {}.".format(bias2, bias2, decrypt(result3)))
#with open('./aggregate/ckks_weights3.json', 'w') as json_file:
#    json.dump(decrypt(result3), json_file)

a1_encrypted = ts.ckks_tensor(context, a1)
result = bias2_encrypted + bias2_encrypted
print("Plain equivalent: {} * {}\nDecrypted result: {}.".format(bias2, a1, decrypt(result)))

for count in range(len(keys_list)):
    with open('./aggregate/ckks_weights'+str(count)+'.json', 'w') as json_file:
        #json.dump(decrypt(result+str(count)), json_file,cls=EncodeTensor)
        json.dump(decrypt(result_param[count]), json_file)

# encrypted vectors
enc_v1 = ts.ckks_vector(context, v1)
enc_v2 = ts.ckks_vector(context, v2)

result = enc_v1 + enc_v2
print(result.decrypt()) # ~ [4, 4, 4, 4, 4]
print(type(result.decrypt()))

result = enc_v1.dot(enc_v2)
print(result.decrypt()) # ~ [10]

matrix = [
  [73, 0.5, 8],
  [81, -5, 66],
  [-100, -78, -2],
  [0, 9, 17],
  [69, 11 , 10],
]
result = enc_v1.matmul(matrix)
print(result.decrypt()) # ~ [157, -90, 153]


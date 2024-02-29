from seal import *
import numpy as np
import time
import sys
import ast

def print_vector(vector):
    print('[ ', end='')
    for i in range(0, 8):
        print(vector[i], end=', ')
    print('... ]')


def example_ckks_basics():
    parms = EncryptionParameters (scheme_type.ckks)
    poly_modulus_degree = 8192
    parms.set_poly_modulus_degree(poly_modulus_degree)
    parms.set_coeff_modulus(CoeffModulus.Create(poly_modulus_degree, [60, 40, 40, 60]))
    # parms.set_coeff_modulus(CoeffModulus.BFVDefault(poly_modulus_degree))
    # parms.set_plain_modulus(PlainModulus.Batching(poly_modulus_degree, 20))
    scale = pow(2.0, 40)
    context = SEALContext(parms)
    
    keygen = KeyGenerator(context)
    secret_key = keygen.secret_key()
    public_key = keygen.create_public_key()
    relin_keys = keygen.create_relin_keys()

    encryptor = Encryptor(context, public_key)
    evaluator = Evaluator(context)
    decryptor = Decryptor(context, secret_key)
    
    # CKKS Encoder
    ckks_encoder = CKKSEncoder(context)
    slot_count = ckks_encoder.slot_count()
    
    input_matrix = [0] * slot_count
    curr_point = 0
    step_size = 1.0 / (slot_count - 1)
    for i in range(slot_count):
        input_matrix.append(curr_point)
        curr_point += step_size

    # batch_encoder = BatchEncoder(context)
    # slot_count = batch_encoder.slot_count()
    # row_size = slot_count / 2
    # print(f'Plaintext matrix row size: {row_size}')

    # pod_matrix = [0] * slot_count
    # pod_matrix[0] = 1
    # pod_matrix[1] = 2
    # pod_matrix[2] = 3
    # pod_matrix[3] = 4
    plain_coeffVec = ckks_encoder.encode([3.141, 2, 3, 4, 4], scale)
    plain_coeff3 = ckks_encoder.encode(3.141, scale)
    plain_coeff1 = ckks_encoder.encode(0.4, scale)
    plain_coeff0 = ckks_encoder.encode(1.0, scale)
    plain_coeff8 = ckks_encoder.encode(0.125, scale)
    weight0 = 0
    bias0 = 0
    weight2 = 0
    bias2 = 0

    keys_list = ['linear_relu_stack.0.weight', 'linear_relu_stack.0.bias', 'linear_relu_stack.2.weight', 'linear_relu_stack.2.bias']

    for count in range(len(keys_list)):
        with open('../../CS277/mnist_model/state/torch_weights'+str(count)+'.json', 'r') as json_file:
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
    
    #weight0 = ckks_encoder.encode(weight0, scale)
    bias0 = ckks_encoder.encode(bias0, scale)
    #weight2 = ckks_encoder.encode(weight2, scale)
    bias2 = ckks_encoder.encode(bias2, scale)

    ### Encryption
    start = time.time()

    #weight0_encrypted = encryptor.encrypt(weight0)
    bias0_encrypted = encryptor.encrypt(bias0) 
    done = time.time()
    elapsed = done - start
    print(elapsed)
    bias0_encrypted = encryptor.encrypt(bias0)
    #weight2_encrypted = encryptor.encrypt(weight2)
    bias2_encrypted = encryptor.encrypt(bias2)
    x3_encrypted = encryptor.encrypt(plain_coeff3)
    x1_encrypted = encryptor.encrypt(plain_coeff1)
    x0_encrypted = encryptor.encrypt(plain_coeff0)
    x8_encrypted = encryptor.encrypt(plain_coeff8)
    vector_encrypted = encryptor.encrypt(plain_coeffVec)
    
    ### Addition
    print("Compute PI + 0.4 + 1.\n")
    encrypted_result = evaluator.add(x3_encrypted, x1_encrypted)
    encrypted_result = evaluator.add(x0_encrypted, encrypted_result)
    print(sys.getsizeof(encrypted_result))
    
    
    ### Multiplication
    encrypted_result = evaluator.multiply_plain(encrypted_result, plain_coeff8)
    # relin_keys = evaluator.relinearize_inplace(x8_encrypted)
    # x8_encrypted = evaluator.rescale_to_next_inplace(x8_encrypted)
    print(sys.getsizeof(encrypted_result))
    vec_result = evaluator.add(vector_encrypted, vector_encrypted)
    
    print("Expected Result: 4.541\n")
    ### Decryption
    start = time.time()
    
    decrypted_result = decryptor.decrypt(encrypted_result)
    done = time.time()
    elapsed = done - start
    print(elapsed)
    input_result = ckks_encoder.decode(decrypted_result)
    
    print_vector(input_result)
    print('Object Size Comparison: ')
    print(sys.getsizeof(x3_encrypted))
    print(sys.getsizeof(3.141))
    
    ### Vector
    print("Vector size: " + str(sys.getsizeof(vec_result)))
    
    decrypted_result = decryptor.decrypt(vec_result)
    input_result = ckks_encoder.decode(decrypted_result)
    
    print_vector(input_result)
    
    
    # x_8th = evaluator.square(x_4th)
    # print(f'size of x_8th: {x_8th.size()}')
    # evaluator.relinearize_inplace(x_8th, relin_keys)
    # evaluator.mod_switch_to_next_inplace(x_8th)
    # print(f'size of x_8th (after relinearization): { x_8th.size()}')
    # print(f'noise budget in x_8th (with modulus switching): {decryptor.invariant_noise_budget(x_8th)} bits')
    # decrypted_result = decryptor.decrypt(x_8th)
    # pod_result = batch_encoder.decode(decrypted_result)
    # print_vector(pod_result)

    # x_plain = batch_encoder.encode(pod_matrix)

    # x_encrypted = encryptor.encrypt(x_plain)
    # print(f'noise budget in freshly encrypted x: {decryptor.invariant_noise_budget(x_encrypted)}')
    # print('-'*50)

    # x_squared = evaluator.square(x_encrypted)
    # print(f'size of x_squared: {x_squared.size()}')
    # evaluator.relinearize_inplace(x_squared, relin_keys)
    # print(f'size of x_squared (after relinearization): {x_squared.size()}')
    # print(f'noise budget in x_squared: {decryptor.invariant_noise_budget(x_squared)} bits')
    # decrypted_result = decryptor.decrypt(x_squared)
    # pod_result = batch_encoder.decode(decrypted_result)
    # print_vector(pod_result)
    # print('-'*50)



if __name__ == "__main__":
    example_ckks_basics()

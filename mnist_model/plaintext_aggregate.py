import tenseal as ts
import ast
import sys
import json

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

result_param[0] = weight0
result_param[0] = [[element + element for element in sublist] for sublist in result_param[0]]
result_param[0] = [[element / 2 for element in sublist] for sublist in result_param[0]]

result_param[1] = bias0
result_param[1] = [element + element for element in result_param[1]]
result_param[1] = [element / 2 for element in result_param[1]]

result_param[2] = weight2
result_param[2] = [[element + element for element in sublist] for sublist in result_param[2]]
result_param[2] = [[element / 2 for element in sublist] for sublist in result_param[2]]

result_param[3] = bias2
result_param[3] = [element + element for element in result_param[3]]
result_param[3] = [element / 2 for element in result_param[3]]

for count in range(len(keys_list)):
    with open('../mnist_model/aggregate/plain_weights'+str(count)+'.json', 'w') as json_file:
        json.dump(result_param[count], json_file)



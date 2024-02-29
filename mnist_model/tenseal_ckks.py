import syft as sy
import torch
import syft.frameworks.tenseal as ts

hook = sy.TorchHook(th)

public_keys, secret_key = ts.generate_ckks_keys()

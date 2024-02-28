# Optional
sudo apt update
sudo apt-get install -y git build-essential cmake python3 python3-dev python3-pip

# Get the repository or download from the releases
git clone https://github.com/Huelse/SEAL-Python.git
cd SEAL-Python

# Install dependencies
pip3 install numpy pybind11

# Init the SEAL and pybind11
git submodule update --init --recursive
# Get the newest repositories (dev only)
# git submodule update --remote

# Build the SEAL lib
cd SEAL
cmake -S . -B build -DSEAL_USE_MSGSL=OFF -DSEAL_USE_ZLIB=OFF
cmake --build build
cd ..

# Run the setup.py
python3 setup.py build_ext -i

# Test
cp seal.*.so examples
cd examples
python3 4_bgv_basics.py

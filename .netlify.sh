python -m pip install --upgrade pip setuptools wheel
pip install -U tox
python setup.py build_ext --inplace
sudo apt install -y graphviz
tox -edocs

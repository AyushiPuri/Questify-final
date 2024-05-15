![Screenshot (8)](https://github.com/AyushiPuri/Questify-final/assets/142603987/6beb15fa-ec92-4d20-9c19-b3c238b6dc92)

### install these after installing miniconda

1. create environment
```shell
conda create -n py39 python=3.9
```

2. install llama-cpp
```shell
conda install -c conda-forge llama-cpp-python=0.2.24 -y
```

3. install remaining requirements
```shell
pip install -r requirements.txt
```

4. run streamlit
```
streamlit run app.py
```


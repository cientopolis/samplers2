# 1)Instalar Python: 
## Ubuntu 14.04 and 16.04
### Si estás usando ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)" 14.04 or 16.04, podés usar el PPA de Felix Krull' at https://launchpad.net/~deadsnakes/+archive/ubuntu/ppa:
#### sudo add-apt-repository ppa:deadsnakes/ppa
#### sudo apt-get update
#### sudo apt-get install python3.6
### Alternativamente, podés usar el PPA de J Fernyhough en https://launchpad.net/~jonathonf/+archive/ubuntu/python-3.6:

### sudo add-apt-repository ppa:jonathonf/python-3.6
### sudo apt-get update
### sudo apt-get install python3.6

## Ubuntu 16.10 and 17.04
### Si estás usando Ubuntu 16.10 o 17.04, entonces Python 3.6 está en el repositorio universal, por lo que podés correr directamente:

#### sudo apt-get update
#### sudo apt-get install python3.6

# 2)Instalar VirtualEnv
#### sudo pip install virtualenv

# 3)Crear virtualenv con version de python especifica
#### python3.6 -m venv Samplers2Env

# 4)Activar Virtual Env
#### Parado en el directorio donde se encuentra instalado:
#### source directorioVirtualEnv/bin/activate

# 5)Instalar librerías
#### Tener el virtual env activado y correr el siguiente comando:
#### pip install -r requirements.txt

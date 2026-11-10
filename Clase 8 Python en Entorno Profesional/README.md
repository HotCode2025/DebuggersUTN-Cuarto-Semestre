# Entorno Virtual en Python

<br> Comenzamos con el entorno virtual en Python, para ingresar al repo despues de un tiempo tuve que hacer lo siguiente,
abri la terminal de Ubuntu desde Windows como administrador:</br>

```sh
  mkdir py-project
  cd py-project
  git clone https://...
  ll
  cd pythonpop
  code .
  git branch #Solo esta la rama main
  git branch second #comenzamos a crear nuevas ramas
  git branch profe
  git branch ariel22
  git status #desde la rama main ya hay cambio para comitear
  git add .
  git commit -m"Agrego el archivo txt donde detallo cada parte de las clases"
  git push origin main #Surge un problema, debo crear un token para poder cargar cambios
  #Se debe entrar en Github setting - Developer setting - Personal access tokens - token classic
  #Se genera escribiendo las notas de que trabajo se va a tratar y se deben tildar cuanto tiempo de duracion tendra el token 
  # y tildar los permisos, generar y por ultimo copiar el token
  git pull origin main
  Usuario: ArielBetancud22
  password: accessToken #El que hemos creado y debemos guardar bien
  git config --global credential.helper store #Este comando es para guardar el token, pero habra que ingresarlo una vez y desde alli lo recordara.
 ```
  
  
  
# Archivo requirements.txt
<br>Vamos a ver este archivo, este gestiona todas las dependencias y en que versiones se necesitan,  vamos a dejar aqui los comandos para alguien logre contribuir en este proyecto, los comandos son los siguientes: </br>


```sh
git clone https://...  
cd app                                  
python3 -m venv env                     # Se debe crear el entorno virtual, este no se comparte desde GitHub
source env/bin/activate                 # Activamos el entorno en Linux 
venv\Scripts\activate                    # Activa el entorno en Windows
pip3 install -r requirements.txt        # Instala las dependencias el -r significa reutilizar
python3 main.py                         # Ejecutamos el programa
```

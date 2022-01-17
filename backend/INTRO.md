# Backend

## Paso 0. Instalar Python
Como primer paso debemos instalar python en su ultima version (3.9)
El proceso cambia si tenemos Windows o Python.
- [Instrucciones Windows](https://tutorial.djangogirls.org/es/installation/#instalar-python)
- [Instrucciones Linux](https://ubunlog.com/python-3-9-como-instalar-en-ubuntu-20-04/)

Una vez que instale, podés correr desde la terminal
```bash
> python3 -V
python3.9.5
```
Listo, ya tenemos python instalado.

## Paso 1. Instalar dependencias del proyecto
Python utiliza [pip](https://pip.pypa.io/en/stable/) para manejar las dependencias de un proyecto.
Por suerte viene instalado cuando instalamos python, asi que no hay que bajar nada extra.
Para comprobarlo, podemos hacer
```
> pip --version
pip 20.0.2 ...
```

### Qué es un virtualenv/entorno aislado?
Python tiene el concepto de [virtualenv](https://tutorial.djangogirls.org/es/django_installation/).
La idea es que cada proyecto tiene su entorno aislado donde instalar librerías
no afecta ninguna otra cosa del sistema y por ende ningún otro proyecto.
El problema más frecuente que resuelve es tener el proyecto A que necesita la versión
1 de la libreria X, y el proyecto B que solo funciona con la version 2.
Sin virtualenvs, no podríamos correr los dos proyectos en simultaneo.
Tendríamos que desinstalar y reinstalar una versión cada vez que cambiamos de proyecto, malísimo!
Con virtualenvs, los cambios son todos locales.
#### Crear un virtualenv
```
python3.9 -m venv .ofisino_venv
```
La parte `python3.9 -m venv` dice: Usá `python3.9` para ejecutar el `-m`ódulo (o programa) llamado `venv`.
`.ofisino_venv` es el nombre que le asignamos a nuestro entorno virtual.

Por qué el punto al inicio del nombre? Es una convención de linux para archivos ocultos.
La carpeta `.venv` nunca se commitea al repositorio, es equivalente al `node_modules` en javascript o el `vendor` en PHP

#### Activar el entorno
Una vez que lo creamos, tenemos que asociar el proyecto a su entorno.decirle a la terminal
Desde la terminal esto se hace con:
```bash
source `.ofisino_venv/bin/activate`
```
Para sorpresa de nadie `activate` activa el entorno. Esto quiere decir que si ahora instalamos una librería,
esta sólo va a estar disponible para este entorno, y ningún otro.
Eso es todo lo que necesitamos saber de virtualenvs por ahora.
Si querés aprender más podés leer más [acá](http://notoquesmicodigo.blogspot.com/2013/11/virtualenv-que-por-que-y-como.html)

> Si tenés algún problema, podés chequear las soluciones comunes [acá](https://tutorial.djangogirls.org/es/django_installation/)

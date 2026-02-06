# The foundational API for Connectly, focusing on CRUD operations. 

## git commands to upload my first commit
- echo "# Connectly-API" >> README.md
- git init
- git add README.md
- git commit -m "first commit"
- git branch -M main
- git remote add origin https://github.com/lmdclerra/Connectly-API.git
- git push -u origin main

## staging and updating views.py 
- git add views.py README.md db.sqlite3
- git commit -m "updating views, readme and sqlite files"
- git push -u origin main

## Searching OpenSSL through winget
```shell
PS C:\Users\hsdel> winget search "OpenSSL"
Name                 Id                         Version Match        Source
---------------------------------------------------------------------------
FireDaemon OpenSSL 3 FireDaemon.OpenSSL         3.4.0   Tag: openssl winget
OpenSSL 3.4.0        ShiningLight.OpenSSL.Dev   3.4.0                winget
OpenSSL Light 3.4.0  ShiningLight.OpenSSL.Light 3.4.0                winget
```

## How to Install OpenSSL
```shell
PS C:\Users\hsdel> winget install ShiningLight.OpenSSL.Dev
```

```shell

Win64 OpenSSL Command Prompt

OpenSSL 3.4.0 22 Oct 2024 (Library: OpenSSL 3.4.0 22 Oct 2024)
built on: Tue Oct 22 23:27:41 2024 UTC
platform: VC-WIN64A
options:  bn(64,64)
compiler: cl  /Z7 /Fdossl_static.pdb /Gs0 /GF /Gy /MD /W3 /wd4090 /nologo /O2 -DL_ENDIAN -DOPENSSL_PIC -D"OPENSSL_BUILDING_OPENSSL" -D"OPENSSL_SYS_WIN32" -D"WIN32_LEAN_AND_MEAN" -D"UNICODE" -D"_UNICODE" -D"_CRT_SECURE_NO_DEPRECATE" -D"_WINSOCK_DEPRECATED_NO_WARNINGS" -D"NDEBUG" -D_WINSOCK_DEPRECATED_NO_WARNINGS -D_WIN32_WINNT=0x0502
OPENSSLDIR: "C:\Program Files\Common Files\SSL"
ENGINESDIR: "C:\Program Files\OpenSSL\lib\engines-3"
MODULESDIR: "C:\Program Files\OpenSSL\lib\ossl-modules"
Seeding source: os-specific
CPUINFO: OPENSSL_ia32cap=0xfed8320b078bffff:0x209c01a9

C:\Users\hsdel>
```

## Challenges using OpenSSL in a Django Project
```shell
C:\Users\hsdel\OneDrive\Desktop\Connectly-API>env\Scripts\activate

(env) C:\Users\hsdel\OneDrive\Desktop\Connectly-API>pip list
Package                       Version
----------------------------- -------
asgiref                       3.8.1
Django                        5.1.5
django-cors-headers           4.6.0
django-extensions             3.2.3
djangorestframework           3.15.2
djangorestframework_simplejwt 5.4.0
pip                           25.0
PyJWT                         2.10.1
sqlparse                      0.5.3
tzdata                        2025.1

(env) C:\Users\hsdel\OneDrive\Desktop\Connectly-API>python manage.py runserver_plus --cert-file cert.pem --key-file key.pem
Unknown command: 'runserver_plus'. Did you mean runserver?
Type 'manage.py help' for usage.
```
## Add Django Extention to INSTALLED_APPS

It looks like you are trying to run the runserver_plus command, which is part of the django-extensions package. However, it seems like this command is not recognized. Here are a few things to check:

Ensure the Package is Installed: Make sure that django-extensions is properly installed. According to your pip list, it is installed, so this step seems fine.

Add to INSTALLED_APPS: Ensure that django_extensions is added to the INSTALLED_APPS in your settings.py file:

```python
INSTALLED_APPS = [
    ...
    'django_extensions',
    ...
]
```

```shell
(env) C:\Users\hsdel\OneDrive\Desktop\Connectly-API>python manage.py runserver_plus --cert-file cert.pem --key-file key.pem
CommandError: Werkzeug is required to use runserver_plus. Please visit https://werkzeug.palletsprojects.com/ or install via pip. (pip install Werkzeug)
```


## ... And The Solution
```shell
(env) C:\Users\hsdel\OneDrive\Desktop\Connectly-API>pip install Werkzeug
Collecting Werkzeug
  Downloading werkzeug-3.1.3-py3-none-any.whl.metadata (3.7 kB)
Collecting MarkupSafe>=2.1.1 (from Werkzeug)
  Downloading MarkupSafe-3.0.2-cp313-cp313-win_amd64.whl.metadata (4.1 kB)
Downloading werkzeug-3.1.3-py3-none-any.whl (224 kB)
Downloading MarkupSafe-3.0.2-cp313-cp313-win_amd64.whl (15 kB)
Installing collected packages: MarkupSafe, Werkzeug
Successfully installed MarkupSafe-3.0.2 Werkzeug-3.1.3

(env) C:\Users\hsdel\OneDrive\Desktop\Connectly-API>python manage.py runserver_plus --cert-file cert.pem --key-file key.pem
CommandError: Python OpenSSL Library is required to use runserver_plus with ssl support. Install via pip (pip install pyOpenSSL).

(env) C:\Users\hsdel\OneDrive\Desktop\Connectly-API>pip install pyOpenSSL
Collecting pyOpenSSL
  Downloading pyOpenSSL-25.0.0-py3-none-any.whl.metadata (16 kB)
Collecting cryptography<45,>=41.0.5 (from pyOpenSSL)
  Downloading cryptography-44.0.0-cp39-abi3-win_amd64.whl.metadata (5.7 kB)
Collecting cffi>=1.12 (from cryptography<45,>=41.0.5->pyOpenSSL)
  Downloading cffi-1.17.1-cp313-cp313-win_amd64.whl.metadata (1.6 kB)
Collecting pycparser (from cffi>=1.12->cryptography<45,>=41.0.5->pyOpenSSL)
  Downloading pycparser-2.22-py3-none-any.whl.metadata (943 bytes)
Downloading pyOpenSSL-25.0.0-py3-none-any.whl (56 kB)
Downloading cryptography-44.0.0-cp39-abi3-win_amd64.whl (3.2 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 3.2/3.2 MB 1.8 MB/s eta 0:00:00
Downloading cffi-1.17.1-cp313-cp313-win_amd64.whl (182 kB)
Downloading pycparser-2.22-py3-none-any.whl (117 kB)
Installing collected packages: pycparser, cffi, cryptography, pyOpenSSL
Successfully installed cffi-1.17.1 cryptography-44.0.0 pyOpenSSL-25.0.0 pycparser-2.22

(env) C:\Users\hsdel\OneDrive\Desktop\Connectly-API>python manage.py runserver_plus --cert-file cert.pem --key-file key.pem
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on https://127.0.0.1:8000
Press CTRL+C to quit
 * Restarting with stat
Performing system checks...

System check identified no issues (0 silenced).

Django version 5.1.5, using settings 'connectly_project.settings'
Development server is running at https://[127.0.0.1]:8000/
Using the Werkzeug debugger (https://werkzeug.palletsprojects.com/)
Quit the server with CTRL-BREAK.
 * Debugger is active!
 * Debugger PIN: 953-453-974
```
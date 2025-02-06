import os
import sys
import django

# Añadir ruta de tu proyecto Django
sys.path.insert(0, os.path.abspath('C:/Users/anghe/OneDrive/Desktop/PC NUEVO/ADWEB-main1.V'))

# Configurar la variable de entorno DJANGO_SETTINGS_MODULE
os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'

# Configurar Django
django.setup()

# -- Project information -----------------------------------------------------

project = 'MiProyecto'
copyright = '2025, Tu Nombre'
author = 'Tu Nombre'

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Añadir estas configuraciones
autodoc_default_options = {
    'members': True,
    'show-inheritance': True,
}
from distutils.core import setup
import os

def refresh_plugin_cache():
    from twisted.plugin import IPlugin, getPlugins
    list(getPlugins(IPlugin))

setup(name='nanoplay',
      version='0.1',
      description='nanoplay is a naivistic music playing server',
      author='Seppo Yli-Olli',
      author_email='seppo.yliolli@gmail.com',
      packages=['nanoplay', 'twisted.plugins'],
      package_data={"twisted" : ["plugins/nanoplay_plugin.py"]},
      requires=['Twisted'],
      scripts=['scripts/nanoplay']
     )

refresh_plugin_cache()

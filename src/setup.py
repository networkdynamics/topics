from distutils.core import setup	
from distutils.extension import Extension
from Cython.Distutils import build_ext
import os.path
import sys
import numpy.core

numpy_include_dir = os.path.join(os.path.dirname(numpy.core.__file__),'include')

ext_modules = [	Extension('topics.topic_model', ['topics/topic_model.pyx'], include_dirs=[numpy_include_dir]),
	Extension('topics.gibbs_lda', ['topics/gibbs_lda.pyx'], include_dirs=[numpy_include_dir]) ]


setup(
	cmdclass = {'build_ext': build_ext},
	ext_modules = ext_modules,
	packages = ['topics'],
	package_data = {'topics' : ['*.pxd']},
	setup_requires = ['distribute','cython>=0.14'],
	install_requires = ['numpy>=1.6.1',],
)

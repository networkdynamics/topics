
build:
	python setup.py build

install:
	python setup.py install

build_inplace:
	python setup.py build_ext --inplace

build_debug:
	python-dbg setup.py build_ext --inplace --cython-gdb

clean:
	rm -rf build; \
	rm -f topics/*.c topics/*.so topics/*.pyc;

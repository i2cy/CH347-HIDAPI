rd /s /q ch347_hidapi.egg-info
rd /s /q build
move /y dist\* history\
python setup.py build sdist bdist_wheel

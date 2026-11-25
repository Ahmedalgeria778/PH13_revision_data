import numpy, scipy, pandas
print('numpy', numpy.__version__, 'scipy', scipy.__version__, 'pandas', pandas.__version__)
try:
    import mpmath
    print('mpmath', mpmath.__version__)
except Exception as e:
    print('mpmath unavailable', repr(e))

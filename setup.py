import sys
from cx_Freeze import setup, Executable

# GUI applications require a different base on Windows (the default is for a
# console application).
base = "Win32GUI"

addtional_mods = ['numpy.core._methods', 'numpy.lib.format']
setup(name="cluster analysis",
      version="0.1",
      description="distributive",
      options={'build_exe': {'includes': addtional_mods}},
      executables=[Executable(
          script="main.py",
          base=base,
          targetName="ClusterAnalysis2.exe",
          icon="icon\\app_icon.ico"
      )])

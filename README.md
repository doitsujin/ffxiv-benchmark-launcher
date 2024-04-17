# ffxiv-benchmark-launcher

This `python` script will allow you to directly launch and configure the FFXIV benchmark. 

To use the script, do the following:

* Get a copy of the benchmark you want to run (for the latest, see [https://na.finalfantasyxiv.com/lodestone/topics/detail/ffe3a1a5430a5a8168ca9782ab9ec0e57cd5be62](https://na.finalfantasyxiv.com/benchmark/))
* Unzip benchmark somewhere
* Download the script and run it, ex: 

```
wget https://raw.githubusercontent.com/doitsujin/ffxiv-benchmark-launcher/main/ffxiv-benchmark.py
python ffxiv-benchmark.py
```

* When prompted, select a prefix with DXVK already installed (to use DXVK features).
  * **Note**: The script will not automatically install `dxvk`, so if you don't do this you will be using `wined3d`
* Change `wine` version if desired (default is system wine, not using Proton such as `wine-ge` by default)
* Select the benchmark folder

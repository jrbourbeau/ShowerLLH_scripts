## The ShowerLLH directory

You will need to specify a ShowerLLH directory (see setup section below) 
that will be used to store all ShowerLLH-related output. 
The default directory structure is shown below using the IT73 
detector configuration.

```
    ShowerLLH/
	|
	+--resources/
	|  
	+--IT73_sim/
	|
	+--IT73_data/
```

The `resources/` directory stores the LLH tables, while `X_sim/` and `X_data/`
(where X is a detector configuration) are used to store reconstructions when 
ShowerLLH is run on simulation and data, respectively. These subdirectories in 
your ShowerLLH directory are generated automatically, as needed. 


## Setup

To set up ShowerLLH, you simply need to run `setup.py` with options for the path
to your ShowerLLH directory (`--llhdir`), the path to the metaproject containing 
the ShowerLLH project (`-m`), and the CVMFS toolset used to build your metaproject
(`-t`). E.g. 

```
./setup.py -llhdir /path/to/desired/ShowerLLHdir -m /path/to/metaproject -t py2-v1
```


## To run ShowerLLH

1. Build log-likelihood tables by running the `make_tables.py` script.
2. Run ShowerLLH on sim by running the `reconstruct_sim.py` script.
3. Run ShowerLLH on data by running the `reconstruct_data.py` script.


# Building LLH tables

Most of these scripts are made using argparse. Type `./[script] -h` for help messages and available options.

1. Run makecountstables.py

  - NOTE: this script submits jobs to condor and thus you must be on submitter when running this script.
  - mass submits MakeHist.py to the cluster
  - MakeHist.py

    - creates count tables using ShowerLLH.FillHist icetray module
    - stored as .npy files

2. Run makeLLHtables.py

  - merges the count tables produced by makecountstables.py
  - deletes the un-merged tables
  - normalizes the counts tables to log-probabilty tables

    - stored as .npy files

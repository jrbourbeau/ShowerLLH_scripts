#!/bin/sh

# Assign variables passed to script
cmd=$1
outfile=$3
shift 3
infiles=( "$@" )

# Create local directory for local I/O
# Copy files to localdir for processing
localdir=${_CONDOR_SCRATCH_DIR}/ShowerLLH_data_merge
mkdir -p $localdir
cp ${infiles[@]} $localdir

# Create array of local infiles to pass to command
localinfiles=()
for i in ${infiles[@]}
do 
	localinfiles+=($localdir/$(basename $i)) 
done

# Run executable on local infiles
# Will return local output file
localoutfile=$localdir/$(basename $outfile)
exec="python $cmd -o $localoutfile ${localinfiles[@]}"
$exec

# Remove local infiles
rm -f ${localinfiles[@]}
# Move local outfile to outdir
mv $localoutfile $(dirname $outfile) 

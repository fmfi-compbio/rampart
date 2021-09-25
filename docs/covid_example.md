# Running SARS-CoV-2 example

We assume that you installed our version of RAMPART folowing instructions [here](installation.md).

To run the covid example, first you have to activate conda environment you created during installation:

```bash
conda activate covid-artic-rampart
```

Then go to `example_data/SARS-CoV-2` folder

```bash
cd example_data/SARS-CoV-2
```

*Note: there shoud be some .fastq data in `example_data/SARS-CoV-2/fastq/pass` folder, but we have not provided them yet - for now, you have to use some of your own data (simply copy them to the `/fastq/pass` folder), you can try next steps anyway, but without data, RAMPART will just wait for the data*

Now run rampart by typing

```bash
rampart --protocol ../../example_protocols/SARS-CoV-2 --clearAnnotated
```
> This command simply runs RAMPART with specified protocol folder, clearing all annotated data before the run. The `../../example_protocols/SARS-CoV-2` path is where the [protocol](protocols.md) files are stored. The --clearAnnotated option means that we want RAMPART to clear all anotaded data from previous runs of this example.
> Look [here](https://github.com/fmfi-compbio/nanocrop/tree/New-monitoring-framework/rampart/SARS-CoV-2) for more actual or another version of protocol files. 

or use our shell script

```bash
./run.sh
```
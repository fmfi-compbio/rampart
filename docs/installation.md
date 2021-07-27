# Installation


These instructions assume that you have installed [MinKNOW](https://community.nanoporetech.com/downloads) and are able to run it.


We also assume that you are using conda -- See [instructions here](https://conda.io/projects/conda/en/latest/user-guide/install/index.html) to install conda on your machine.


## Install from source

(1) Clone the Github repo 

```bash
git clone https://github.com/fmfi-compbio/rampart.git
cd rampart
```

(2) Create an activate the conda environment with the required dependencies using the provided `environment.yml` file via

*note: we are using a modified version of porechop, where we fixed a bug which caused that in the original version of RAMPART the first 12 barcodes were missing for 96 pcr barcode set*

```bash
conda env create -f environment.yml
conda activate covid-artic-rampart
```

(3) Install dependencies using `npm`

```bash
npm install
```

(4) Build the RAMPART client bundle

*note: you will have to run this command anytime you pull a new version from gitHub*

```bash
npm run build
```

(5) (optional, but recommended) install rampart globally within the conda environment
so that it is available via the `rampart` command

```bash
npm install --global 
```

Check that things work by running `rampart --help`


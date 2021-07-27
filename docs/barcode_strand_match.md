# Covid strand matching pipeline

This pipeline looks for new `.csv` files that RAMPART has created in annotations  pipeline (located in `/annotations` folder) since last time when the pipeline was triggered.

Then it looks for matching `.fastq` files and creates `.bam` files from them one by one, using `minimap2`. 

The `.bam` files are no longer needed after we process them in our python script, so that they are deleted afterwards.

The first output file of this pipeline is located in `/annotations/base_count/count.csv` and contains counts of each base (A, C, G or T) for each position in reference for each barcode. In each line of the file there is 

* position in the reference genome
* barcode name
* count of A's mapped to this position in reference genome
* count of C's
* count of G's
* count of T's

When you trigger the pipeline next time, the pipeline will use this output file as one of its inputs, new counts will be added to those from the existing `counts.csv` file and a new file will be created as output.

The next step of our pipeline is determining the variants based on the provided `.txt` file of a specific format (see mutations file section below) which contains the changes in reference genome that are specific for some known variants of sars-cov-2.

By default our pipeline uses one of the `.txt` files we have created. All the `.txt` files are located in /covid_protocol/pipelines/run_python_scripts/rules/mut_files/
You may also want to provide your own. To do this, you have to create a `.txt` file in the directory mentioned above, and then in `covid_protocol/pipelines/run_python_scripts/config.yaml` replace the name of the file to be used with your own. 

You can also set your own threshold value, which determines minimal number of reads mapped to the position in the reference genome, so that our python script will clasify a mutation as significat enough to support that the barcode sample corresponds to a variant.

These are the default settings:

```
###mutations###
coverage_threshold: 10
mutations_file: mutbb.txt
```


At the end, the `annotations/results` folder should contain a `mutations.json` file containing the mutations we matched to the barcodes.

Once the json file is available, it will be loaded to RAMPART and the results will be shown.

## The mutations file
This file specifies the variants of sars-cov-2 to look for and mutations that are specific for a variant.
Each line starts with a label of a variant at the beginning, 
followed by exactly one space and then a number of mutations that we want to match so that we can say that a barcode corresponds to this variant.
Then there are mutations that are typical for a variant separated by spaces.
Lines starting with `#` are comments and are ignored when parsing the file.

### Example
```
UK 5 C3267T C5388A ... G28280C A28281T T28282A
```
in our default file you can see this line, 

starting with "UK", which is our label for this variant. 

the label is followed by a number, 5, which says that "if at least 5 of the following mutations are present int he sample, classify the sample as this variant"

the number is followed by mutations (for example C is changed to T at the position 3267 mapped to reference genome) that are typical for this variant, separated by spaces.

### Tree-like structure
You can also provide another variants in tree-like structure, using syntax `start_sub` and `end_sub` in separate lines:
```
#UK variant
UK 5 C3267T ... T28282A

#more specific variants for UK
start_sub
UK-subvariant_1 1 A17615G

#subvariants for UK-subvariant_1
start_sub
.
.
UK-subvariant_1-Poland 4 C5301T C7420T C9693T G23811T C25350T C28677T G29348T
UK-subvariant_1-Gambia 3 T6916C T18083C G22132A C23929T
end_sub

end_sub

#CZ variant
CZ 3 G12988T G15598A G18028T T24910C T26972C 
```

This means that we will look for UK variant, and if we will find at least 5 mutations from the list provided in the UK line, we will also continue searching for other more specific variants.

For example if UK variant is matched, we will check whether there is also a mutation in position A17615G, 

if it is, then we will chcek if there are some of the mutations specified in its subsection - UK-subvariant_1-Poland or UK-subvariant_1-Gambia. 

We will stop searching at the point when there are no more subsections specified or when less than the required count of mutations vere found for a sample.

We will look for CZ variant too. This one has no subvariants specified in this example file, so no further search would be made.


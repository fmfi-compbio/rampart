rule count_and_compare:
    input:
        path = config["path"],
        mut= workflow.current_basedir+"/mut_files/"+config["mutations_file"],
        ref= config["references_file"]
    output:
        csv = config["path"]+"/results/mutations.json"
    threads: 2,
    params:
        path_to_script = workflow.current_basedir,
        out_dir = config["path"]+"/results",
        output = config["path"]+"/results/mutations",
        count_file=config["path"]+"/base_count/count.csv",
        base_count_dir=config["path"]+"/base_count",
        annot_path=config["path"],
        fastq_path=config["fastq_path"],
        threshold=config["coverage_threshold"]
    message:
        "running count and compare script"
    shell:
        """
        mkdir -p {params.base_count_dir} &&\
        python3 {params.path_to_script}/count_observed_counts.py {input.ref:q} -o {params.count_file:q}\
         --working_path {params.base_count_dir} --fastq_path {params.fastq_path:q} --rampart_csv_path {params.annot_path:q} &&\
        mkdir -p {params.out_dir} &&\
        python3 {params.path_to_script}/compare_mutations.py {params.count_file:q} {input.ref:q} {input.mut:q} --threshold {params.threshold:q} -o {params.output}
        """
         

import argparse
import sys
import os

import pysam

from helpers import load_fasta, apply_to_cigartuples, create_barcodes_dict, print_alignments, dump_dict_to_file, load_dict

letters = "ACGT"
l2n = {letter: num for num, letter in enumerate(letters)}

def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("reference", type=str)
    parser.add_argument("-o", "--output", type=str, required=True)
    parser.add_argument("--alignment_low_cutoff", type=int, default=50)
    parser.add_argument("--working_path", type=str, required=True)
    parser.add_argument("--fastq_path", type=str, required=True)
    parser.add_argument("--rampart_csv_path", type=str, required=True)
    return parser.parse_args(argv)

def create_bam(reference,fname,fastq_path,working_path):
    print("minimap2 -t 2 -x map-ont -a "+reference+" "+fastq_path+"/"+fname+".fastq | samtools view -S -b -o - | samtools sort - -o "+working_path+"/"+fname+".bam && samtools index "+working_path+"/"+fname+".bam")
    res=os.system("minimap2 -t 2 -x map-ont -a "+reference+" "+fastq_path+"/"+fname+".fastq | samtools view -S -b -o - | samtools sort - -o "+working_path+"/"+fname+".bam && samtools index "+working_path+"/"+fname+".bam" )
    
def scan_folder(working_path, dir_path):
    to_ignore = set()
    to_work_with = set()
    if os.path.exists(working_path+"/done.txt"):
        with open(working_path+"/done.txt", "r") as f:
            for line in f:
                to_ignore.add(line.strip())
    for filename in os.listdir(dir_path):
        if filename.endswith(".csv"): 
            if not(filename in to_ignore):
                to_work_with.add(filename)
    return to_work_with
    
def write_files_to_be_ignored(working_path, to_work_with):
    with open(working_path+"/done.txt", "a+") as f:
        for fname in to_work_with:
            print(fname, file=f)

"""
def dump_observed_counts(counts_by_pos, f):
    print("position,letter,count", file=f)
    for position, counts in enumerate(counts_by_pos):
        for i, letter in enumerate("ACGT"):
            print(f"{position+1},{letter},{counts[i]}", file=f)

def dump_observed_counts_for_barcodes(counts_by_barcodes_and_pos, f):
    for barcode in counts_by_barcodes_and_pos:
        fname = barcode+".txt"
        with open(fname, "w") as barcodefile:
            dump_observed_counts(counts_by_barcodes_and_pos[barcode], barcodefile)
"""            

def count_bases_in_alignment(alignments, reference, alignment_length_low_cutoff, barcodes_dict, counts_by_barcode_and_pos):
    global l2n
    #counts_by_pos = [[0 for _ in letters] for _ in reference]
    empty_queries_count = 0
    short_alignments_count = 0

    def count_alongside_cigar(op, l, r, q, al, barcode):
        global l2n
        nonlocal counts_by_barcode_and_pos, reference
        query = al.query_sequence
        if op == 0 or op == 7 or op == 8:
            for k in range(l):
                try:
                    #counts_by_pos[r + k][l2n[query[q + k]]] += 1
                    counts_by_barcode_and_pos[barcode][r + k][l2n[query[q + k]]]+=1
                except IndexError as e:
                    print(e)
                    print(f"{op},{l},{r + k}<?{len(counts_by_barcode_and_pos)},{q + k}<?{len(query)}")
                    sys.exit(1)
                    
    for alignment_num, alignment in enumerate(alignments.fetch()):
        query = alignment.query_sequence
        if query is None:
            empty_queries_count += 1
            print(f"{empty_queries_count} empty queries so far! ({alignment_num} processed)")
            continue
        alignment_length = alignment.query_alignment_length
        if alignment_length < alignment_length_low_cutoff:
            short_alignments_count += 1
            print(f"{short_alignments_count} short alignments so far! ({alignment_num} processed)")
            continue
        query_name = alignment.query_name
        if query_name in barcodes_dict:
            barcode = barcodes_dict[query_name]
            #print(barcode)
            if not barcode in counts_by_barcode_and_pos:
                print("found new barcode! "+barcode)
                counts_by_barcode_and_pos[barcode] = [[0 for _ in letters] for _ in reference]
        else:
            barcode = "none"
            print(barcode)
        apply_to_cigartuples(count_alongside_cigar, alignment, barcode)
    return counts_by_barcode_and_pos


def count_observed_counts(alignment_filename,
                          csv_filename,
                          alignment_length_low_cutoff,
                          counts,
                          reference): 
    alignments = pysam.AlignmentFile(alignment_filename, "rb")
    #print_alignments(alignments)
    barcodes_dict = create_barcodes_dict(csv_filename)
    os.system("rm "+alignment_filename)
    os.system("rm "+alignment_filename+".bai")
    #print(barcodes_dict)

    counts_by_barcode_and_pos = count_bases_in_alignment(alignments, reference, alignment_length_low_cutoff, barcodes_dict, counts)

    return counts_by_barcode_and_pos;

def main():
    args = parse_args(sys.argv[1:])
    file_set=scan_folder(args.working_path, args.rampart_csv_path)
    reference = list(load_fasta(args.reference))[0][1]
    counts_by_barcode_and_pos = load_dict(args.output, reference)
    if len(counts_by_barcode_and_pos)==0:
    	counts_by_barcode_and_pos["none"] = [[0 for _ in letters] for _ in reference]
    for fname in file_set:
        print(fname)
        fname=fname.rsplit('.', 1)[0]
        create_bam(args.reference,fname,args.fastq_path,args.working_path)
        counts_by_barcode_and_pos = count_observed_counts(alignment_filename=args.working_path+"/"+fname+".bam",
                              csv_filename=args.rampart_csv_path+"/"+fname+".csv",
                              alignment_length_low_cutoff=args.alignment_low_cutoff,
                              counts=counts_by_barcode_and_pos,
                              reference=reference)
    curpath = os.path.abspath(os.curdir)
    print("Current path is: %s" % (curpath))
    print("Writing output to: %s" % (os.path.join(curpath, args.output)))    
    with open(args.output, "w") as f:
        dump_dict_to_file(counts_by_barcode_and_pos, f)
    write_files_to_be_ignored(args.working_path, file_set)
    

if __name__ == "__main__":
    main()

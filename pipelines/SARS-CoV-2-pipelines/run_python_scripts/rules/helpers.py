import math
import os
from collections import defaultdict

letters = "ACGT"
l2n = {letter: num for num, letter in enumerate(letters)}

def load_dict(file_path, reference):
    fdict={}
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            for line in f:
                l = line.split(",")
                position = int(l[0])-1
                barcode = l[1]
                A = int(l[2])
                C = int(l[3])
                G = int(l[4])
                T = int(l[5])
                if not barcode in fdict:
                    fdict[barcode] = [[0 for _ in letters] for _ in reference]
                fdict[barcode][position][0]+=A
                fdict[barcode][position][1]+=C
                fdict[barcode][position][2]+=G
                fdict[barcode][position][3]+=T 
    return fdict

def load_fasta(filename: str):
    with open(filename) as f:
        yield from load_fasta_fd(f)


def load_fasta_fd(f):
    label, buffer = "", []
    for line in f:
        if len(line) > 0 and line[0] == ">":
            # new label
            if len(buffer) > 0:
                yield label, "".join(buffer)
            label = line.strip()[1:]
            buffer = []
        else:
            buffer.append(line.strip())
    if len(buffer) > 0:
        yield label, "".join(buffer)


def apply_to_cigartuples(fun, alignment, barcode, *args, **kwargs):
    """
    M	BAM_CMATCH	0
    I	BAM_CINS	1
    D	BAM_CDEL	2
    N	BAM_CREF_SKIP	3
    S	BAM_CSOFT_CLIP	4
    H	BAM_CHARD_CLIP	5
    P	BAM_CPAD	6
    =	BAM_CEQUAL	7
    X	BAM_CDIFF	8
    B	BAM_CBACK	9 (????!)
    """
    query_pos = 0
    reference_pos = alignment.reference_start
    for op, length in alignment.cigartuples:
        fun(op, length, reference_pos, query_pos, alignment, barcode, *args, **kwargs)
        if op == 0 or op == 7 or op == 8:
            reference_pos += length
            query_pos += length
        elif op == 1 or op == 4:
            query_pos += length
        elif op == 2 or op == 3:
            reference_pos += length
        elif op == 5 or op == 6:
            pass
        else:
            raise Exception(f"Operation code of cigar tuple is outside of range [0-8]: "
                            f"op={op}, length={length}")

def create_barcodes_dict(csv_filename):
   barcode_dict = {}
   with open(csv_filename, "r") as f:
        line = f.readline()
        while True:
            line = f.readline()
            if not line:
                break
            arr = line.split(",")
            barcode_dict[arr[0]] = arr[3]
   return barcode_dict
                      
            
def dump_dict_to_file(counts, f):        
    for barcode in counts:
       for position, pos_counts in enumerate(counts[barcode]):
           print(f"{position+1},{barcode},{pos_counts[0]},{pos_counts[1]},{pos_counts[2]},{pos_counts[3]}", file=f)   
   
   
   
   
       

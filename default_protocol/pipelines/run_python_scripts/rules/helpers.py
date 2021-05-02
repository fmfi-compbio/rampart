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
                    #print("found new barcode! "+barcode)
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

"""
def load_observed_counts(fd):
    header = fd.readline().strip()
    assert header == "position,letter,count", f"Expected 'position,letter,count' header, got '{header}' instead"
    result_raw = defaultdict(dict)
    for line in fd:
        row = line.strip().split(",")
        pos, letter, count = int(row[0])-1, row[1], int(row[2])
        result_raw[pos][letter] = count
    result = [[result_raw.get(pos, {}).get(letter, 0) for letter in "ACGT"]
              for pos in range(1 + max(result_raw.keys(), default=-1))]
    return result



def load_clades(fd):
    global l2n
    header = fd.readline().strip()
    assert header == "clade,position,letter,probability"
    result = defaultdict(list)
    for line in fd:
        row = line.strip().split(",")
        clade, position, letter_count, probability = row[0], int(row[1])-1, l2n[row[2]], float(row[3])
        while position >= len(result[clade]):
            result[clade].append([0 for _ in l2n])
        result[clade][position][letter_count] = probability
    clades = list(result.keys())

    for clade in clades:
        assert len(result[clade]) == len(result[clades[0]])

    return dict(result)


def entropy(p):
    return -sum(x * math.log(x) if x > 0 else 0 for x in p)


def cross_entropy(p, q):
    assert len(p) == len(q)
    return -sum(sorted(p[i] * math.log(max(1e-300, q[i])) for i in range(len(p))))


def add_noise(v, eps=0.02):
    res = [(1-eps) * x + eps/(len(v)-1) * (1 - x) for x in v]
    return res
"""

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


def load_posteriors_for_reads(f):
    header = f.readline().strip().split(",")
    clade_names = header[1:]
    probs = []
    for line in f:
        row = line.strip().split(",")
        read_id = row[0]
        probs.append((read_id, tuple(map(float, row[1:]))))
    return clade_names, probs
    
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
                
def print_alignments(alig):
   for read in alig.fetch():
       print(read)            
   #for alignment_num, alignment in enumerate(alig.fetch()):
       #print(alignment.query_name)
            
def dump_dict_to_file(counts, f):        
    for barcode in counts:
       for position, pos_counts in enumerate(counts[barcode]):
           print(f"{position+1},{barcode},{pos_counts[0]},{pos_counts[1]},{pos_counts[2]},{pos_counts[3]}", file=f)   
   
   
   
   
       

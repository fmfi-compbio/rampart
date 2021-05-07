import os
import sys
import argparse
import json

from helpers import load_fasta, l2n, letters

class Tree:
    def __init__(self, name, min_num):
        self.children = []
        self.data = []
        self.name = name
        self.min_num = min_num

def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", type=str)
    parser.add_argument("reference", type=str)
    parser.add_argument("mutations", type=str)
    parser.add_argument("--threshold", type=int, default=42) #minimal number of reads needed
    parser.add_argument("-o", "--output", type=str, required=True)
    return parser.parse_args(argv)
    
def load_file(file_path, reference):
    barcode_dict = {}
    with open(file_path, "r") as f:
        for line in f:
            l = line.split(",")
            position = int(l[0])-1
            barcode = l[1]
            A = int(l[2])
            C = int(l[3])
            G = int(l[4])
            T = int(l[5])
            if not barcode in barcode_dict:
                barcode_dict[barcode] = [[0 for _ in letters] for _ in reference]
            barcode_dict[barcode][position][0]+=A
            barcode_dict[barcode][position][1]+=C
            barcode_dict[barcode][position][2]+=G
            barcode_dict[barcode][position][3]+=T   
    return barcode_dict


def load_mutations(mutations_path):    #loading .txt file containing mutations for each variant
    
    mutations = Tree("root", 0)
    stack = []
    index = 0
    stack.append(mutations)
    
    with open (mutations_path, "r") as txtfile:
        mut_name = ""
        maybeparent = mutations
        for line in txtfile:
            line = line.strip()
            if line == "start_sub":
                stack.append(maybeparent)
                index += 1
            elif line == "end_sub":
                stack.pop()   
                index -= 1       
            elif not line.startswith('#') and line:
                columns = line.split(" ")
                parent = stack[index]  
                child = Tree(columns[0], int(columns[1]))
                for i in range(2, len(columns)):
                    child.data.append(columns[i])
		
                parent.children.append(child)
                maybeparent = child            

    return mutations

def find_variants(barcode_dict, variants, jsonfile, threshold): #looking for possible variants for a barcode

    barcodes=[]
    for barcode in barcode_dict:
        barcode_to_append = {}
        barcode_to_append['barcode'] = barcode
        barcode_to_append['variants'] = []
        for strand in variants.children:
            variant=check_variant(barcode_dict[barcode], threshold, strand)
            if variant != None:
                barcode_to_append['variants'].append(variant)
        barcodes.append(barcode_to_append)
    print(json.dumps(barcodes), file=jsonfile)  


def check_variant(barcode, threshold, strand): #check whether this variant meets our conditions
    num_of_mutations = 0
    variant_dict = {}
    variant_dict['name'] = strand.name
    variant_dict['mutations'] = []
    for mut in strand.data:
        if mut[2].isdigit():
            position = int(mut[1:len(mut)-1])-1
                        
            #check that the position is within range        
            if position < 0 or position >= len(barcode):
                continue
            
            same_as_reference = barcode[position][l2n[mut[0]]] #num of bases same as reference
            same_as_mutation = barcode[position][l2n[mut[len(mut)-1]]]; #num of bases same as mutation
            reads_coverage = barcode[position][0]+barcode[position][1]+barcode[position][2]+barcode[position][3]
                   
            if same_as_reference < same_as_mutation and reads_coverage >= threshold:                     
                num_of_mutations += 1
                mutation_dict = {}
                mutation_dict['position'] = position+1
                mutation_dict['from'] = mut[0]
                mutation_dict['to'] = mut[len(mut)-1]
                mutation_dict['same_as_reference'] = same_as_reference
                mutation_dict['same_as_mutation'] = same_as_mutation
                variant_dict['mutations'].append(mutation_dict)
               
   
    variant_dict['subs'] = []
    #we found a variant 
    if num_of_mutations >= strand.min_num:
        #if the variant has subvariants, check them.
        if (len(strand.children) > 0):
            for substrand in strand.children:
                substrand_dict = check_variant(barcode, threshold, substrand)
                if (substrand_dict != None):
                    variant_dict['subs'].append(substrand_dict)
        return variant_dict 
    #if there is not enough mutations matched for this variant
    else:
    	return None
            
def main():
    args = parse_args(sys.argv[1:])   
    reference = list(load_fasta(args.reference))[0][1]
    barcode_dict = load_file(args.file_path, reference)
    variants = load_mutations(args.mutations)
    threshold = args.threshold
    with  open(args.output+".json", "w") as jsonfile:
    	find_variants(barcode_dict, variants, jsonfile, threshold)
    

    
if __name__ == "__main__":
    main()

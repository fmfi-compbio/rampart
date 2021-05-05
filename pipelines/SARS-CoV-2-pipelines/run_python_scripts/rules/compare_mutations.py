import os
import sys
import argparse

from helpers import load_fasta, l2n

letters = "ACGT"

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

def find_variants(barcode_dict, variants, json, threshold): #looking for possible variants for a barcode
    barcode_strings=[]
    json_string='['
    for barcode in barcode_dict:
        barcode_string=""
        barcode_string+='{"barcode":"'+barcode+'","variants":[' #begin of barcode
        variant_strings=[]
        for strand in variants.children:
            variant_string=check_variant(barcode_dict[barcode], threshold, strand)
            if variant_string!="":
                variant_strings.append(variant_string)
        barcode_string+= ", ".join(variant_strings)
        barcode_string+=']}' #end of barcode
        barcode_strings.append(barcode_string)
    json_string+=", ".join(barcode_strings)
    json_string+=']'                        
    print(json_string, file=json)      


def check_variant(barcode, threshold, strand): #check whether this variant meets our conditions
    pocet=0
    json_string = '{'
    json_string+='"name": "'+strand.name+'",'
    json_string+='"mutations":['
    positions=[]
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
                pocet += 1
                positions.append('{"position":'+str(position+1)+',"from":"'+mut[0]+'","to":"'+mut[len(mut)-1]+'"}')
    json_string+=", ".join(positions)           
                
    json_string+='],'
    json_string+='"subs":['      
    #we found a variant 
    if pocet >= strand.min_num:
        #if the variant has subvariants, check them.
        if (len(strand.children) > 0):
            substrand_strings=[]
            for substrand in strand.children:
                string_to_insert = check_variant(barcode, threshold, substrand)
                if (string_to_insert != ""):
                    substrand_strings.append(string_to_insert)
            if len(substrand_strings)>0:
                json_string+=", ".join(substrand_strings)        
        json_string+=']}'
        return json_string 
    #if there is not enough mutations matched for this variant
    else:
    	return ""
            
def main():
    args = parse_args(sys.argv[1:])   
    reference = list(load_fasta(args.reference))[0][1]
    barcode_dict = load_file(args.file_path, reference)
    variants = load_mutations(args.mutations)
    threshold = args.threshold
    with  open(args.output+".json", "w") as json:
    	find_variants(barcode_dict, variants, json, threshold)
    

    
if __name__ == "__main__":
    main()

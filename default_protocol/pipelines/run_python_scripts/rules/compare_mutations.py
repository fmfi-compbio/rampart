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
                #print("found new barcode! "+barcode)
                barcode_dict[barcode] = [[0 for _ in letters] for _ in reference]
            barcode_dict[barcode][position][0]+=A
            barcode_dict[barcode][position][1]+=C
            barcode_dict[barcode][position][2]+=G
            barcode_dict[barcode][position][3]+=T   
    return barcode_dict


def load_mutations(mutations_path):    
    #nacitanie mut.txt
    
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
            
def guess(barcode, threshold, strand):
    pocet = 0
    single_muts = [] #mutacie sconcatenovane cez & (budu)
    
    for mut in strand.data:
        #print(mut)
        if mut[2].isdigit():
            position = int(mut[1:len(mut)-1])-1
            
            #toto treba, inak vyhodi podmienku ze je mimo indexu :|        
            if position < 0 or position >= len(barcode):
                continue
            
            m1 = barcode[position][l2n[mut[0]]] #pocet baz zhodnych s referenciou
            m2 = barcode[position][l2n[mut[len(mut)-1]]]; #pocet baz zhodnych s mutaciou
            reads_coverage = barcode[position][0]+barcode[position][1]+barcode[position][2]+barcode[position][3]
                   
            if m1 < m2 and reads_coverage >= threshold: #ak bolo na danu poziciu namapovanych uz aspon threshold baz a je viac tych zmutovanych                         
                pocet += 1
                single_muts.append(mut)
                
    #ak je to pravdepodobne tato mutacie, zisti pre submutacie, ci sedia nejake
    if pocet >= strand.min_num:
        if (len(strand.children) > 0):
            strands = ""
            pocet_subov = 0
            for strandik in strand.children:
                stran, poc, sinmut = guess(barcode, threshold, strandik)
                if (stran != ""):
                    if pocet_subov > 0:
                        strands += "/"+stran #dalsia vetva submutacii, oddelena cela '/'
                    else:
                        strands += stran
                    pocet_subov += 1
                    pocet += poc
                    single_muts += sinmut
    	    	
            if pocet_subov > 1:
                return strand.name + ":" + strands, pocet, single_muts #ak sa to vetvi, da ':'
            elif pocet_subov > 0:
                return strand.name + "." + strands, pocet, single_muts #ak sa to nevetvi, deti oddelene ','
                
        return strand.name, pocet, single_muts
    	
    else:
    	return "", 0, ""

    
def find_variants(barcode_dict, mutacie, csv, threshold):
    #barcode dict - nacitany dictionary zo suboru (pocty ACGT na jednotlivych poziciach v jednotlivych barkodoch)
    #mutacie - nacitany subor mut.txt (load_mutations)
    #print(barcode_dict)
    print("barcode,strand,support,mutations", file=csv)
    for barcode in barcode_dict:
        for strand in mutacie.children:
            strands, pocet, single_mut = guess(barcode_dict[barcode], threshold, strand) 
            
            if strands == "":
                continue
                
            sinmut = "&".join(single_mut)
            string = barcode +","+ strands +","+ str(pocet)+","+ sinmut
            print(string, file=csv)           


def find_variants2(barcode_dict, mutacie, json, threshold): #podobne ako find_variants, len chceme vysledok v jason formate
    json_string='['
    for barcode in barcode_dict:
        json_string+='{"barcode":"'+barcode+'","mutations":[' #zaciatok barkodu
        for strand in mutacie.children:
            json_string+= guess2(barcode_dict[barcode], threshold, strand) 
        json_string+=']},' #koniec barkodu
    json_string+=']'                        
    print(json_string, file=json)      


def guess2(barcode, threshold, strand): #podobne ako guess, len chceme vysledok v json formate
    pocet=0
    json_string = '{'
    json_string+='"name": "'+strand.name+'",'
    json_string+='"mutations":['
    for mut in strand.data:
        #print(mut)
        if mut[2].isdigit():
            position = int(mut[1:len(mut)-1])-1
                        
            #toto treba, inak vyhodi podmienku ze je mimo indexu :|        
            if position < 0 or position >= len(barcode):
                continue
            
            m1 = barcode[position][l2n[mut[0]]] #pocet baz zhodnych s referenciou
            m2 = barcode[position][l2n[mut[len(mut)-1]]]; #pocet baz zhodnych s mutaciou
            reads_coverage = barcode[position][0]+barcode[position][1]+barcode[position][2]+barcode[position][3]
                   
            if m1 < m2 and reads_coverage >= threshold: #ak bolo na danu poziciu namapovanych uz aspon threshold baz a je viac tych zmutovanych                         
                pocet += 1
                pos=position+1
                json_string+='{"position":'+str(pos)+',"from":"'+mut[0]+'","to":"'+mut[len(mut)-1]+'"},'
               
                
    json_string+='],'
    json_string+='"subs":['      
    #ak je pravdepodobna tato mutacie, zisti pre submutacie, ci sedia nejake
    if pocet >= strand.min_num:
        if (len(strand.children) > 0):
            for strandik in strand.children:
                string_to_insert = guess2(barcode, threshold, strandik)
                if (string_to_insert != ""):
                    json_string+=string_to_insert
                    
        json_string+=']},'
        return json_string
    	
    else:
    	return ""
            
def main():
    args = parse_args(sys.argv[1:])   
    reference = list(load_fasta(args.reference))[0][1]
    barcode_dict = load_file(args.file_path, reference)
    mutacie = load_mutations(args.mutations)
    threshold = args.threshold
    with  open(args.output+".csv", "w") as csv:
    	find_variants(barcode_dict, mutacie, csv, threshold)
    with  open(args.output+".json", "w") as json:
    	find_variants2(barcode_dict, mutacie, json, threshold)
    

    
if __name__ == "__main__":
    main()

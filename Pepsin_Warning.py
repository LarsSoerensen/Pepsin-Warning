# -*- coding: utf-8 -*-
"""
Created on Thu Jan 14 12:47:39 2016

@author: lssx
"""

#==================================================================================
# This software will identfy if an PLGS identified sequence is impossiple
# (H,K,R,P in position P1 or P in P2)
# The seqeunce can be loaded using a FASTA sequence or just typed in
# The .CSV output from LARS can be used to provide the list of identified peptides
#==================================================================================

import csv

seq_dict = {}
with open("FXIIII-B_IA_final_peptide.csv") as csv_file:
    reader = csv.reader(csv_file)
    row_count = 0 #Skipping the .csv header
    for row in reader:
        if row_count == 0:
            row_count += 1
        else:        
            postion_and_AA = []
            position = int(row[26])
            postion_and_AA.append((position-1, position-2)) #Adds the P1 and P2 seqeunce postions to each identified peptide.
            for char in row[25]:
                postion_and_AA.append((char, position)) 
                position += 1
              
            seq_dict[row[25]] = postion_and_AA

csv_file.close()

sequence = 'SETSRTAFGGRRAVPPNNSNAAEDDLPTVELQGVVPRGVNLQEFLNVTSVHLFKERWDTNKVDHHTDKYENNKLIVRRGQSFYVQIDFSRPYDPRRDLFRVEYVIGRYPQENKGTYIPVPIVSELQSGKWGAKIVMREDRSVRLSIQSSPKCIVGKFRMYVAVWTPYGVLRTSRNPETDTYILFNPWCEDDAVYLDNEKEREEYVLNDIGVIFYGEVNDIKTRSWSYGQFEDGILDTCLYVMDRAQMDLSGRGNPIKVSRVGSAMVNAKDDEGVLVGSWDNIYAYGVPPSAWTGSVDILLEYRSSENPVRYGQCWVFAGVFNTFLRCLGIPARIVTNYFSAHDNDANLQMDIFLEEDGNVNSKLTKDSVWNYHCWNEAWMTRPDLPVGFGGWQAVDSTPQENSDGMYRCGPASVQAIKHGHVCFQFDAPFVFAEVNSDLIYITAKKDGTHVVENVDATHIGKLIVTKQIGGDGMMDITDTYKFQEGQEEERLALETALMYGAKKPLNTEGVMKSRSNVDMDFEVENAVLGKDFKLSITFRNNSHNRYTITAYLSANITFYTGVPKAEFKKETFDVTLEPLSFKKEAVLIQAGEYMGQLLEQASLHFFVTARINETRDVLAKQKSTVLTIPEIIIKVRGTQVVGSDMTVTVQFTNPLKETLRNVWVHLDGPGVTRPMKKMFREIRPNSTVQWEEVCRPWVSGHRKLIASMSSDSLRHVYGELDVQIQRRPSM'
danger_list_P1 = []
danger_list_P2 = []
position = 0
for char in sequence:
    if char in set(['R','H','K','P']):
        danger_list_P1.append((char, position))
        if char == 'P':
            danger_list_P2.append((char, position))
    else: 
        pass
    position += 1

for item in seq_dict:
    for ite in danger_list_P1:
        if ite[1] == seq_dict[item][0][0]:
            if item[0] == ite[0]:
                pass
            else:
                print(item, ite[1], seq_dict[item][0][0])
        else:
            pass
    for ite in danger_list_P2:
        if ite[1] == seq_dict[item][0][1]:
            if item[0] == ite[0]:
                pass
            else:
                print(item, ite[1], seq_dict[item][0][1])
        else:
            pass
    
print('Done')
        

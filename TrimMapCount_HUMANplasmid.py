from math import ceil
import os, sys, glob, stat
import re

lines_per_commandfile = 10

files_list=[]
with open("plasmidFilestomap.txt", 'r') as f:
  for line in f:
    files_list.append(line[:-1])

output_basename = "mapped_toPAO1x."
print(files_list)

filecounter = 1
for i in range(ceil(len(files_list)/lines_per_commandfile)):
    with open(output_basename+str(i), 'w') as f:
      print("module load fastqc/0.11.2", file=f)
      print("module load bowtie2/2.3.2", file=f)
      print("module load R/3.4.3", file=f)
      print("module load gcc/7.3.0", file=f)
      print("module load python/2.7", file=f)
      print("module load cutadapt/1.8.1", file=f)
      print("module load samtools", file=f)
      for filename in files_list[((i)*lines_per_commandfile):((i)*lines_per_commandfile)+ lines_per_commandfile]:
#        print("cutadapt -m 25 -a AGATCGGAAGAGCACACGTCTGAACTCCAGTCAC -o /nv/hp10/dcornforth3/scratch/IntermediateSteps/trimmed.{:s} {:s} > /nv/hp10/dcornforth3/scratch/IntermediateSteps/cutadapt.{:s}.txt".format(filename, filename, filename), file=f)
        print("bowtie2 -x /nv/hp10/dcornforth3/data/Dan/ref_genome/combined_megaplasmid/combined_megaplasmid -U /nv/hp10/dcornforth3/scratch/IntermediateSteps/trimmed.{:s} -S /nv/hp10/dcornforth3/scratch/IntermediateSteps/{:s}.mapped_to_plasmids.SAM".format(filename, filename, filename), file=f)

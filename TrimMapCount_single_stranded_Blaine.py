from math import ceil
import datetime
import os, sys, glob, stat
import re

lines_per_commandfile = 10

files_list=[]
with open("Filestomap.txt", 'r') as f:
  for line in f:
    files_list.append(line[:-1])

output_basename = "mapped_toPAO1."
print(files_list)

now = datetime.datetime.now()
current_date = str(now.month)+"_" + str(now.day)+ "_" + str(now.year)

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
      print("cutadapt -m 18 -a AGATCGGAAGAGCACACGTCTGAACTCCAGTCAC -o /nv/hp10/dcornforth3/scratch/IntermediateSteps/trimmed18.{:s}.{:s} {:s} > /nv/hp10/dcornforth3/scratch/IntermediateSteps/cutadapt18.{:s}.{:s}.txt".format(filename, current_date, filename, filename, current_date), file=f)
      print("bowtie2 -x /nv/hp10/dcornforth3/refstrains/NON_PA_June8/NON_PA_June8 -U /nv/hp10/dcornforth3/scratch/IntermediateSteps/trimmed18.{:s}.{:s} -S /nv/hp10/dcornforth3/scratch/IntermediateSteps/{:s}.mapped_to_otherbugs.SAM --un /nv/hp10/dcornforth3/scratch/IntermediateSteps/{:s}.unmapped_to_otherbugs.{:s}.fastq".format(filename, current_date, filename, filename, current_date), file=f)
      print("bowtie2 -x /nv/hp10/dcornforth3/data/Dan/ref_genome/PAO1_Jan7_2020/PAO1_107 -U /nv/hp10/dcornforth3/scratch/IntermediateSteps/{:s}.unmapped_to_otherbugs.{:s}.fastq -S /nv/hp10/dcornforth3/scratch/IntermediateSteps/{:s}.18mapped_to_PAO1.{:s}.sam".format(filename, current_date, filename, current_date), file=f)
      print("/nv/hp10/dcornforth3/data/Dan/bin/featureCounts -a /nv/hp10/dcornforth3/data/Dan/ref_genome/PAO1_Jan7_2020/Pseudomonas_aeruginosa_PAO1_107.gff -g locus -t CDS -o /nv/hp10/dcornforth3/data/Dan/BlaineOutput/featurecount18.{:s}.{:s}.mapped_to_PAO1.sam /nv/hp10/dcornforth3/scratch/IntermediateSteps/{:s}.18mapped_to_PAO1.{:s}.sam".format(filename, current_date, filename, current_date), file=f)
  with open("submit_file_" + current_date + "_" + str(i)+ ".pbs", 'w') as f:
    print("#PBS -N Kelly_job", file=f)
    print("#PBS -q biocluster-6", file=f)
    print("#PBS -o Kelly_job.output.$PBS_JOBID", file=f)
    print("#PBS -j oe", file=f)
    print("#PBS -l nodes=1:ppn=2", file=f)
    print("#PBS -l walltime=20:00:00", file=f)
    print("#PBS -m abe", file=f)
    print("#PBS -M dcornforth@gmail.com", file=f)

    print("cd $PBS_O_WORKDIR", file=f)
    print("sh mapped_toPAO1." + str(i), file=f)

from math import ceil
import datetime
import os, sys, glob, stat
import re

print("python3 scriptname.py jobname inputfiles_per_job")
lines_per_commandfile = int(sys.argv[2])

files_list=[]
with open("Filestomap.txt", 'r') as f:
  for line in f:
    files_list.append(line[:-1])

output_basename = "mapped_toSaureus."
print(files_list)

now = datetime.datetime.now()
current_date = str(now.hour) + "_" + str(now.month)+"_" + str(now.day)+ "_" + str(now.year)

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
      print("cutadapt -m 25 -a AGATCGGAAGAGCACACGTCTGAACTCCAGTCAC -o /nv/hp10/dcornforth3/scratch/IntermediateSteps/trimmed25.{:s}.{:s} {:s} > /nv/hp10/dcornforth3/scratch/IntermediateSteps/cutadapt25.{:s}.{:s}.txt".format(filename, current_date, filename, filename, current_date), file=f)
      print("bowtie2 -x /nv/hp10/dcornforth3/data/Dan/bin/NON_SA_JAN22_2020/NON_SA_Jan22_2020_FINAL -U /nv/hp10/dcornforth3/scratch/IntermediateSteps/trimmed25.{:s}.{:s} -S /nv/hp10/dcornforth3/scratch/IntermediateSteps/{:s}.mapped_to_otherbugs.SAM --un /nv/hp10/dcornforth3/scratch/IntermediateSteps/{:s}.unmapped_to_otherbugs.{:s}.fastq".format(filename, current_date, filename, filename, current_date), file=f)
      print("bowtie2 -x /nv/hp10/dcornforth3/data/Dan/ref_genome/STAPH_PANGENOME/Saureus_pangenome -U /nv/hp10/dcornforth3/scratch/IntermediateSteps/{:s}.unmapped_to_otherbugs.{:s}.fastq -S /nv/hp10/dcornforth3/scratch/IntermediateSteps/{:s}.25mapped_to_Saureus.{:s}.sam".format(filename, current_date, filename, current_date), file=f)
      print("/nv/hp10/dcornforth3/data/Dan/bin/featureCounts -a /nv/hp10/dcornforth3/data/Dan/ref_genome/STAPH_PANGENOME/Saureus_pangenome.gff -s 1 -g locus_tag -t gene -o /nv/hp10/dcornforth3/data/Dan/StaphModelOutput/featurecount25.{:s}.{:s}.mapped_to_Saureus.sam /nv/hp10/dcornforth3/scratch/IntermediateSteps/{:s}.25mapped_to_Saureus.{:s}.sam".format(filename, current_date, filename, current_date), file=f)
  with open("submit_file_" + current_date + "_" + str(i)+ ".pbs", 'w') as f:
    print("#PBS -N " + sys.argv[1], file=f)
    print("#PBS -q biocluster-6", file=f)
    print("#PBS -o " + sys.argv[1] + ".output.$PBS_JOBID", file=f)
    print("#PBS -j oe", file=f)
    print("#PBS -l nodes=1:ppn=2", file=f)
    print("#PBS -l walltime=40:00:00", file=f)
    print("#PBS -m abe", file=f)
    print("#PBS -M dcornforth@gmail.com", file=f)
    print("cd $PBS_O_WORKDIR", file=f)
    print("sh mapped_toSaureus." + str(i), file=f)
  with open("run_all_submits.sh", 'w') as f:
    for index1 in range(i+1):
      print("qsub submit_file_" + current_date+ "_" + str(index1) + ".pbs", file=f)
### OK and now we will make the "short_tester" which just makes a command file with the very first input file and makes a launcher.
## ok really what we have to consider here is to actually use "head" and make a new short file and just run with that!
os.system('head -1000 ' + files_list[1]+ " > " + output_basename + "short_file_commands")
single_filename = output_basename + "short_file_commands"
with open(output_basename + "short_file_commands", 'w') as f:
  print("module load fastqc/0.11.2", file=f)
  print("module load bowtie2/2.3.2", file=f)
  print("module load R/3.4.3", file=f)
  print("module load gcc/7.3.0", file=f)
  print("module load python/2.7", file=f)
  print("module load cutadapt/1.8.1", file=f)
  print("module load samtools", file=f)
  print("cutadapt -m 25 -a AGATCGGAAGAGCACACGTCTGAACTCCAGTCAC -o /nv/hp10/dcornforth3/scratch/IntermediateSteps/trimmed25.{:s}.{:s} {:s} > /nv/hp10/dcornforth3/scratch/IntermediateSteps/cutadapt25.{:s}.{:s}.txt".format(single_filename, current_date, single_filename, single_filename, current_date), file=f)
  print("bowtie2 -x /nv/hp10/dcornforth3/data/Dan/bin/NON_SA_JAN22_2020/NON_SA_Jan22_2020_FINAL -U /nv/hp10/dcornforth3/scratch/IntermediateSteps/trimmed25.{:s}.{:s} -S /nv/hp10/dcornforth3/scratch/IntermediateSteps/{:s}.mapped_to_otherbugs.SAM --un /nv/hp10/dcornforth3/scratch/IntermediateSteps/{:s}.unmapped_to_otherbugs.{:s}.fastq".format(single_filename, current_date, single_filename, single_filename, current_date), file=f)
  print("bowtie2 -x /nv/hp10/dcornforth3/data/Dan/ref_genome/STAPH_PANGENOME/Saureus_pangenome -U /nv/hp10/dcornforth3/scratch/IntermediateSteps/{:s}.unmapped_to_otherbugs.{:s}.fastq -S /nv/hp10/dcornforth3/scratch/IntermediateSteps/{:s}.25mapped_to_Saureus.{:s}.sam".format(single_filename, current_date, single_filename, current_date), file=f)
  print("/nv/hp10/dcornforth3/data/Dan/bin/featureCounts -a /nv/hp10/dcornforth3/data/Dan/ref_genome/STAPH_PANGENOME/Saureus_pangenome.gff -s 1 -g locus_tag -t gene -o /nv/hp10/dcornforth3/data/Dan/StaphModelOutput/featurecount25.{:s}.{:s}.mapped_to_Saureus.sam /nv/hp10/dcornforth3/scratch/IntermediateSteps/{:s}.25mapped_to_Saureus.{:s}.sam".format(single_filename, current_date, single_filename, current_date), file=f)

with open(single_filename + current_date + "_" + str(i)+ ".pbs", 'w') as f:
  print("#PBS -N " + sys.argv[1], file=f)
  print("#PBS -q biocluster-6", file=f)
  print("#PBS -o Kelly_job.output.$PBS_JOBID", file=f)
  print("#PBS -j oe", file=f)
  print("#PBS -l nodes=1:ppn=2", file=f)
  print("#PBS -l walltime=40:00:00", file=f)
  print("#PBS -m abe", file=f)
  print("#PBS -M dcornforth@gmail.com", file=f)
  print("cd $PBS_O_WORKDIR", file=f)
  print("sh " + single_filename, file=f)


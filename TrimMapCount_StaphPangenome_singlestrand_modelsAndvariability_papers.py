from math import ceil
import datetime
import os, sys, glob, stat
import re

###USAGE
#in the running directory have a file that lists all the files to be processed in Filestomap.txt; "ls *fastq.gz > Filestomap.txt"
#python3 scriptname.py jobname number_of_inputfiles_per_job bowtie2_decoyfiles_directory bowtie2_targetfiles_directory intermediate_files_directory output_directory cutadapt_cutoff featurecounts_binaryfile targetgenome_gff 

#python3 /nv/hp10/dcornforth3/data/Dan/bin/TrimMapCount_StaphPangenome_singlestrand_modelsAndvariability_papers.py ModelPapers 5 /nv/hp10/dcornforth3/data/Dan/bin/NON_SA_JAN22_2020/NON_SA_Jan22_2020_FINAL /nv/hp10/dcornforth3/data/Dan/ref_genome/STAPH_PANGENOME/Saureus_pangenome /nv/hp10/dcornforth3/scratch/IntermediateSteps /nv/hp10/dcornforth3/data/Dan/StaphModelOutput 22 /nv/hp10/dcornforth3/data/Dan/bin/featureCounts /nv/hp10/dcornforth3/data/Dan/ref_genome/STAPH_PANGENOME/Saureus_pangenome.gff

jobname = sys.argv[1]
lines_per_commandfile = int(sys.argv[2])
bowtie2_decoyfiles_directory = sys.argv[3]
bowtie2_targetfiles_directory = sys.argv[4]
intermediate_files_directory = sys.argv[5]
output_directory = sys.argv[6]
cutadapt_cutoff = sys.argv[7]
featurecounts_binaryfile = sys.argv[8]
targetgenome_gff = sys.argv[9]

files_list=[]
with open("Filestomap.txt", 'r') as f:
  for line in f:
    files_list.append(line[:-1])

output_basename = "mapped_to" + bowtie2_targetfiles_directory.split("/")[-1]
print(files_list)

now = datetime.datetime.now()
current_date = str(now.hour) + "_" + str(now.month)+"_" + str(now.day)+ "_" + str(now.year)

for i in range(ceil(len(files_list)/lines_per_commandfile)):
  with open(output_basename+str(i), 'w') as f:
    print("module load bowtie2/2.3.2", file=f)
    print("module load R/3.4.3", file=f)
    print("module load gcc/7.3.0", file=f)
    print("module load python/2.7", file=f)
    print("module load cutadapt/1.8.1", file=f)
    print("module load samtools", file=f)
    for filename in files_list[((i)*lines_per_commandfile):((i)*lines_per_commandfile)+ lines_per_commandfile]:
      print("cutadapt -m " + cutadapt_cutoff + " -a AGATCGGAAGAGCACACGTCTGAACTCCAGTCAC -o " + intermediate_files_directory+ "/trimmed.{:s}.{:s} {:s} > ".format(filename, current_date, filename) +  intermediate_files_directory +"/cutadapt.{:s}.{:s}.txt".format(filename, current_date), file=f)
      print("bowtie2 -x "+ bowtie2_decoyfiles_directory+ " -U " + intermediate_files_directory + "/trimmed.{:s}.{:s} -S ".format(filename, current_date) + intermediate_files_directory + "/{:s}.mapped_to_otherbugs.sam --un ".format(filename) + intermediate_files_directory + "/{:s}.unmapped_to_otherbugs.{:s}.fastq".format(filename, current_date), file=f)
      print("bowtie2 -x " + bowtie2_targetfiles_directory + " -U " + intermediate_files_directory + "/{:s}.unmapped_to_otherbugs.{:s}.fastq -S ".format(filename, current_date) + intermediate_files_directory + "/{:s}.{:s}.{:s}.sam".format(filename, output_basename, current_date), file=f)
      print(featurecounts_binaryfile + " -a " + targetgenome_gff + " -s 1 -g locus_tag -t gene -o " + output_directory + "/featurecount.{:s}.{:s}.{:s} ".format(filename, current_date, output_basename) + intermediate_files_directory + "/{:s}.{:s}.{:s}.sam".format(filename, output_basename, current_date), file=f)
  
  with open("submit_file_" + current_date + "_" + str(i)+ ".pbs", 'w') as f:
    print("#PBS -N " + jobname, file=f)
    print("#PBS -q biocluster-6", file=f)
    print("#PBS -o " + jobname + ".output.$PBS_JOBID", file=f)
    print("#PBS -j oe", file=f)
    print("#PBS -l nodes=1:ppn=2", file=f)
    print("#PBS -l walltime=40:00:00", file=f)
    print("#PBS -m abe", file=f)
    print("#PBS -M dcornforth@gmail.com", file=f)
    print("cd $PBS_O_WORKDIR", file=f)
    print("sh " + output_basename + str(i), file=f)
  with open("run_all_submits.sh", 'w') as f:
    for index1 in range(i+1):
      print("qsub submit_file_" + current_date+ "_" + str(index1) + ".pbs", file=f)

### OK and now we will make the "short_tester" which just makes a command file with the beginning of the very first input file and makes a launcher.
single_filename = "short_file.fastq"

with open('make_shortfile.sh', "w") as shortfilemaker:
    print("gunzip -c " + files_list[0] + " | head -1000 > " + single_filename, file=shortfilemaker)

with open("short_file_commands", 'w') as f:
  print("module load bowtie2/2.3.2", file=f)
  print("module load R/3.4.3", file=f)
  print("module load gcc/7.3.0", file=f)
  print("module load python/2.7", file=f)
  print("module load cutadapt/1.8.1", file=f)
  print("module load samtools", file=f)
  print("sh make_shortfile.sh", file=f)
  print("cutadapt -m " + cutadapt_cutoff + " -a AGATCGGAAGAGCACACGTCTGAACTCCAGTCAC -o " + intermediate_files_directory+ "/trimmed.{:s}.{:s} {:s} > ".format(single_filename, current_date, single_filename) +  intermediate_files_directory +"/cutadapt.{:s}.{:s}.txt".format(single_filename, current_date), file=f)
  print("bowtie2 -x "+ bowtie2_decoyfiles_directory+ " -U " + intermediate_files_directory + "/trimmed.{:s}.{:s} -S ".format(single_filename, current_date) + intermediate_files_directory + "/{:s}.mapped_to_otherbugs.sam --un ".format(single_filename) + intermediate_files_directory + "/{:s}.unmapped_to_otherbugs.{:s}.fastq".format(single_filename, current_date), file=f)
  print("bowtie2 -x " + bowtie2_targetfiles_directory + " -U " + intermediate_files_directory + "/{:s}.unmapped_to_otherbugs.{:s}.fastq -S ".format(single_filename, current_date) + intermediate_files_directory + "/{:s}.{:s}.{:s}.sam".format(single_filename, output_basename, current_date), file=f)
  print(featurecounts_binaryfile + " -a " + targetgenome_gff + " -s 1 -g locus_tag -t gene -o " + output_directory + "/featurecount.{:s}.{:s}.{:s} ".format(single_filename, current_date, output_basename) + intermediate_files_directory + "/{:s}.{:s}.{:s}.sam".format(single_filename, output_basename, current_date), file=f) 

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


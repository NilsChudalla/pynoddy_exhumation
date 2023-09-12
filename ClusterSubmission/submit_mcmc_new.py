import time
from exh_functions import *
from os import system,makedirs

executable = "/home/ho640525/projects/Exhumation/ClusterSubmission/execute_mcmc_new.sh"
created_parser = parser_new()
args = created_parser.parse_args()
n_draws = args.ndraws
if isinstance(args.events, list):
    event = args.events  # Events as a list
elif isinstance(args.events, int):
    event = [args.events]  # Convert single integer to a list
else:
    raise ValueError("Invalid input for 'events' argument")
prop = args.property #property that will be disturbed
std = args.standard_deviation #uncertainty assigned to the property

"""
THE SUBMISSION LOGIC
TO BE CHECKED AND TESTED
"""

"""
1 simulation with z-step 100m and Resolution 16 took ~30min
For a target job time of 5h we can put 
10 simulations with z-step 100m and Resolution 16
Now if we want to run 54 simulations we can do

5 JOBS of 10 simulations each (JOBs groupable by 10)
1 JOB of 4 simulations (modulus JOB)
"""

N_SIMULATIONS_PER_JOB = 10

def generateSubFile(ndraws,events,property,standard_deviation,folder):
    n_jobs, n_job_modulus = ndraws // N_SIMULATIONS_PER_JOB, ndraws % N_SIMULATIONS_PER_JOB

    timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
    this_job_dir = f"/home/ho640525/projects/Exhumation/ClusterSubmission/Logs/{timestamp}/"
    JobSubFile_Groupable = f"/home/ho640525/projects/Exhumation/ClusterSubmission/Sub/MCMCnew_Groupable_{timestamp}_NJOBS{n_jobs}.sh"
    JobSubFile_Modulus = f"/home/ho640525/projects/Exhumation/ClusterSubmission/Sub/MCMCnew_Modulus_{timestamp}_NJOBS1.sh"

    makedirs(this_job_dir,exist_ok=True)    


    
    ## JOB FILE FOR JOBS GROUPABLE BY 10
    if n_jobs != 0:
        with open(JobSubFile_Groupable, 'w') as sout:
            sout.write("#!/bin/bash -l\n")
            sout.write("#SBATCH --job-name=array_job_Groupable\n")
            sout.write("# cap on execution time\n")
            sout.write("#d-hh:mm:ss\n")
            sout.write("#SBATCH --time=2-24:00:00\n")
            sout.write("# this is a hard limit\n")
            sout.write("#SBATCH --mem-per-cpu=4000MB\n")
            sout.write("### Declare the merged STDOUT/STDERR file\n")
            sout.write(f"#SBATCH --output={this_job_dir}/MCMC_goupable_output_%A_%a.txt\n")
            sout.write(f"# {ndraws} jobs will run in this array at the same time\n")
            sout.write(f"#SBATCH --array=1-{n_jobs}\n")
            sout.write("# each job will see a different ${SLURM_ARRAY_TASK_ID}\n")
            sout.write("echo \'now processing task id:: \' ${SLURM_ARRAY_TASK_ID}\n")
            sout.write(f"{executable} {N_SIMULATIONS_PER_JOB} {events} {property} {standard_deviation} {folder}\n")

    if  n_job_modulus!= 0:
        with open(JobSubFile_Modulus, 'w') as sout:
            sout.write("#!/bin/bash -l\n")
            sout.write("#SBATCH --job-name=array_job_Modulus\n")
            sout.write("# cap on execution time\n")
            sout.write("#d-hh:mm:ss\n")
            sout.write("#SBATCH --time=2-24:00:00\n")
            sout.write("# this is a hard limit\n")
            sout.write("#SBATCH --mem-per-cpu=4000MB\n")
            sout.write("### Declare the merged STDOUT/STDERR file\n")
            sout.write(f"#SBATCH --output={this_job_dir}/MCMC_modulus_output_%A_%a.txt\n")
            sout.write(f"# {ndraws} jobs will run in this array at the same time\n")
            sout.write(f"#SBATCH --array=1-1\n")
            sout.write("# each job will see a different ${SLURM_ARRAY_TASK_ID}\n")
            sout.write("echo \'now processing task id:: \' ${SLURM_ARRAY_TASK_ID}\n")
            sout.write(f"{executable} {n_job_modulus} {events} {property} {standard_deviation} {folder}\n")

    if n_jobs!=0 and n_job_modulus!=0:
        return JobSubFile_Groupable, JobSubFile_Modulus

    elif n_jobs!=0 and n_job_modulus==0:
        return JobSubFile_Groupable,None

    elif n_jobs == 0 and n_job_modulus!=0:
        return None,JobSubFile_Modulus
    else:
        print("No jobs to be submitted")
        return None, None

if __name__=="__main__":
    fnameGroup, fnameModul = generateSubFile(ndraws,events,property, standard_deviation,folder)
    for k in [fnameGroup, fnameModul]:
        if k is not None:  system(f"sbatch {k}")

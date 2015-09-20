import os
import psutil

path = "programs"
if not os.path.exists(path):
    raise Exception("{} hasn't been created yet.".format(path))

# Get all the processes currently running
procs = [p for p in psutil.process_iter() if p.is_running()]

for program in os.listdir(path):
    program_path = os.path.join(path, program)
    for proc in procs:
        # if the program is already running don't bother starting it again
        try:
            cmd = proc.cmdline()
            if len(cmd) > 1 and cmd[1] == program_path:
                break
        except psutil.AccessDenied, psutil.NoSuchProcess:
            continue
    # If the program is not running, go ahread and run it in a backgronud process
    else:
        os.system("python {} &".format(program_path))

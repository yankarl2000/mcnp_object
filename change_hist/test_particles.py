import change_hist
import os
import pathlib
import subprocess
import time


orig_file = "orig_data/cubes.i"
nps = 10
particles_num = [9, 23, 34, 37, 44, 58, 64, 93, 100, 117]

def start_computation(file):
    parent_dir = pathlib.Path().resolve()
    directory = file.partition("/")[0]
    path = os.path.join(parent_dir, directory)
    os.chdir(path)
    file = file.partition("/")[2]
    #p = subprocess.Popen('cmd /c "{} > some.txt"'.format("ping -n 20 127.0.0.1"))
    p = subprocess.Popen('cmd /c "{} > mcnp_output.txt"'.format("mcnp inp="+file))
    os.chdir(parent_dir)
    return p

processes = []
for particle_num in particles_num:
    file = change_hist.make_folders(orig_file, nps, particle_num)
    processes.append(start_computation(file))

counter = 0
print(time.ctime())
print("finished {} processes".format(counter))
while True:
    c = 0
    for p in processes:
        if p.poll() == 0: c+=1
    if counter < c:
        counter = c
        print("\nfinished {} processes".format(c))
    if c == len(particles_num):
        print(time.ctime())
        break
    print(".", end="")
    time.sleep(5)
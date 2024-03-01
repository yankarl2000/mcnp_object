'''
открываем файл после рассчёта
изменяем nps = 10 и hist в соответствии с потерянными частицами из text_for_SC
сохраняем полученный файл в папку test_particle_(particle_number)
начинаем рассчёт
'''
import os
import pathlib
import shutil


# сохраняем часть файла с данными о количестве частиц и начала рассчёта hist
# для последующего изменения
def get_last_lines(file, n):
    with open(file, "r", encoding = "utf-8") as file:
        lines = file.readlines()
        c = len(lines)
        return lines[c - n:c]

# удаляем часть файла с данными о количестве частиц и начала рассчёта hist
def del_last_lines(file, n):
    with open(file, "r+", encoding = "utf-8") as file:
        file.seek(0, os.SEEK_END)
        pos = file.tell() - 1
        counter = 0
        while pos > 0 and counter < n:
            c = file.read(1)
            if c == "\n":
                counter+=1
            pos -= 2
            file.seek(pos, os.SEEK_SET)
        if pos > 0:
            file.seek(pos+3, os.SEEK_SET)
            file.truncate()
        else: print("too short file")

# изменяем данные nps и hist
def insert_nps_hist(ending, nps, hist):
    for i in range(len(ending)):
        if ending[i].startswith("nps"):
            ending[i] = "nps {}\n".format(nps)
        if ending[i].startswith("rand"):
            ending[i] = "rand  gen=1  seed=19073486328125  stride=152917  hist={}".format(hist)
    return ending

def make_folders(orig_file, nps, particle_number):
    number_strings = 5
    hist = particle_number - 3
    ending = get_last_lines(orig_file, number_strings)
    ending = insert_nps_hist(ending, nps, hist)
    parent_dir = pathlib.Path().resolve()
    directory = "particle_test_N_"+str(particle_number)
    os.mkdir(os.path.join(parent_dir, directory))
    fn = orig_file.split("/")[-1]
    fn = fn.partition(".")
    fn = fn[0]+"("+str(particle_number)+")"+fn[1]+fn[2]
    new_filename = directory+"/"+fn
    shutil.copyfile(orig_file, new_filename)
    del_last_lines(new_filename, number_strings)
    with open(new_filename, 'a') as f:
        f.writelines(ending)
    return new_filename
'''
out_claster.py filename?.object

? - any digit for no one file
all particles writed in file text_for_SC.txt in the same folder

printed number of particles in each file
'''

import pathlib
import sys
from os.path import isfile
from string import digits

def write_point(full_path):
    with open(full_path) as cur_file:
        lines = cur_file.readlines()
        count = 0
        index_xyz = []
        for ID, line in enumerate(lines):
            if line.strip().startswith("x,y,z coordinates"):
                count += 1
                index_xyz.append(ID)
        print('Количество потерянных частиц = ', count)
        # print(index_xyz)
        # ------ знаем индексы строк, теперь вычленяем две последние координаты ------------
        xyz_coor = []
        for index in index_xyz:
            # print(ID)

            lines_cur = lines[index]
            while "  " in lines_cur:  # оставляем только по одному пробелу
                lines_cur = lines_cur.replace("  ", " ")
            x_coor = lines_cur.strip().split(' ')[2]
            y_coor = lines_cur.strip().split(' ')[3]
            z_coor = lines_cur.strip().split(' ')[4]

            x_coor = float(x_coor)
            y_coor = float(y_coor)
            z_coor = float(z_coor)

            xyz_coor.append(x_coor)
            xyz_coor.append(y_coor)
            xyz_coor.append(z_coor)

            # -------- задаем имя для каждой точки согласно значению в history no. 53924800
            lines_cur = lines[index - 8]
            while "  " in lines_cur:  # оставляем только по одному пробелу
                lines_cur = lines_cur.replace("  ", " ")

            point_name = int(lines_cur.strip().split(' ')[-1])
            xyz_coor.append(point_name)
            # ---------------------------------------------------------------------

    return xyz_coor


def create_script(path_file, xyz_coor):
    ii = 0
    idid = 0
    script = ''

    while ii < len(xyz_coor):
        create_line = """# Sketch Point
point = Point.Create(CM({}), CM({}), CM({}))
result = SketchPoint.Create(point)
# EndBlock
# Переименовать 'Точка'
selection = Selection.Create(GetRootPart().Curves[{}])
result = RenameObject.Execute(selection,"{}")
# EndBlock
""".format(xyz_coor[ii], xyz_coor[ii+1], xyz_coor[ii+2], idid, xyz_coor[ii+3])
        ii += 4
        idid += 1
        script += create_line

    name_wrire_file = path_file + '\\text_for_SC.txt'
    with open(name_wrire_file, 'a', encoding='utf-8') as wr_file:
        wr_file.write(script)


if __name__ == '__main__':
    #print(sys.argv[1])
    path_file = str(pathlib.Path().resolve())+ '\\'  # --------- ПУТЬ К ФАЙЛУ ------------
    name_file = sys.argv[1]           # --------- ИМЯ ФАЙЛА ---------------
    full_path = path_file + name_file
    if name_file.find('?') != -1:
        for d in digits:
            some_path = path_file + name_file.replace('?', d)
            if isfile(some_path):
                xyz_coor = write_point(some_path)
                create_script(path_file, xyz_coor)
    else:
        xyz_coor = write_point(full_path)
        create_script(path_file, xyz_coor)
    
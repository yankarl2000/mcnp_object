import pathlib
import os

def write_point(full_path):
    with open(full_path) as cur_file:
        lines = cur_file.readlines()
        count = 0
        index_xyz = []
        for ID, line in enumerate(lines):
            if line.strip().startswith("x,y,z coordinates"):
                count += 1
                index_xyz.append(ID)
        print('Количество точек = ', count)
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
    with open(name_wrire_file, 'w', encoding='utf-8') as wr_file:
        wr_file.write(script)


if __name__ == '__main__':
    path = str(pathlib.Path().resolve())

    # xyz_coor = write_point(full_path)
    # create_script(path_file, xyz_coor)
    for dirname in os.listdir(os.getcwd()):
        #dir = os.path.join('/home/user/workspace', directories)
        #os.chdir(dir)
        #current = os.path.dirname(dir)
        #new = str(current).split("-")[0]
        if dirname.partition("_")[0] == "particle":
            num = int(dirname.split("_")[-1])
            full_path = path + '\\' + dirname + "\\" + "outp"
            print("particle number: "+str(num), end="  --  ")
            xyz_coor = write_point(full_path)
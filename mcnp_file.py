from mcnp_geometry import Cell, Surface

class Ifile:
    def __init__(self, filename):
        self.filename = filename
        empty_lines = 0
        title_card = ''
        cell_line = ''
        cells = []
        surface_line = ''
        surfaces = []
        data_section = ''
        (old_comment, comment) = ('', '')
        block = "title_card"
        with open(filename, 'r') as file:
            for line in file.readlines():
                if line.strip() == '':
                    empty_lines += 1
                    continue
                if (block == "title_card" and
                    line[0].isdigit() and
                    len(line.split())>2):
                    block = "cells"
                    cell_line = line
                    continue
                if block == "cells" and empty_lines == 1:
                    cells.append(Cell(old_comment + cell_line + comment))
                    (old_comment, comment) = ('', '')
                    block = "surfaces"
                if block == "surfaces" and empty_lines == 2:
                    surfaces.append(Surface(old_comment + surface_line + comment))
                    block = "data_section"
                if block == "title_card":
                    title_card += line
                elif block == "cells":
                    if line[0].isdigit():
                        cells.append(Cell(old_comment + cell_line))
                        (old_comment, comment) = (comment, '')
                        cell_line = line
                    elif line.startswith('C') or line.startswith('c'):
                        comment += line
                    else:
                        cell_line += line
                elif block == "surfaces": 
                    if line[0].isdigit() and surface_line != '':
                        surfaces.append(Surface(old_comment + surface_line))
                        (old_comment, comment) = (comment, '')
                        surface_line = line
                    elif line.startswith('C') or line.startswith('c'):
                        if surface_line == '': old_comment += line
                        else: comment += line
                    else:
                        surface_line += line
                elif block == "data_section":
                    data_section += line
        self.title_card = title_card
        self.cells = cells
        self.surfaces = surfaces
        self.data_section = data_section
    def find_similar_surfaces(self):
        print("Searching for similar surfaces:")
        groups = []
        for i in range(len(self.surfaces)):
            printProgressBar(i+1, len(self.surfaces))
            for j in range(i+1, len(self.surfaces)):
                surf_i = self.surfaces[i]
                surf_j = self.surfaces[j]
                new_group = True
                if surf_i.similar_with(surf_j):
                    for i1 in range(len(groups)):
                        for j1 in range(len(groups[i1])):
                            if groups[i1][j1].number == surf_i.number:
                                if not surf_j.number in [s.number for s in groups[i1]]:
                                    groups[i1] += [surf_j]
                                new_group = False
                    if new_group:
                        groups.append([surf_i, surf_j])
        if len(groups) == 0: print("not found similar surfaces")
        for i in range(len(groups)):
            print(f"group {i+1}: " + " ".join([str(s.number) for s in groups[i]]))
        return groups
    def replace_similar_surfaces(self):
        groups = self.find_similar_surfaces()
        for i in range(len(groups)):
            if i % 100 == 0: print("Прогресс замены: "+str(round(100*i/len(groups)))+"%")
            for g in groups[i][1:]:
                for cell in self.cells:
                    cell.replace(g, groups[i][0])
        counter = 0
        new_surfaces = []
        for i in range(len(self.surfaces)):
            if i % 100 == 0: print("Прогресс удаления: "+str(round(100*i/len(self.surfaces)))+"%")
            add_surf = True
            for group in groups:
                for g in group[1:]:
                    if self.surfaces[i] == g:
                        counter += 1
                        add_surf = False
            if add_surf: new_surfaces.append(self.surfaces[i])
        self.surfaces = new_surfaces
        print("удалено {} поверхностей".format(counter))
    def write(self, filename):
        with open(filename, 'w') as file:
            file.write(self.title_card)
        with open(filename, 'a') as file:
            file.write(str(self.cells[0]))
            for i in range(1, len(self.cells)):
                file.write(str(self.cells[i]))
            file.write('\n')
            for s in self.surfaces:
                file.write(str(s))
            file.write('\n' + self.data_section)
    def change(self, old, new):
        pass

def printProgressBar(iteration, total, prefix = '', suffix = '', decimals = 1, length = 50, fill = '█', printEnd = "\r"):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    if iteration == total: 
        print()
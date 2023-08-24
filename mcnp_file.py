from mcnp_geometry import Cell, Surface, MNEMONICS

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
        block = "title_card"
        with open(filename, 'r') as file:
            for line in file.readlines():
                if line.startswith("C") or line.startswith("c"):
                    if block == "title_card": title_card += line
                    else: continue
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
                    cells.append(Cell(cell_line))
                    block = "surfaces"
                    surface_line = line
                    continue
                if block == "surfaces" and empty_lines == 2:
                    surfaces.append(Surface(surface_line))
                    block = "data_section"
                if block == "title_card":
                    title_card += line
                elif block == "cells":
                    if line[0].isdigit():
                        cells.append(Cell(cell_line))
                        cell_line = line
                    else:
                        cell_line += line
                elif block == "surfaces":
                    if line[0].isdigit():
                        surfaces.append(Surface(surface_line))
                        surface_line = line
                    else:
                        surface_line += line
                elif block == "data_section":
                    data_section += line
        self.title_card = title_card
        self.cells = cells
        self.surfaces = surfaces
        self.data_section = data_section
    def find_similar_surfaces(self):
        groups = []
        for i in range(len(self.surfaces)):
            if i % 300 == 0: print("Прогресс поиска: "+str(round(100*i/len(self.surfaces)))+"%")
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
        print("-----------------------")
        print(groups)
        print("-----------------------")
    def replace_similar_surfaces(self):
        groups = []
        for i in range(len(self.surfaces)):
            if i % 300 == 0: print("Прогресс поиска: "+str(round(100*i/len(self.surfaces)))+"%")
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
                file.write("\n" + str(self.cells[i]))
            file.write("\n")
            for s in self.surfaces:
                file.write("\n" + str(s))
            file.write("\n\n" + self.data_section)
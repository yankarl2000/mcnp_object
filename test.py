import mcnp_file as mf

i_file = mf.Ifile("cubes.i")
print(i_file.title_card, end='')
print("+++++++++++++++++++++++")
for c in i_file.cells:
    print(c.text, end='')
    print("+++++++++++++++++++++++")
for s in i_file.surfaces:
    print(s.text, end='')
    print("+++++++++++++++++++++++")
print(i_file.data_section)
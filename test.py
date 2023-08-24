import mcnp_file as mf

filename = "new_UPP04.i"

i_file = mf.Ifile(filename)
i_file.find_similar_surfaces()
#i_file.write("new_UPP04.i")
'''
добавить outclaster и change_hist post pre processing
сделать скрипт замены всех совпадающих поверхностей и удаления лишних с сохранением в файл
с комментариями $ и C и без
'''
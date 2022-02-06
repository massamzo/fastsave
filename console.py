import os

def get_list(folder):
    lista = []
    for r, dir, file in os.walk(folder):
        fol = []
        files = []
        for names in dir:
            fol.append(names)

        for name in file:
            files.append(name)

        lista.append(fol)
        lista.append(files)
        break
    
    return lista
        




import os


def adapt_to_excel(old_file):
    old_f = open(old_file, 'r', encoding='utf-8-sig')
    new_f = open(old_file.rsplit('.', 1)[0]+'-OK.csv', 'w', encoding='utf-8-sig')
    for line in old_f:
        cells = line.split(';')
        new_line = ''
        for cell in cells:
            aux_cell = cell.strip().replace('"', '')
            new_line += ('="'+aux_cell+'";')
        new_f.write(new_line+'\n')
    old_f.close()
    new_f.close()
    if os.path.exists(old_file):
        os.remove(old_file)


if __name__ == '__main__':
    adapt_to_excel('pessoas.csv')

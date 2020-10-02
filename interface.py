import PySimpleGUI as sg
from os.path import isdir, isfile, dirname
from os import system, startfile
from sys import exit as sys_exit

# Gimmick
import sys
import os
from ctypes import windll, byref, create_unicode_buffer


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


windll.gdi32.AddFontResourceExW(byref(create_unicode_buffer(resource_path("media/Quicksand-Regular.ttf"))), 0x20, 0)
windll.gdi32.AddFontResourceExW(byref(create_unicode_buffer(resource_path("media/Quicksand-SemiBold.ttf"))), 0x20, 0)
# Gimmick

background = "#ffffff"
sg.SetOptions(background_color=background, element_background_color=background,
              icon=resource_path("media/consulta.ico"), font=("Quicksand", 14))
sg.ChangeLookAndFeel('Reddit')


def get_consulta_paths():
    layout = [[sg.Image(resource_path("media/consulta-back.png"), pad=((130, 0), (0, 0))),
               sg.Text("Ajuda", pad=((110, 0), (0, 110)), text_color="#34B7F1", click_submits=True, key="instructions",
                       tooltip="Indique o arquivo .db de origem e o tipo da consulta.\nNo final, será gerado um arquivo csv",
                       font=("Quicksand SemiBold", 12))],
              [sg.Text('Arquivo SQL:')],
              [sg.Input(key="input_file", size=(32, 0), font="Quicksand 12"),
               sg.FileBrowse(button_text="Selecionar", key="select_db", font="Quicksand 11",
                             pad=((40, 0), (0, 0)), file_types=(("ALL Files", "*.db"),),)],
              [sg.Text(" "*70, font="Quicksand 10", key="error_1")],
              [sg.Text('Arquivo .csv com CNPJs:')],
              [sg.Input(key="csv_file", size=(32, 0), font="Quicksand 12"),
               sg.FileBrowse(button_text="Selecionar", key="select_csv", font="Quicksand 11",
                             pad=((40, 0), (0, 0)), file_types=(("ALL Files", "*.csv"),), )],
              [sg.Text(" " * 70, font="Quicksand 10", key="error_2")],
              [sg.Text('_' * 70, font="Arial 11")],
              [sg.Text('Destino dos resultados:')],
              [sg.Input(key="output_folder", size=(32, 0), font="Quicksand 12"),
               sg.FolderBrowse(button_text="Selecionar", key="select_folder",
                               font="Quicksand 11", pad=((40, 0), (0, 0)))],
              [sg.Text(" "*70, font="Quicksand 10", key="error_3")],
              [sg.Button(pad=((170, 0), (6, 0)), button_text="CONSULTAR", border_width=2, key="search")]]

    window = sg.Window('Consulta CNPJ', layout, size=(500, 620)).Finalize()
    window["instructions"].Widget.config(cursor="hand2")
    window["select_db"].Widget.config(cursor="hand2")
    window["select_csv"].Widget.config(cursor="hand2")
    window["select_folder"].Widget.config(cursor="hand2")

    while True:
        event, values = window.Read()
        if event in (None, "Cancelar"):
            window.close()
            sys_exit()

        if event == "instructions":
            # TODO: show help
            continue

        try:
            if isfile(values["input_file"]):
                window["error_1"].update("")
            if not isfile(values["input_file"]):
                window["error_1"].update("Selecione o banco de dados", text_color="red")
        except TypeError:
            window["error_1"].update("Selecione o banco de dados", text_color="red")

        try:
            if isfile(values["csv_file"]):
                window["error_2"].update("")
            if not isfile(values["csv_file"]):
                window["error_2"].update("Selecione um arquivo csv válido", text_color="red")
        except TypeError:
            window["error_2"].update("Selecione um arquivo csv válido", text_color="red")

        try:
            if isdir(values["output_folder"]):
                window["error_3"].update("")
            if not isdir(values["output_folder"]):
                window["error_3"].update("Selecione uma pasta de destino válida", text_color="red")
        except TypeError:
            window["error_3"].update("Selecione uma pasta de destino válida", text_color="red")

        if isfile(values["csv_file"]) and not isdir(values["output_folder"]):
            window["output_folder"].update(dirname(values["csv_file"]))
            window["error_3"].update("Confirme a pasta de destino", text_color="red")

        if isfile(values["input_file"]) and isfile(values["csv_file"]) and isdir(values["output_folder"]):
            break

    window.close()
    try:
        return (values["input_file"], values["csv_file"], values["output_folder"])
    except Exception:
        reading_error_window()


def reading_error_window(txt_error=""):
    layout = [[sg.Column([[sg.Text("⚠", font="Arial 34", text_color="red", pad=((0, 0), (11, 0)))]], scrollable=False),
               sg.Column([[sg.Text(f"Ocorreu um erro {txt_error}")]], scrollable=False, pad=((0, 0), (0, 20)))]
              ]

    error_window = sg.Window("Erro", layout).Finalize()

    event, values = error_window.Read()
    while event not in (None, "close"):
        event, values = error_window.Read()
        continue
    error_window.close()
    sys_exit()


def final_confirmation_window(final_folder):
    layout = [[sg.Column([[sg.Text("✔", font="Arial 48", text_color="green", pad=((0, 0), (11, 0)))]], scrollable=False),
               sg.Column([[sg.Text("Arquivos criados com sucesso!", font=("Quicksand SemiBold", 20))]],
                                   scrollable=False, pad=((0, 0), (15, 0)))],
              [sg.Button(key="open_folder", border_width=2,
                         button_text="ABRIR ARQUIVOS", pad=((260, 0), (0, 10))),
               sg.Button(key="close", border_width=2,
                         button_text="FECHAR", pad=((15, 0), (0, 10)))
               ]
             ]

    confirmation_window = sg.Window("Consulta CNPJ", layout).Finalize()
    confirmation_window["open_folder"].Widget.config(cursor="hand2")
    confirmation_window["close"].Widget.config(cursor="hand2")

    event, values = confirmation_window.Read()
    while event not in (None, "close"):
        if event == "open_folder":
            try:
                startfile(final_folder)
                break
            except Exception:
                try:
                    system("open " + final_folder)
                    break
                except Exception:
                    confirmation_window.close()
                    sys_exit()
        event, values = confirmation_window.Read()
    confirmation_window.close()
    sys_exit()


if __name__ == "__main__":
    print(get_consulta_paths())
    reading_error_window("Algum erro")
    final_confirmation_window("Algum arquivo")

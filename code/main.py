#librerias
from tkinter import filedialog,messagebox
from PIL import Image,ImageTk
#from pymkv import MKVFile
import tkinter as tk
import subprocess
import threading
import argparse
import platform
import pygame
import shutil
import time
import json
#import cv2
import os

#scripts para otros procesos
import menus
from mavm import MaVM

def install_w():
    if shutil.which("ffmpeg") is None:
        print("Install FFmpeg")
        exit()
    elif shutil.which("mkvmerge") is None:
        print("Install MKVToolNix")
        exit()

def install_lin(a=None):
    if not(a==None):
        if os.path.exists("/etc/os-release"):
            with open("/etc/os-release") as file:
                data = file.read()
            if "Ubuntu" in data or "Debian" in data:
                subprocess.run(["sudo","apt-get","install",a])
            elif "Fedora" in data or "Red Hat" in data:
                subprocess.run(["sudo","dnf","install",a])
            elif "Arch" in data:
                subprocess.run(["sudo","pacman","-S",a])
        else:
            exit()

if platform.system() == "Windows":
    intatall_w()
elif platform.system() == "Darwin":
    install_w()
else:
    if shutil.which("ffmpeg") is None:
        install_lin("ffmpeg")
    if shutil.which("mkvmerge") is None:
        install_lin("mkvtoolnix")

pygame.mixer.init()
try:
    shutil.rmtree(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp'))   #borra la carpeta completa
    os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp'))
except:
    os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp'))

try:
    shutil.rmtree(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp_frames'))   #borra la carpeta completa
    os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp_frames'))
except:
    os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp_frames'))

class ventana:
    def __init__(self, ventana_tk, file):
        #ventana
        self.ventana_tk = ventana_tk
        self.ventana_tk.title("MaVM player")
        self.ventana_tk.geometry("800x450")
        self.ventana_tk.minsize(800,450)
        self.ventana_tk.config(bg='gray')
        #self.ventana_tk.protocol("WM_DELETE_WINDOW", self.exit)


        #variables
        self.file = file
        self.raiz_proyecto = os.path.dirname(os.path.abspath(__file__))
        print(self.raiz_proyecto)
        self.carpeta_temporal = os.path.join(self.raiz_proyecto, 'temp')
        self.carpeta_temporal_frames = os.path.join(self.raiz_proyecto, 'temp_frames')
        self.resolution_menu = [False, None]
        self.detectar_botones = ""
        self.objetos_menu = []
        self.video_repr = False
        self.used_vid = {}
        self.menu_r = True

        self.pista_audio_name = tk.StringVar(self.ventana_tk)
        self.pista_audio_name.set("none")
        self.pista_video_name = tk.StringVar(self.ventana_tk)
        self.pista_video_name.set("none")


        #objetos
        #abrir un archivo
        archivos = tk.Button(self.ventana_tk, text="files", command=self.archivos_ventana)
        archivos.place(x=0,y=0,width=80,height=16)

        self.reproductor = tk.Frame(self.ventana_tk, bg='black')
        self.reproductor.place(x=0,y=20)

        self.atras_boton = tk.Button(self.ventana_tk, text="<-10s", command=self.detectar_botones_fun_atra)
        self.atras_boton.place(x=0,y=430,width=20,height=16)

        self.adelante_boton = tk.Button(self.ventana_tk, text="10s->", command=self.detectar_botones_fun_adel)
        self.adelante_boton.place(x=780,y=430,width=20,height=16)

        self.play_boton = tk.Button(self.ventana_tk, text="play/pause", command=self.detectar_botones_fun_stop)
        self.play_boton.place(x=780,y=430,width=20,height=16)

        self.pista_audio_menu = tk.OptionMenu(self.ventana_tk, self.pista_audio_name, "none")
        self.pista_audio_menu.place(x=780,y=430,width=20,height=16)

        self.pista_audio_text = tk.Label(self.ventana_tk, text="audio>")

        self.pista_video_menu = tk.OptionMenu(self.ventana_tk, self.pista_video_name, "none")
        self.pista_video_menu.place(x=760,y=430,width=20,height=16)

        self.pista_video_text = tk.Label(self.ventana_tk, text="video>")

        self.ventana_tk.after(50, self.actalizar_medidas)


        #codigo
        if self.file:
            self.ventana_tk.after(100, self.repdorucir)
    
    def exit(self):
        exit()

    def reset_botones_fun(self):
        self.detectar_botones = ""

    def detectar_botones_fun_atra(self):
        self.detectar_botones = "atras"

    def detectar_botones_fun_adel(self):
        self.detectar_botones = "adelante"

    def detectar_botones_fun_stop(self):
        self.detectar_botones = "stop-play"

    def archivos_ventana(self):
        self.file = filedialog.askopenfilename(title='buscar video MaVM', filetypes=(('video MaVM', '*.mavm'),('todos los archivos', '*.*')))
        print(self.file)
        self.repdorucir()

    def actalizar_medidas(self):
        try:
            ancho_ventana = self.ventana_tk.winfo_width()
            alto_ventana = self.ventana_tk.winfo_height()
            
            interfaz_alto = max(self.ventana_tk.winfo_height()*.05,16)
            interfaz_ancho = max(self.ventana_tk.winfo_width()*.0625,50)
            play_ancho = max(self.ventana_tk.winfo_width()*.1875,150)

            self.reproductor.config(width=ancho_ventana,height=alto_ventana-(20+4+interfaz_alto))

            self.atras_boton.place(x=int(ancho_ventana/6)-interfaz_ancho/2,y=alto_ventana-interfaz_alto,width=interfaz_ancho,height=interfaz_alto)

            self.play_boton.place(x=int(ancho_ventana/3)-play_ancho/2,y=alto_ventana-interfaz_alto,width=play_ancho,height=interfaz_alto)

            self.adelante_boton.place(x=int(3*ancho_ventana/6)-interfaz_ancho/2,y=alto_ventana-interfaz_alto,width=interfaz_ancho,height=interfaz_alto)

            self.pista_audio_menu.place(x=int(ancho_ventana)-interfaz_ancho*2,y=alto_ventana-interfaz_alto,width=interfaz_ancho*2,height=interfaz_alto)

            self.pista_audio_text.place(x=int(ancho_ventana)-interfaz_ancho*3,y=alto_ventana-interfaz_alto,width=interfaz_ancho*1,height=interfaz_alto)

            self.pista_video_menu.place(x=int(ancho_ventana)-interfaz_ancho*5,y=alto_ventana-interfaz_alto,width=interfaz_ancho*2,height=interfaz_alto)

            self.pista_video_text.place(x=int(ancho_ventana)-interfaz_ancho*6,y=alto_ventana-interfaz_alto,width=interfaz_ancho*1,height=interfaz_alto)

            self.reproductor.update_idletasks()
        except:
            pass
        if self.menu_r:
            self.ventana_tk.after(10, self.actalizar_medidas)

    def start(self):
        for widget in self.reproductor.winfo_children():
            widget.destroy()  #elimina cada widget
        
        metadata_path   = self.contenido_dat['metadata.json']
        start_menu_path = self.contenido_dat['start.json']
        
        metadata_file = open(metadata_path, 'r')
        metadata_text = metadata_file.read()
        metadata_json = json.loads(metadata_text)
        metadata_file.close()

        start_menu_file = open(start_menu_path, 'r')
        start_menu_text = start_menu_file.read()
        start_menu_json = json.loads(start_menu_text)
        start_menu_file.close()

        self.video_mavm_version = metadata_json["mavm_version"]
        if not(self.video_mavm_version in ['v.2.1.0','v.2.2.0','v.3.0.0']):
            messagebox.showerror("File version error", "The file version is not supported. This program only supports versions 2.1.0 to 3.0.0")
            exit()
        print(self.video_mavm_version)

        version_compatible = menus.version_formato(self.video_mavm_version)[0]
        print(version_compatible)

        descripcion = tk.Label(self.reproductor,text=metadata_json["descripcion"]["text"],fg="#ffffff",background="black")
        descripcion.place(x=self.reproductor.winfo_width()//2-4*len(metadata_json["descripcion"]["text"]),y=self.reproductor.winfo_height()//2)
        self.reproductor.update_idletasks()
        print(metadata_json["descripcion"]["text"])

        for i in range(1,metadata_json["descripcion"]["duration"]*100):
            time.sleep(1/100)
        
        self.menu(start_menu_json)

    def menu(self, menu_json):
        try:
            pygame.mixer.pause()
        except:
            try:
                for i in list(self.used_vid.keys()):
                    try:
                        self.used_vid[i][3].pause()
                    except:
                        pass
            except:
                pass
        self.used_vid = {}
        self.loop_comandos_on = False
        self.objetos_menu = []
        y = True
        for widget in self.reproductor.winfo_children():
            try:
                if widget is self.espacio_mv:
                    y = False
                else: 
                    widget.destroy()  #elimina cada widget
            except:
                widget.destroy()  #elimina cada widget
        
        #crear espacio para menu y video

        if y:
            self.espacio_mv = tk.Frame(self.reproductor, bg='white')
            self.espacio_mv.place()
        else:
            for widget_mv in self.espacio_mv.winfo_children():
                widget_mv.destroy()
        
        menu_dat = menus.version_formato(self.video_mavm_version)
        lista_comandos = menu_dat[1](menu_json).lista_comandos
        print("lc",lista_comandos)

        self.resolution_menu = [True, lista_comandos["resolucion"]]
        self.menu_resize()

        #self.objetos_menu = 
        #comando[1]["imagen"]
        print("start:",lista_comandos["start"])
        for comando in lista_comandos["start"]:
            print("lcc", comando)
            t = self.comnado_ejecutar(comando, self.espacio_mv)
            #time.sleep(t)
            time.sleep(16/1000)
        
        print(lista_comandos["loop"])
        if 0 == len(lista_comandos["loop"]):
            pass
        else:
            print("loop:",lista_comandos["loop"])
            self.loop_comandos_on = True
            self.menu_loop(lista_comandos["loop"])

    def menu_loop(self, lista_comandos):
        if self.loop_comandos_on:
            for comando in lista_comandos:
                if self.loop_comandos_on:
                    #print("lcc", comando)
                    t = self.comnado_ejecutar(comando, self.espacio_mv)
                    #time.sleep(t)
                    time.sleep(t)
                    if not(self.loop_comandos_on):
                        break
            time.sleep(10/1000)
            #threading.Thread(target=lambda: self.menu_loop(lista_comandos)).start()
            self.ventana_tk.after(10, lambda: self.menu_loop(lista_comandos))
        else:
            pass

    def comnado_ejecutar(self, comando, v):
            t = 16/1000
            #print("contenido comando:", comando)
            if comando[0] == "image":
                print(comando[1]["imagen"])
                imagen_file = Image.open(self.contenido_dat[comando[1]["imagen"]])
                imagen = ImageTk.PhotoImage(imagen_file)
                if "create" in comando[1].keys():
                    self.objetos_menu.append({"id":comando[1]["create"],"objeto":tk.Label(v, image=imagen), "cordenadas":comando[1]["coordinates"], "imagen":imagen_file})
                    self.objetos_menu[len(self.objetos_menu)-1]["objeto"].image = imagen
                    self.objetos_menu[len(self.objetos_menu)-1]["objeto"].place(x=0,y=0)
                    print(self.objetos_menu[len(self.objetos_menu)-1])
                elif "edit" in comando[1].keys():
                    print("Buscando objeto con id:", comando[1]["edit"])
                    for i in range(len(self.objetos_menu)-1):
                        if "id" in self.objetos_menu[i].keys():
                            if self.objetos_menu[i]["id"] == comando[1]["edit"]:
                                print("Objeto encontrado:", self.objetos_menu[i])
                                self.objetos_menu[i]["cordenadas"] = comando[1]["coordinates"]
                                self.objetos_menu[i]["imagen"] = imagen_file
                                self.objetos_menu[i]["objeto"].place(x=0,y=0)
                                print(self.objetos_menu[i])
            elif comando[0] == "text":
                self.objetos_menu.append({"objeto": tk.Label(v,text=comando[1]["text"],fg="#808080"), "cordenadas":comando[1]["coordinates"]})
            elif comando[0] == "button":
                if "create" in comando[1].keys():
                    if "image" in comando[1].keys():
                        if "command" in comando[1].keys():
                            print(comando[1]["image"])
                            print(self.contenido_dat[comando[1]["image"]])
                            imagen_file = Image.open(self.contenido_dat[comando[1]["image"]])
                            imagen = ImageTk.PhotoImage(imagen_file)

                            print(comando[1]["coordinates"])

                            self.objetos_menu.append({"id":comando[1]["create"],
                            "objeto":tk.Label(self.espacio_mv, image=imagen), "cordenadas":comando[1]["coordinates"],"imagen":imagen_file})

                            self.objetos_menu[len(self.objetos_menu)-1]["objeto"].image = imagen
                            self.objetos_menu[len(self.objetos_menu)-1]["objeto"].bind("<Button-1>", lambda event, cmd=comando[1]["command"]: self.ejecutar_boton(cmd))

                            self.objetos_menu[len(self.objetos_menu)-1]["objeto"].place()
                        else:
                            print(comando[1]["image"])
                            print(self.contenido_dat[comando[1]["image"]])
                            imagen_file = Image.open(self.contenido_dat[comando[1]["image"]])
                            imagen = ImageTk.PhotoImage(imagen_file)

                            self.objetos_menu.append({"id":comando[1]["create"],
                            "objeto":tk.Label(self.espacio_mv, image=imagen), "cordenadas":comando[1]["coordinates"],"imagen":imagen_file})

                            self.objetos_menu[len(self.objetos_menu)-1]["objeto"].place()

                        if "command4selection" in comando[1].keys():
                            self.objetos_menu[len(self.objetos_menu)-1]["objeto"].bind("<Enter>", lambda e: self.ejecutar_boton(comando[1]["command4selection"]))
                            self.objetos_menu[len(self.objetos_menu)-1]["objeto"].place()
                        if "command4no_selection" in comando[1].keys():
                            self.objetos_menu[len(self.objetos_menu)-1]["objeto"].bind("<Leave>", lambda e: self.ejecutar_boton(comando[1]["command4no_selection"]))
                            self.objetos_menu[len(self.objetos_menu)-1]["objeto"].place()
                    else:
                        self.objetos_menu.append({"id":comando[1]["create"],"objeto":tk.Button(v, text=comando[1]["title"],bg=f'#{comando[1]["color"][0]:02x}{comando[1]["color"][1]:02x}{comando[1]["color"][2]:02x}'), "cordenadas":comando[1]["coordinates"]})
                        self.objetos_menu[len(self.objetos_menu)-1]["objeto"].place()

                        if "command" in comando[1].keys():
                            self.objetos_menu[len(self.objetos_menu)-1]["objeto"].config(command=lambda: self.ejecutar_boton(comando[1]["command"]))
                        if "command4selection" in comando[1].keys():
                            self.objetos_menu[len(self.objetos_menu)-1]["objeto"].bind("<Enter>", lambda e: self.ejecutar_boton(comando[1]["command4selection"]))
                        if "command4no_selection" in comando[1].keys():
                            self.objetos_menu[len(self.objetos_menu)-1]["objeto"].bind("<Leave>", lambda e: self.ejecutar_boton(comando[1]["command4no_selection"]))
                elif "edit" in comando[1].keys():
                    for i in range(len(self.objetos_menu)):
                        if "id" in self.objetos_menu[i].keys():
                            if self.objetos_menu[i]["id"] == comando[1]["edit"]:
                                if "image" in comando[1].keys():
                                    if "command" in comando[1].keys():
                                        print(comando[1]["image"])
                                        print(self.contenido_dat[comando[1]["image"]])
                                        imagen_file = Image.open(self.contenido_dat[comando[1]["image"]])
                                        imagen = ImageTk.PhotoImage(imagen_file)

                                        print(comando[1]["coordinates"])

                                        self.objetos_menu[i] = {"id":comando[1]["edit"],"objeto":self.objetos_menu[i]["objeto"], "cordenadas":comando[1]["coordinates"],"imagen":imagen_file}

                                        self.objetos_menu[i]["objeto"].image = imagen
                                        self.objetos_menu[i]["objeto"].bind("<Button-1>", lambda event, cmd=comando[1]["command"]: self.ejecutar_boton(cmd))

                                        self.objetos_menu[i]["objeto"].place()
                                    else:
                                        print(comando[1]["image"])
                                        print(self.contenido_dat[comando[1]["image"]])
                                        imagen_file = Image.open(self.contenido_dat[comando[1]["image"]])
                                        imagen = ImageTk.PhotoImage(imagen_file)

                                        print(comando[1]["coordinates"])

                                        self.objetos_menu[i] = {"id":comando[1]["edit"],"objeto":self.objetos_menu[i]["objeto"], "cordenadas":comando[1]["coordinates"],"imagen":imagen_file}

                                        self.objetos_menu[len(self.objetos_menu)-1]["objeto"].place()
                                        print(comando[1]["image"])
                                        print(self.contenido_dat[comando[1]["image"]])
                                        imagen_file = Image.open(self.contenido_dat[comando[1]["image"]])
                                        imagen = ImageTk.PhotoImage(imagen_file)

                                        self.objetos_menu.append({"id":comando[1]["create"],
                                        "objeto":tk.Label(self.espacio_mv, image=imagen), "cordenadas":comando[1]["coordinates"],"imagen":imagen_file})

                                        self.objetos_menu[i]["objeto"].place()
                                    if "command4selection" in comando[1].keys():
                                        self.objetos_menu[i]["objeto"].bind("<Enter>", lambda e: self.ejecutar_boton(comando[1]["command4selection"]))
                                        self.objetos_menu[i]["objeto"].place()
                                    if "command4no_selection" in comando[1].keys():
                                        self.objetos_menu[i]["objeto"].bind("<Leave>", lambda e: self.ejecutar_boton(comando[1]["command4no_selection"]))
                                        self.objetos_menu[i]["objeto"].place()
                                else:
                                    if "command" in comando[1].keys():
                                        self.objetos_menu[i] = {"id":comando[1]["edit"],"objeto":self.objetos_menu[i]["objeto"], "cordenadas":comando[1]["coordinates"]}

                                        self.objetos_menu[i]["objeto"].bind("<Button-1>", lambda event, cmd=comando[1]["command"]: self.ejecutar_boton(cmd))

                                        self.objetos_menu[i]["objeto"].config(text=comando[1]["title"])
                                    else:
                                        self.objetos_menu[i] = {"id":comando[1]["edit"],"objeto":self.objetos_menu[i]["objeto"], "cordenadas":comando[1]["coordinates"]}

                                        self.objetos_menu[i]["objeto"].config(text=comando[1]["title"])
                                    if "command4selection" in comando[1].keys():
                                        self.objetos_menu[i]["objeto"].bind("<Enter>", lambda e: self.ejecutar_boton(comando[1]["command4selection"]))

                                        self.objetos_menu[i]["objeto"].place()
                                    if "command4no_selection" in comando[1].keys():
                                        self.objetos_menu[i]["objeto"].bind("<Leave>", lambda e: self.ejecutar_boton(comando[1]["command4no_selection"]))

                                        self.objetos_menu[i]["objeto"].place()
            elif comando[0] == "sound":
                print("TIPO:", type(comando[1]))
                print("VALOR:", comando[1])
                if "create" in comando[1].keys():
                    self.objetos_menu.append({"id":comando[1]["create"],"objeto":pygame.mixer.Sound(self.contenido_dat[comando[1]["sound"]])})
                    self.objetos_menu[len(self.objetos_menu)-1]["objeto"].play()
                    self.objetos_menu[len(self.objetos_menu)-1]["objeto"].set_volume(comando[1]["volume"]/100)
                    print("sonido play")
                elif "edit" in comando[1].keys():
                    for i in range(len(self.objetos_menu)-1):
                        if "id" in self.objetos_menu[i].keys():
                            if self.objetos_menu[i]["id"] == comando[1]["edit"]:
                                self.objetos_menu[i]["objeto"].set_volume(comando[1]["volume"]/100)
            elif comando[0] == "time":
                if "wait" in comando[1].keys():
                    tiempo = comando[1]["wait"][0]
                    unidad = comando[1]["wait"][1]
                    if unidad == "seconds":
                        t = tiempo
                    elif unidad == "minutes":
                        t = tiempo*60
                    elif unidad == "hours":
                        t = iempo*3600
            elif comando[0] == "teleport":
                self.teleport(comando[1]["ubicaciones"])
            elif comando[0] == "video":
                print(comando)
                if not("restart" in comando[1].keys()):
                    file, extension = os.path.splitext(comando[1]["video"])

                    try:
                        os.makedirs(os.path.join(self.carpeta_temporal_frames,file))
                    except:
                        shutil.rmtree(os.path.join(self.carpeta_temporal_frames),file)
                        os.makedirs(os.path.join(self.carpeta_temporal_frames,file))
                    
                    subprocess.run(["ffmpeg", "-y", "-i",self.contenido_dat[comando[1]["video"]],"frame_%04d.png"], cwd=f"{self.carpeta_temporal_frames}/{file}")
                    subprocess.run(["ffmpeg", "-y", "-i",self.contenido_dat[comando[1]["video"]],"-vn","-c:a","libopus",f"{file}.opus"], cwd=f"{self.carpeta_temporal_frames}")
                
                if "create" in comando[1].keys():
                    print("create")
                    self.objetos_menu.append({"id":comando[1]["create"],"objeto":tk.Label(v), "cordenadas":comando[1]["coordinates"], "video":file, "video_path":self.contenido_dat[comando[1]["video"]], "video_r":file})
                    self.objetos_menu[len(self.objetos_menu)-1]["objeto"].place(x=0,y=0)
                    print(self.objetos_menu[len(self.objetos_menu)-1])

                    self.used_vid[file] = [False,0]

                    fps = self.get_fps(self.objetos_menu[len(self.objetos_menu)-1]["video_path"])

                    self.video_r(len(self.objetos_menu)-1, file, fps, self.contenido_dat[comando[1]["video"]])
                elif "restart" in comando[1].keys():
                    for i in range(len(self.objetos_menu)):
                        if "id" in self.objetos_menu[i].keys():
                            if self.objetos_menu[i]["id"] == comando[1]["restart"]:
                                print('self.objetos_menu[i]["id"] == comando[1]["restart"]')
                                if not(self.used_vid[self.objetos_menu[i]["video"]][0]):
                                    print('not(self.used_vid[self.objetos_menu[i]["video"]][0])', not(self.used_vid[self.objetos_menu[i]["video"]][0]))
                                    self.used_vid[self.objetos_menu[i]["video"]] = [True,0]
                                    
                                    fps = self.get_fps(self.objetos_menu[i]["video_path"])

                                    self.video_r(i, self.objetos_menu[i]["video"], fps, self.objetos_menu[i]["video_path"])
                elif "edit" in comando[1].keys():
                    for i in range(len(self.objetos_menu)-1):
                        if "id" in self.objetos_menu[i].keys():
                            if self.objetos_menu[i]["id"] == comando[1]["edit"]:
                                self.objetos_menu[i].append({"id":comando[1]["create"],"objeto":tk.Label(v), "cordenadas":comando[1]["coordinates"], "video":file, "video_path":self.contenido_dat[comando[1]["video"]]})
                                elf.objetos_menu[len(self.objetos_menu)-1]["objeto"].place(x=0,y=0)
                                print(self.objetos_menu[len(self.objetos_menu)-1])
            return t

    def _teleport(self, paths, paths_b=None):
        print("h")
        print(paths)
        if type(paths) == type([]):
            for path_num in range(0,len(paths)-1):
                self.teleport(paths[path_num])
        else:
            self.loop_comandos_on = False
            nombre, extension = os.path.splitext(paths)
            if extension == ".mkv":
                self.menu_r = False
                self.video_repr = True
                self.video(self.contenido_dat[paths], paths_b)
                #while self.video_repr:
                 #   if not(self.video_repr):
                  #      break
            elif extension == ".json":
                print("path_menu",self.contenido_dat[paths])
                menu_f = open(self.contenido_dat[paths])
                menu_t = menu_f.read()
                menu_j = json.loads(menu_t)
                menu_f.close()
                print("menu:",menu_j)
                time.sleep(16/1000)
                self.menu(menu_j)

    def teleport(self, paths, paths_b=None):
        print("h")
        print(paths)
        if type(paths) == type([]):
            if 0 == len(paths)-1:
                nombre, extension = os.path.splitext(paths[0])
                if extension == ".mkv":
                    self.menu_r = True
                    self.video_repr = True
                    self.video(self.contenido_dat[paths[0]], [])
                    #while self.video_repr:
                     #   if not(self.video_repr):
                      #      break
                elif extension == ".json":
                    print("path_menu",self.contenido_dat[paths[0]])
                    menu_f = open(self.contenido_dat[paths[0]])
                    menu_t = menu_f.read()
                    menu_j = json.loads(menu_t)
                    menu_f.close()
                    print("menu:",menu_j)
                    time.sleep(16/1000)
                    self.menu(menu_j)
                    self.reproductor.update_idletasks()
                    self.espacio_mv.update_idletasks()
            else:
                for path_num in range(0,len(paths)-1):
                    nombre, extension = os.path.splitext(paths[path_num])
                    if extension == ".mkv":
                        if len(paths)-1>=path_num+1:
                            self.menu_r = True
                            self.video_repr = True
                            self.video(self.contenido_dat[paths[path_num]], paths[path_num+1:])
                            #while self.video_repr:
                            #   if not(self.video_repr):
                            #      break
                            break
                        else:
                            self.menu_r = True
                            self.video_repr = True
                            self.video(self.contenido_dat[paths[path_num]], [])
                            #while self.video_repr:
                            #   if not(self.video_repr):
                            #      break
                            break
                    elif extension == ".json":
                        print("path_menu",self.contenido_dat[paths[path_num]])
                        menu_f = open(self.contenido_dat[paths[path_num]])
                        menu_t = menu_f.read()
                        menu_j = json.loads(menu_t)
                        menu_f.close()
                        print("menu:",menu_j)
                        time.sleep(16/1000)
                        self.menu(menu_j)
                        self.reproductor.update_idletasks()
                        self.espacio_mv.update_idletasks()
        else:
            self.loop_comandos_on = False
            nombre, extension = os.path.splitext(paths)
            if extension == ".mkv":
                self.menu_r = True
                self.video_repr = True
                self.video(self.contenido_dat[paths], paths_b)
                #while self.video_repr:
                 #   if not(self.video_repr):
                  #      break
            elif extension == ".json":
                print("path_menu",self.contenido_dat[paths])
                menu_f = open(self.contenido_dat[paths])
                menu_t = menu_f.read()
                menu_j = json.loads(menu_t)
                menu_f.close()
                print("menu:",menu_j)
                time.sleep(16/1000)
                self.menu(menu_j)
                self.reproductor.update_idletasks()
                self.espacio_mv.update_idletasks()

    def video_r(self, vid, file_name, fps, video_path):
        print("video-r1")
        print(f"{self.carpeta_temporal_frames}/{file_name}")
        frames = sorted(os.listdir(f"{self.carpeta_temporal_frames}/{file_name}"))
        print("ff", frames)
        self.used_vid[file_name][1] = 0
        if self.used_vid[file_name][0] == False:
            try:
                print("sound")
                self.used_vid[file_name].append(pygame.mixer.Sound(f"{self.carpeta_temporal_frames}/{file_name}.opus"))
                self.used_vid[file_name].append(self.used_vid[file_name][2].play())
                #self.used_vid[file_name][2].volume(50)
            except Exception as e:
                print(e)
            print("vp", video_path)
            self.used_vid[file_name] = [True,0]
            video_hilo = threading.Thread(target=lambda: self.update_frame_vid(frames,fps,file_name,video_path,vid))
            video_hilo.start()

    def update_frame_vid(self, frames, fps, file_name, video_path, vid):
        print("video-r2")
        for frame in frames:
            if self.used_vid[file_name][0] and self.get_frames_num(video_path) > self.used_vid[file_name][1]:
                try:
                    frame_file = os.path.join(self.carpeta_temporal_frames,file_name,frame)
                    imagen_file = Image.open(frame_file)
                    imagen = ImageTk.PhotoImage(imagen_file)
                    self.objetos_menu[vid]["objeto"].image = imagen
                    self.objetos_menu[vid]["imagen"] = imagen_file
                    self.used_vid[file_name][1] += 1
                    time.sleep(1/fps)
                    print(frame)
                except:
                    break
            else:
                try:
                    self.used_vid[file_name][2].stop()
                except:
                    pass
                self.used_vid[file_name][0] = False
        self.used_vid[file_name][0] = False
    
    def get_frames_num(self, filename):
        cmd = [
            "ffprobe", "-v", "error", "-count_frames",
            "-select_streams", "v:0",
            "-show_entries", "stream=nb_read_frames",
            "-of", "default=nokey=1:noprint_wrappers=1",
            filename
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return int(result.stdout.strip())

    def get_fps(self, filename):
        cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=r_frame_rate",
            "-of", "json", filename
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        data = json.loads(result.stdout)
        rate = data["streams"][0]["r_frame_rate"]
        num, den = map(int, rate.split('/'))
        fps = num / den

        print(num, den)
        print(f"FPS: {fps}")
        return fps
    
    def ejecutar_boton(self, comandos):
        if type(comandos[0]) == type([]):
            print("op")
            print(comandos)
            for comando in comandos:
                print("op2")
                print(comando)
                self.ejecutar_boton(comando)
        else:
            time.sleep(16/1000)
            self.comnado_ejecutar(comandos,self.espacio_mv)

    def menu_resize(self):
        try:
            if self.resolution_menu[0]:
                reproductor_ancho = self.reproductor.winfo_width()
                reproductor_alto = self.reproductor.winfo_height()


                escala_ancho = self.resolution_menu[1][0]
                escala_alto = self.resolution_menu[1][1]

                escala_relacion_de_aspecto = escala_ancho/escala_alto
                reproductor_relacion_de_aspecto = reproductor_ancho/reproductor_alto

                if escala_relacion_de_aspecto < reproductor_relacion_de_aspecto: #mas ancho que el menu
                    espacio_mv_ancho = reproductor_alto*escala_relacion_de_aspecto
                    espacio_mv_x     = (reproductor_ancho-espacio_mv_ancho)//2
                    espacio_mv_alto  = reproductor_alto
                    espacio_mv_y     = 0
                else: #mas alto que el menu
                    espacio_mv_alto  = reproductor_ancho/escala_relacion_de_aspecto
                    espacio_mv_y     = (reproductor_alto-espacio_mv_alto)//2
                    espacio_mv_ancho = reproductor_ancho
                    espacio_mv_x     = 0
                
                self.espacio_mv.place(x=espacio_mv_x,y=espacio_mv_y,width=espacio_mv_ancho,height=espacio_mv_alto)

                diferencia_escala_espacio_mv = [espacio_mv_ancho/escala_ancho,espacio_mv_alto/escala_alto]
                
                for objeto in self.objetos_menu:
                    if "video_r" in objeto.keys():
                        cordenadas = [0,0,escala_ancho,escala_alto]
                        
                        ancho_imagen=int(cordenadas[2]*diferencia_escala_espacio_mv[0])-int(cordenadas[0]*diferencia_escala_espacio_mv[0])
                        alto_imagen=int(cordenadas[3]*diferencia_escala_espacio_mv[1])-int(cordenadas[1]*diferencia_escala_espacio_mv[1])

                        imagen =  ImageTk.PhotoImage(objeto["imagen"].resize((ancho_imagen,alto_imagen), Image.Resampling.LANCZOS))

                        objeto["objeto"].config(image=imagen)
                        objeto["objeto"].image = imagen

                        objeto["objeto"].place(x=int(cordenadas[0]*diferencia_escala_espacio_mv[0]),
                                            y=int(cordenadas[1]*diferencia_escala_espacio_mv[1]),
                                            width=int(cordenadas[2]*diferencia_escala_espacio_mv[0])-int(cordenadas[0]*diferencia_escala_espacio_mv[0]),
                                            height=int(cordenadas[3]*diferencia_escala_espacio_mv[1])-int(cordenadas[1]*diferencia_escala_espacio_mv[1]))
                    elif "imagen" in objeto.keys():
                        cordenadas = objeto["cordenadas"]

                        ancho_imagen=int(cordenadas[2]*diferencia_escala_espacio_mv[0])-int(cordenadas[0]*diferencia_escala_espacio_mv[0])
                        alto_imagen=int(cordenadas[3]*diferencia_escala_espacio_mv[1])-int(cordenadas[1]*diferencia_escala_espacio_mv[1])

                        imagen =  ImageTk.PhotoImage(objeto["imagen"].resize((ancho_imagen,alto_imagen), Image.Resampling.LANCZOS))

                        objeto["objeto"].config(image=imagen)
                        objeto["objeto"].image = imagen

                        objeto["objeto"].place(x=int(cordenadas[0]*diferencia_escala_espacio_mv[0]),
                                            y=int(cordenadas[1]*diferencia_escala_espacio_mv[1]),
                                            width=int(cordenadas[2]*diferencia_escala_espacio_mv[0])-int(cordenadas[0]*diferencia_escala_espacio_mv[0]),
                                            height=int(cordenadas[3]*diferencia_escala_espacio_mv[1])-int(cordenadas[1]*diferencia_escala_espacio_mv[1]))
                    else:
                        cordenadas = objeto["cordenadas"]

                        objeto["objeto"].place(x=int(cordenadas[0]*diferencia_escala_espacio_mv[0]),
                                            y=int(cordenadas[1]*diferencia_escala_espacio_mv[1]),
                                            width=int(cordenadas[2]*diferencia_escala_espacio_mv[0])-int(cordenadas[0]*diferencia_escala_espacio_mv[0]),
                                            height=int(cordenadas[3]*diferencia_escala_espacio_mv[1])-int(cordenadas[1]*diferencia_escala_espacio_mv[1]))

            self.reproductor.update_idletasks()
            self.espacio_mv.update_idletasks()
        except:
            pass
        if self.menu_r:
            self.ventana_tk.after(10, self.menu_resize)

    def repdorucir(self):
        paths = MaVM.extrac_type_all(file=self.file, output_folder=self.carpeta_temporal, content_type=None)
        #videos = MaVM.extrac_type_all(file=self.file, output_folder=self.carpeta_temporal, content_type="video/x-matroska")

        self.contenido_dat = {}
        for path in paths:
            directorio, archivo = os.path.split(path)
            self.contenido_dat[archivo] = path
            print(archivo)
        self.start()

    def video(self,video_path,paths):
        self.loop_comandos_on = False
        self.objetos_menu = []
        self.used_vid = {}
        for widget in self.reproductor.winfo_children():
            try:
                if widget is self.espacio_mv:
                    y = False
                else: 
                    widget.destroy()  #elimina cada widget
            except:
                widget.destroy()  #elimina cada widget
        
        for widget in self.espacio_mv.winfo_children():
            try:
                if widget is self.espacio_mv:
                    y = False
                else: 
                    widget.destroy()  #elimina cada widget
            except:
                widget.destroy()  #elimina cada widget
        
        archivo = os.path.basename(video_path)

        file_name, extension = os.path.splitext(archivo)
        
        try:
            shutil.rmtree(os.path.join(self.carpeta_temporal_frames,file_name))
            os.makedirs(os.path.join(self.carpeta_temporal_frames,file_name))
        except:
            os.makedirs(os.path.join(self.carpeta_temporal_frames,file_name))
        
        contenido_video = subprocess.run(["ffprobe", "-v", "quiet", "-print_format", "json", "-show_streams", video_path],capture_output=True,text=True)
        
        contenidos_video_json = json.loads(contenido_video.stdout)["streams"]

        video_audios = []
        video_videos = []

        self.pista_audio_name.set("none")

        for contenido in contenidos_video_json:
            if "codec_type" in contenido.keys():
                if contenido["codec_type"] == "audio":
                    video_audios.append(str(len(video_audios)))
                    self.pista_audio_name.set("0")
                elif contenido["codec_type"] == "video":
                    video_videos.append(str(len(video_videos)))

        menu_audio = self.pista_audio_menu["menu"]

        menu_audio.delete(0, "end")

        opciones_audio = video_audios
        for opcion in opciones_audio:
            def _set_val(v=opcion):
                print("audio seleccionado", v)
                self.pista_audio_name.set(v)
            menu_audio.add_command(
                label=opcion,
                command=_set_val
            )

        try:
            shutil.rmtree(os.path.join(self.carpeta_temporal_frames,f"{self.carpeta_temporal_frames}/{file_name}"))
            os.makedirs(os.path.join(self.carpeta_temporal_frames,f"{self.carpeta_temporal_frames}/{file_name}"))
        except:
            os.makedirs(os.path.join(self.carpeta_temporal_frames,f"{self.carpeta_temporal_frames}/{file_name}"))
            
        for audio_num, audio in enumerate(video_audios):
            subprocess.run(["ffmpeg", "-i",video_path, "-map",f"0:a:{audio_num}", "-c:a","libopus", f"{audio_num}.opus"], cwd=f"{self.carpeta_temporal_frames}/{file_name}")
        
        menu_video = self.pista_video_menu["menu"]

        menu_video.delete(0, "end")
        self.pista_video_name.set("0")

        opciones_video = video_videos
        for opcion in opciones_video:
            def _set_val_v(v=opcion):
                print("video seleccionado", v)
                self.pista_video_name.set(v)
            menu_video.add_command(
                label=opcion,
                command=_set_val_v
            )

        for video_num, video in enumerate(video_videos):
            try:
                shutil.rmtree(os.path.join(self.carpeta_temporal_frames,file_name,str(video_num)))
                os.makedirs(os.path.join(self.carpeta_temporal_frames,file_name,str(video_num)))
            except:
                os.makedirs(os.path.join(self.carpeta_temporal_frames,file_name,str(video_num)))
            
            subprocess.run(["ffmpeg", "-i",video_path, "-map",f"0:v:{video_num}", "fotograma_%04d.png"], cwd=f"{os.path.join(self.carpeta_temporal_frames,file_name,str(video_num))}")
        
        #subprocess.run(['mpv', video_path])

        fps = self.get_fps(video_path)

        try:
            audio = [True, pygame.mixer.music.load(os.path.join(self.carpeta_temporal_frames,f"{file_name}.opus"))]
            pygame.mixer.music.play()
        except:
            audio = [False]
        print(audio)
        #audi0.set_volume(50/100)

        self.used_vid[file_name] = [False,0]
        #try:
        #    self.used_vid[file_name][2] = pygame.mixer.music(f"{self.carpeta_temporal_frames}/{video_path}.opus")
        #    self.used_vid[file_name].append(self.used_vid[file_name][2].play())
        #except:
        #    pass
        print("vp", video_path)
        
        frame_num = -1
        #print(frames)
        #frames_num = len(frames)-1

        self.objetos_menu.append({"objeto":tk.Label(self.espacio_mv), "video_r":archivo, "video_path":video_path, "imagen": None})
        vid = len(self.objetos_menu)-1
        self.objetos_menu[vid]["objeto"].place()

        if audio[0]:
            pygame.mixer.music.play()
        
        self.pista_audio = "none"

        self.video_repr = True
        self.video_b(file_name=file_name,vid=vid,frame_num=frame_num,play=True,paths=paths,audio=audio)
    
    def get_seconds(self, video_path):
        """Obtiene la duración del video usando ffprobe."""
        comando = [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", video_path
        ]
        try:
            resultado = subprocess.run(comando, capture_output=True, text=True, check=True)
            duracion = float(resultado.stdout.strip())
            return duracion
        except subprocess.CalledProcessError as e:
            return None

    def video_b(self,file_name,vid,frame_num,play,paths,audio):
        frames = sorted(os.listdir(f"{self.carpeta_temporal_frames}/{file_name}/{self.pista_video_name.get()}"))
        frames_num = len(frames)-1

        #while not(frame_num == frames_num):
        #if not(frame_num == frames_num):
        if frame_num >= frames_num:
            if self.pista_audio_name.get() != "none":
                pygame.mixer.music.pause()
            for widget in self.reproductor.winfo_children():
                try:
                    if widget is self.espacio_mv:
                        y = False
                    else: 
                        widget.destroy()  #elimina cada widget
                except:
                    widget.destroy()  #elimina cada widget
            
            for widget in self.espacio_mv.winfo_children():
                try:
                    if widget is self.espacio_mv:
                        y = False
                    else: 
                        widget.destroy()  #elimina cada widget
                except:
                    widget.destroy()  #elimina cada widget
            
            self.menu_r = True
            self.video_repr = False

            self.teleport(paths)

            #self.menu_resize()
            #self.actalizar_medidas()
            return
        elif self.video_repr:
            print(f"{file_name}.mkv")
            fps = len(frames)/self.get_seconds(self.contenido_dat[f"{file_name}.mkv"])

            segundos_por_fotograma = 1/fps
            fotogramas_cambio = int(10*fps)

            segundos_cambio = fotogramas_cambio/fps

            if play:
                print(play)
                try:
                    accion = self.detectar_botones
                    
                    frame = frames[frame_num]

                    print(frame)
                    if accion == "stop-play":
                        play = False
                        self.reset_botones_fun()
                        if self.pista_audio_name.get() != "none":
                            #if self.pista_audio_name.get() != self.pista_audio:
                            #   pygame.mixer.music.load(os.path.join(self.carpeta_temporal_frames,file_name,f"{self.pista_video_name.get()}.opus"))
                            #pygame.mixer.music.pause()
                            pygame.mixer.music.pause()
                    elif accion == "adelante":
                        if (frame_num+fotogramas_cambio)>frames_num or (frame_num+fotogramas_cambio)==frames_num:
                            frame_num = frames_num
                        else:
                            frame_num += fotogramas_cambio
                        self.reset_botones_fun()
                        if self.pista_audio_name.get() != "none":
                            #if self.pista_audio_name.get() != self.pista_audio:
                            #   pygame.mixer.music.load(os.path.join(self.carpeta_temporal_frames,file_name,f"{self.pista_video_name.get()}.opus"))
                            #pygame.mixer.music.pause()
                            pygame.mixer.music.load(os.path.join(self.carpeta_temporal_frames,file_name,f"{self.pista_audio_name.get()}.opus"))
                            print(os.path.join(self.carpeta_temporal_frames,file_name,f"{self.pista_audio_name.get()}.opus"))
                            self.pista_audio = self.pista_audio_name.get()
                        pygame.mixer.music.play(start=frame_num/fps)
                    elif accion == "atras":
                        if (frame_num-fotogramas_cambio)<0 or (frame_num-fotogramas_cambio)==0:
                            frame_num = 0
                        else:
                            frame_num -= fotogramas_cambio
                        self.reset_botones_fun()
                        if self.pista_audio_name.get() != "none":
                            #if self.pista_audio_name.get() != self.pista_audio:
                            #   pygame.mixer.music.load(os.path.join(self.carpeta_temporal_frames,file_name,f"{self.pista_video_name.get()}.opus"))
                            #pygame.mixer.music.pause()
                            pygame.mixer.music.load(os.path.join(self.carpeta_temporal_frames,file_name,f"{self.pista_audio_name.get()}.opus"))
                            print(os.path.join(self.carpeta_temporal_frames,file_name,f"{self.pista_audio_name.get()}.opus"))
                            self.pista_audio = self.pista_audio_name.get()
                        pygame.mixer.music.play(start=frame_num/fps)
                    else:
                        frame_num +=1

                    if self.pista_audio_name.get() != "none":
                        if self.pista_audio_name.get() != self.pista_audio:
                            pygame.mixer.music.load(os.path.join(self.carpeta_temporal_frames,file_name,f"{self.pista_video_name.get()}.opus"))
                            #pygame.mixer.music.pause()
                            pygame.mixer.music.load(os.path.join(self.carpeta_temporal_frames,file_name,f"{self.pista_audio_name.get()}.opus"))
                            print(os.path.join(self.carpeta_temporal_frames,file_name,f"{self.pista_audio_name.get()}.opus"))
                            pygame.mixer.music.play(start=frame_num/fps)
                        self.pista_audio = self.pista_audio_name.get()
                    print(f"frame_num:{frame_num}\nframes_num:{frames_num}")
                    #os.path.join(
                    frame_file_path = os.path.join(self.carpeta_temporal_frames,file_name,self.pista_video_name.get(),frame)
                    imagen_file = Image.open(frame_file_path)
                    imagen = ImageTk.PhotoImage(imagen_file)
                    #self.objetos_menu[vid]["objeto"].image = imagen
                    self.objetos_menu[vid]["imagen"] = imagen_file
                    self.used_vid[file_name][1] += 1
                except Exception as e:
                    print(e)
            else:
                accion = self.detectar_botones
                if accion == "stop-play":
                    play = True
                    self.reset_botones_fun()
                    if self.pista_audio_name.get() != "none":
                        pygame.mixer.music.play(start=frame_num/fps)
                
            self.reproductor.update_idletasks()
                
            self.espacio_mv.update_idletasks()

            self.ventana_tk.after(int(segundos_por_fotograma*1000), lambda: self.video_b(file_name,vid,frame_num,play,paths,audio))

def args():
    parser = argparse.ArgumentParser(description="reproductor MaVM")
    parser.add_argument("file", nargs='?', help="ruta del video .mavm")
    
    args_var = parser.parse_args()
    
    if args_var.file:
        if not('.mavm' in args_var.file.lower()):
            print("el archivo debe ser .mavm")
            exit()
        elif not(os.path.exists(args_var.file)):
            print("el archivo no existe")
            exit()
        else:
            file = os.path.abspath(args_var.file)
            ventana_tk = tk.Tk()
            ventana(ventana_tk=ventana_tk, file=file)
            ventana_tk.mainloop()
    else:
        ventana_tk = tk.Tk()
        ventana(ventana_tk, None)
        ventana_tk.mainloop()

args()

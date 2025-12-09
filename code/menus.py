class version_formato:
    def __new__(cls, version):
        version_soported = ('v.2.1.0',)
        interfaz_version = {'v.2.1.0': cls.interfaz_2_1_0}
        if version in version_soported:
            return [True, interfaz_version[version]]
        else:
            return [False, None]
    
    class interfaz_2_1_0:
        def __init__(self, menu):
            lista_comandos = {
                "resolucion":[],
                "start": [],
                "loop": []
                }
            m = []
            menu_name = ''
            start_comandos = menu["start"]
            for comandos in start_comandos:
                    comando    = list(comandos.keys())[0]
                    parametros = list(comandos.values())[0]
                    if comando == "menu":
                        menu_name = parametros[1]
                    elif comando == menu_name:
                        if list(parametros[0].keys())[0] == "resolution":
                            lista_comandos["resolucion"] = list(parametros[0].values())[0]
                        else:
                            lista_comandos["start"] = self.comando_x(parametros, lista_comandos["start"])
                    elif comando == "time":
                        lista_comandos["start"].append(["time", {
                            "wait": [parametros[0],parametros[1]]
                            }])
            
            loop_comandos = menu["loop"]
            for comandos in loop_comandos:
                    comando   = list(comandos.keys())[0]
                    parametros = list(comandos.values())[0]
                    if comando == menu_name:
                        lista_comandos["loop"] = self.comando_x(parametros, lista_comandos["loop"])
                    elif comando == "time":
                        lista_comandos["loop"].append(["time", {
                            "wait": [parametros[0],parametros[1]]
                            }])
            self.lista_comandos = lista_comandos

        def comando_x(self, comandos, lista_comandos):
                print(comandos)
                try:
                    comando   = list(comandos[0].keys())[0]
                    parametros = list(comandos[0].values())[0]
                except:
                    comando   = list(comandos.keys())[0]
                    parametros = list(comandos.values())[0]
                if comando == "image":
                    if parametros[0] == "create":
                        lista_comandos.append(["image", {
                            parametros[0]: parametros[1],
                            "coordinates": [
                                parametros[3], parametros[4],
                                parametros[5], parametros[6]
                                ],
                            "imagen": parametros[7]
                        }])
                    elif parametros[0] == "edit":
                        lista_comandos.append(["image", {
                            parametros[0]: parametros[1],
                            "coordinates": [
                                parametros[3], parametros[4],
                                parametros[5], parametros[6]
                                ],
                            "imagen": parametros[7]
                        }])
                elif comando == "text": 
                    lista_comandos.append(["text", {
                        "coordinates": [
                            parametros[1], parametros[2],
                            parametros[3], parametros[4]
                            ],
                        "text": parametros[6]
                    }])
                elif comando == "button":
                    if "command_click" in parametros:
                        if type(parametros[12]) == type([]):
                            coman = []
                            for com in parametros[12]:
                                coman.append(self.comando_x(com,[]))
                        else:
                            coman = self.comando_x([parametros[12]],[])
                        if "command4selection" in parametros:
                            if "command4no_selection" in parametros:
                                if type(parametros[14]) == type([]):
                                    coman2 = []
                                    for com in parametros[14]:
                                        coman2.append(self.comando_x(com,[]))
                                else:
                                    coman2 = self.comando_x([parametros[14]],[])

                                if type(parametros[16]) == type([]):
                                    coman3 = []
                                    for com in parametros[16]:
                                        coman3.append(self.comando_x(com,[]))
                                else:
                                    coman3 = self.comando_x([parametros[16]],[])
                                
                                lista_comandos.append(["button", {
                                    parametros[0]: parametros[1],
                                    "coordinates": [
                                        parametros[3], parametros[4],
                                        parametros[5], parametros[6]
                                        ],
                                    "title": parametros[8],
                                    "color": parametros[10],
                                    "command": coman,
                                    "command4selection": coman2,
                                    "command4no_selection": coman3
                                }])
                            else:
                                if type(parametros[14]) == type([]):
                                    coman2 = []
                                    for com in parametros[14]:
                                        coman2.append(self.comando_x(com,[]))
                                else:
                                    coman2 = self.comando_x([parametros[14]],[])
                                lista_comandos.append(["button", {
                                    parametros[0]: parametros[1],
                                    "coordinates": [
                                        parametros[3], parametros[4],
                                        parametros[5], parametros[6]
                                        ],
                                    "title": parametros[8],
                                    "color": parametros[10],
                                    "command": coman,
                                    "command4selection": coman2
                                }])
                        else:
                            lista_comandos.append(["button", {
                                    parametros[0]: parametros[1],
                                    "coordinates": [
                                        parametros[3], parametros[4],
                                        parametros[5], parametros[6]
                                        ],
                                    "title": parametros[8],
                                    "color": parametros[10],
                                    "command": coman
                                }])
                    else:
                        lista_comandos.append(["button", {
                            parametros[0]: parametros[1],
                            "coordinates": [
                                parametros[3], parametros[4],
                                parametros[5], parametros[6]
                                ],
                            "title": parametros[8],
                            "color": parametros[10]
                        }])
                elif comando == "teleport":
                    lista_comandos.append(["teleport", {
                        "ubicaciones": parametros
                    }]),
                elif comando == "video":
                    if parametros[0] == "create":
                        lista_comandos.append(["video", {
                            "create": parametros[1],
                            "coordinates": [parametros[3],parametros[4],
                                            parametros[5],parametros[6]],
                            "video": parametros[7]
                        }])
                    elif parametros[0] == "edit":
                        if parametros[2] == "restart":
                            lista_comandos.append(["video", {
                                "restart":parametros[1]
                            }])
                        else:
                            lista_comandos.append(["video", {
                                "edit": parametros[1],
                                "coordinates": [parametros[3],parametros[4],
                                                parametros[5],parametros[6]],
                                "video": parametros[7]
                            }])
                elif comando == "button_default":
                    lista_comandos.append(["button_default", {
                        "button": parametros[0]
                    }])
                elif comando == "sound":
                    if parametros[0] == "create":
                        lista_comandos.append(["sound", {
                            "create": parametros[1],
                            "sound": parametros[2],
                            "volume": parametros[4]
                        }])
                    elif parametros[0] == "edit":
                        lista_comandos.append(["sound", {
                            "edit": parametros[1],
                            "volume": parametros[3]
                        }])
                return lista_comandos
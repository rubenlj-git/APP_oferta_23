
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import plotly.express as px
import base64
from streamlit_option_menu import option_menu
import io
import geopandas as gpd
from mpl_toolkits.axes_grid1 import make_axes_locatable
import plotly.graph_objects as go
import matplotlib.colors as colors
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import locale




# user="/home/ruben/" 
# user = "C:/Users/joana.APCE/"
# path = user + "Dropbox/Estudi d'oferta/2022/repos/APP-Estudi_oferta/"

path = ""


############################################################  TITULO DE PESTAÑA DE PÁGINA WEB ################################################
st.set_page_config(
    page_title="Estudi d'oferta de nova construcció",
    page_icon="""data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAA1VBMVEVHcEylpKR6eHaBgH9GREGenJxRT06op6evra2Qj49kYWCbmpqdnJyWlJS+vb1CPzyurKyHhYWMiYl7eXgOCgiPjY10cnJZV1WEgoKCgYB9fXt
    /fHyzsrGUk5OTkZGlo6ONioqko6OLioq7urqysbGdnJuurazCwcHLysp+fHx9fHuDgYGJh4Y4NTJcWVl9e3uqqalcWlgpJyacm5q7urrJyMizsrLS0tKIhoaMioqZmJiTkpKgn5+Bf36WlZWdnJuFg4O4t7e2tbXFxMR3dXTg39/T0dLqKxxpAAAAOHRSTlMA/WCvR6hq/
    v7+OD3U9/1Fpw+SlxynxXWZ8yLp+IDo2ufp9s3oUPII+jyiwdZ1vczEli7waWKEmIInp28AAADMSURBVBiVNczXcsIwEAVQyQZLMrYhQOjV1DRKAomKJRkZ+P9PYpCcfbgze+buAgDA5nf1zL8TcLNamssiPG/
    vt2XbwmA8Rykqton/XVZAbYKTSxzVyvVlPMc4no2KYhFaePvU8fDHmGT93i47Xh8ijPrB/0lTcA3lcGQO7otPmZJfgwhhoytPeKX5LqxOPA9i7oDlwYwJ3p0iYaEqWDdlRB2nkDjgJPA7nX0QaVq3kPGPZq/V6qUqt9BAmVaCUcqEdACzTBFCpcyvFfAAxgMYYVy1sTwAAAAASUVORK5CYII=""",
    layout="wide"
)

############################################################  FUNCIONES: CSS, DESCARGAR EXCELS, SUBIR IMAGEN APCE ################################################
def load_css_file(css_file_path):
    with open(css_file_path) as f:
        return st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
load_css_file(path + "main.css")

def filedownload(df, filename):
    towrite = io.BytesIO()
    df.to_excel(towrite, encoding='latin-1', index=True, header=True)
    towrite.seek(0)
    b64 = base64.b64encode(towrite.read()).decode("latin-1")
    href = f"""<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}">
    <button class="download-button">Descarregar</button></a>"""
    return href


left_col, right_col, margin_right = st.columns((0.7, 1, 0.25))
with right_col:
    with open(path + "APCE_mod.png", "rb") as f:
        data_uri = base64.b64encode(f.read()).decode("utf-8")
    markdown = f"""
    <div class="image">
    <img src="data:image/png;base64, {data_uri}" alt="image" />
    </div>
    """
    st.markdown(markdown, unsafe_allow_html=True)


############################################################  CONFIGURAR MENU DE OPCIONES ################################################
# Creating a dropdown menu with options and icons, and customizing the appearance of the menu using CSS styles.
selected = option_menu(
    menu_title=None,  # required
    options=["Catalunya","Províncies i àmbits","Municipis", "Districtes de Barcelona","Contacte"],  # Dropdown menu
    icons=[None,"map","house-fill","house-fill", "envelope"],  # Icons for dropdown menu
    menu_icon="cast",  # optional
    default_index=0,  # optional
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#cce8e2"},
        "icon": {"color": "#005c48", "font-size": "17px"},
        "nav-link": {
            "font-size": "17px",
            "text-align": "center",
            "font-weight": "bold",
            "color":"#005442",
            "margin": "20px",
            "--hover-color": "#DAE4E0",
            "background-color": "#cce8e2"
            },
        "nav-link-selected": {"background-color": "#66b9a7"},
        })

############################################################  IMPORTAMOS BBDD 2022 ################################################
@st.cache_data(show_spinner="**Carregant les dades... Esperi, siusplau**", max_entries=500)
def tidy_bbdd(any):
    # Importar BBDD promocions d'habitatge
    bbdd_estudi_prom = pd.read_excel(path + 'BBDD 2022_2021 03.02.23.xlsx', sheet_name='Promocions 2022_2021')
    bbdd_estudi_prom.columns = bbdd_estudi_prom.iloc[0,:]
    bbdd_estudi_prom = bbdd_estudi_prom[bbdd_estudi_prom["ESTUDI"]==any]
    bbdd_estudi_prom['TIPO_aux'] = np.where(bbdd_estudi_prom['TIPO'].isin([1,2]), 'Habitatges unifamiliars', 'Habitatges plurifamiliars')

    mapping = {1: 'Unifamiliars aïllats', 
            2: 'Unifamiliars adossats', 
            3: 'Plurifamiliars en bloc obert', 
            4: 'Plurifamiliars en bloc tancat'}

    mapping1 = {1: "De nova Construcció",
                2: "Rehabilitació integral"}

    mapping2 = {1: "Pendent d'enderroc", 
            2: "Solar", 
            3: "Buidat", 
            4: "Cimentació",
            5: "Estructura",
            6: "Tancaments exteriors",
            7: "Tancaments interiors",
            8: "Claus en mà",
            9: "NS/NC"}

    mapping3 = {
                    1: 'A',
                    1.2:"A",
                    2: 'B',
                    2.3: "B",
                    3: 'C',
                    4: 'D',
                    4.5: "D",
                    5: 'E',
                    5.3 : "C",
                    6: "F",
                    7: "G",
                    8: "En tràmits",
                    9: "Sense informació"
    }

    mapping4 = {
                    0: "Altres",
                    1: "Plaça d'aparcament opcional",
                    2: "Plaça d'aparcament inclosa",
                    3: "Sense plaça d'aparcament",
    }


    # bbdd_estudi_hab['QENERGC'] = bbdd_estudi_hab['QENERGC'].map(number_to_letter_map)

    bbdd_estudi_prom['TIPO'] = bbdd_estudi_prom['TIPO'].map(mapping)

    bbdd_estudi_prom['TIPH'] = bbdd_estudi_prom['TIPH'].map(mapping1)


    bbdd_estudi_prom['ESTO'] = bbdd_estudi_prom['ESTO'].map(mapping2)

    bbdd_estudi_prom['QENERGC'] = bbdd_estudi_prom['QENERGC'].map(mapping3)

    bbdd_estudi_prom['APAR'] = bbdd_estudi_prom['APAR'].map(mapping4)


    # Importar BBDD habitatges
    bbdd_estudi_hab = pd.read_excel(path + 'BBDD 2022_2021 03.02.23.xlsx', sheet_name='Habitatges 2022_2021')
    bbdd_estudi_hab.columns = bbdd_estudi_hab.iloc[0,:]
    bbdd_estudi_hab = bbdd_estudi_hab[bbdd_estudi_hab["ESTUDI"]==any]





    # ["Total dormitoris","Banys i lavabos","Cuines estàndard","Cuines americanes","Terrasses, balcons i patis","Estudi/golfes","Safareig","Altres interiors","Altres exteriors"]

    # ["DORM", "LAV", "cuina_normal", "cuina_amer", "TER", "Golfes", "Safareig","Altres interiors","Altres exteriors" ]

    bbdd_estudi_hab['TIPOG'] = np.where(bbdd_estudi_hab['TIPO'].isin([1,2]), 'Habitatges unifamiliars', 'Habitatges plurifamiliars')
    bbdd_estudi_hab['TIPO'] = bbdd_estudi_hab['TIPO'].map(mapping)
    bbdd_estudi_hab['QENERGC'] = bbdd_estudi_hab['QENERGC'].map(mapping3)
    bbdd_estudi_hab['APAR'] = bbdd_estudi_hab['APAR'].map(mapping4)

    bbdd_estudi_hab = bbdd_estudi_hab.dropna(axis=1 , how ='all')



    bbdd_estudi_hab = bbdd_estudi_hab.rename(columns = {'V0006':'Total dormitoris_aux', 
                                                            "DORM": "Total dormitoris",
                                                            "LAV": "Banys i lavabos",
                                                            "TER": "Terrasses, balcons i patis",
                                                            'NOMD01C':'Superfície útil',
                                                            "Preu_m2_util": "Preu m2 útil",
                                                            "NOMD01F_2022": "Preu mitjà",
                                                            'NOMD01P':'Estudi/golfes', 
                                                            'NOMD01Q':'Safareig', 
                                                            'NOMD01K': 'Cuines estàndard', 
                                                            'NOMD01L': 'Cuines americanes', 
                                                            "NOMD01R": "Altres interiors", 
                                                            "NOMD01S":"Altres exteriors"})

    bbdd_estudi_prom = bbdd_estudi_prom.rename(columns = {'V0006':'Total dormitoris_aux', 
                                                            "DORM": "Total dormitoris",
                                                            "LAV": "Banys i lavabos",
                                                            "TER": "Terrasses, balcons i patis",
                                                            'NOMD01C':'Superfície útil',
                                                            "Preu_m2_util": "Preu m2 útil",
                                                            'NOMD01P':'Estudi/golfes', 
                                                            'NOMD01Q':'Safareig', 
                                                            'NOMD01K': 'Cuines estàndard', 
                                                            'NOMD01L': 'Cuines americanes', 
                                                            "NOMD01R": "Altres interiors", 
                                                            "NOMD01S":"Altres exteriors"})


    # Canviar de nom tots els equipaments
    bbdd_estudi_hab = bbdd_estudi_hab.rename(columns = {'EQUIC_1': 'Zona enjardinada', 
                                                        'EQUIC_2': 'Parc infantil',
                                                        'EQUIC_3': 'Piscina comunitària', 
                                                        'EQUIC_4': 'Traster', 
                                                        'EQUIC_5': 'Ascensor', 
                                                        'EQUIC_6': 'Equipament Esportiu',  
                                                        'EQUIC_7': 'Sala de jocs', 
                                                        'EQUIC_8': 'Sauna', 
                                                        "EQUIC_9_50": "Altres",
                                                        'EQUIC_99': 'Cap dels anteriors'})
    bbdd_estudi_prom = bbdd_estudi_prom.rename(columns = {'EQUIC_1': 'Zona enjardinada', 
                                                        'EQUIC_2': 'Parc infantil',
                                                        'EQUIC_3': 'Piscina comunitària', 
                                                        'EQUIC_4': 'Traster', 
                                                        'EQUIC_5': 'Ascensor', 
                                                        'EQUIC_6': 'Equipament Esportiu',  
                                                        'EQUIC_7': 'Sala de jocs', 
                                                        'EQUIC_8': 'Sauna', 
                                                        "QUAL_ALTRES": "Altres",
                                                        'EQUIC_99': 'Cap dels anteriors'})
    bbdd_estudi_prom["Ascensor"] = np.where(bbdd_estudi_prom["Ascensor"]>=1, 1, bbdd_estudi_prom["Ascensor"])
    bbdd_estudi_hab["Ascensor"] = np.where(bbdd_estudi_hab["Ascensor"]>=1, 1, bbdd_estudi_hab["Ascensor"])


    # Canviar de nom totes les qualitats
    bbdd_estudi_hab = bbdd_estudi_hab.rename(columns = {"QUALIC_5": "Aire condicionat", 
                                                        "QUALIC_6": "Bomba de calor", 
                                                        "QUALI_A": "Aerotèrmia", 
                                                        'QUALIC_7':"Calefacció", 
                                                        'QUALIC_8':"Preinstal·lació d'A.C./B. Calor/Calefacció", 
                                                        'QUALIC_9': 'Parquet', 
                                                        'QUALIC_10':'Armaris encastats',
                                                        'QUALIC_12':'Placa de cocció amb gas',
                                                        'QUALIC_13':'Placa de cocció vitroceràmica',
                                                        "QUALIC_14":"Placa d'inducció",
                                                        'QUALIC_22':'Plaques solars'})


    bbdd_estudi_prom = bbdd_estudi_prom.rename(columns = {"QUALIC_5": "Aire condicionat", 
                                                        "QUALIC_6": "Bomba de calor", 
                                                        "QUALI_A": "Aerotèrmia", 
                                                        'QUALIC_7':"Calefacció", 
                                                        'QUALIC_8':"Preinstal·lació d'A.C./B. Calor/Calefacció", 
                                                        'QUALIC_9': 'Parquet', 
                                                        'QUALIC_10':'Armaris encastats',
                                                        'QUALIC_12':'Placa de cocció amb gas',
                                                        'QUALIC_13':'Placa de cocció vitroceràmica',
                                                        "QUALIC_14":"Placa d'inducció",
                                                        'QUALIC_22':'Plaques solars'})
    #  Canviar nom a tipus de calefacció
    bbdd_estudi_prom = bbdd_estudi_prom.rename(columns = {'CALEFC_3': 'De gasoil', 
                                                        'CALEFC_4': 'De gas natural', 
                                                        'CALEFC_5': 'De propà', 
                                                        'CALEFC_6': "D'electricitat", 
                                                        'CALEFC_9': "No s'indica tipus"})




    bbdd_estudi_prom['TIPV'] = np.where(bbdd_estudi_prom['TIPV_1'] >= 1, "Venda a través d'immobiliària independent",
                                        np.where(bbdd_estudi_prom['TIPV_2'] >= 1, "Venda a través d'immobiliaria del mateix promotor",
                                                np.where(bbdd_estudi_prom['TIPV_3'] >= 1, "Venda directa del promotor", "Sense informació")))


    bbdd_estudi_prom['TIPOL_VENDA'] = np.where(bbdd_estudi_prom['TIPOL_VENDA_1'] == 1, "0D",
                                        np.where(bbdd_estudi_prom['TIPOL_VENDA_2'] == 1, "1D",
                                                np.where(bbdd_estudi_prom['TIPOL_VENDA_3'] == 1, "2D",
                                                        np.where(bbdd_estudi_prom['TIPOL_VENDA_4'] == 1, "3D",
                                                            np.where(bbdd_estudi_prom['TIPOL_VENDA_5'] == 1, "4D", 
                                                                np.where(bbdd_estudi_prom['TIPOL_VENDA_6'] == 1, "5+D", "NA"))))))

                        
                                                    
    #  "Venda a través d'immobiliària independent", "Venda a través d'immobiliaria del mateix promotor", "Venda directa del promotor"

    bbdd_estudi_hab['TIPH'] = bbdd_estudi_hab['TIPH'].map(mapping1)

    bbdd_estudi_hab['ESTO'] = bbdd_estudi_hab['ESTO'].map(mapping2)


    vars = ['Zona enjardinada', 'Parc infantil', 'Piscina comunitària', 
            'Traster', 'Ascensor', 'Equipament Esportiu', 'Sala de jocs', 
            'Sauna', 'Altres', "Aire condicionat", "Bomba de calor", 
            "Aerotèrmia", "Calefacció", "Preinstal·lació d'A.C./B. Calor/Calefacció", 
            "Parquet", "Armaris encastats", 'Placa de cocció amb gas', 
            'Placa de cocció vitroceràmica', "Placa d'inducció", 'Plaques solars', "APAR"]
    vars_aux = ['Zona enjardinada', 'Parc infantil', 'Piscina comunitària', 
            'Traster', 'Ascensor', 'Equipament Esportiu', 'Sala de jocs', 
            'Sauna', 'Altres', "Aire condicionat", "Bomba de calor", 
            "Aerotèrmia", "Calefacció", "Preinstal·lació d'A.C./B. Calor/Calefacció", 
            "Parquet", "Armaris encastats", 'Placa de cocció amb gas', 
            'Placa de cocció vitroceràmica', "Placa d'inducció", 'Plaques solars', "Safareig","Terrasses, balcons i patis"]
    for i in vars:
        bbdd_estudi_prom[i] = bbdd_estudi_prom[i].replace(np.nan, 0)
    for i in vars_aux:
        bbdd_estudi_hab[i] = bbdd_estudi_hab[i].replace(np.nan, 0)
    bbdd_estudi_hab["Calefacció"] = bbdd_estudi_hab["Calefacció"].replace(' ', 0) 
    bbdd_estudi_prom["Calefacció"] = bbdd_estudi_prom["Calefacció"].replace(' ', 0) 


    bbdd_estudi_hab["Tram_Sup_util"] = bbdd_estudi_hab["Tram_Sup_util"].str.replace(" ", "")
    bbdd_estudi_hab["Tram_Sup_util"] = bbdd_estudi_hab["Tram_Sup_util"].str[3:]



    # Afegir categories a algunes columnes de la base de dades d'habitatge

    room_dict =  {i: f"{i}D" if i <= 4 else "5+D" for i in range(0, 20)}
    toilet_dict = {i: f"{i} Bany" if i <= 1 else "2 i més Banys" for i in range(1, 20)}
    bbdd_estudi_hab_mod = bbdd_estudi_hab.copy()

    bbdd_estudi_hab_mod['Total dormitoris'] = bbdd_estudi_hab_mod['Total dormitoris'].map(room_dict)
    bbdd_estudi_hab_mod['Banys i lavabos'] = bbdd_estudi_hab_mod['Banys i lavabos'].map(toilet_dict)
    bbdd_estudi_hab_mod["Terrasses, balcons i patis"] = np.where(bbdd_estudi_hab_mod["Terrasses, balcons i patis"]>=1, 1, 0)

    bbdd_estudi_hab["Nom DIST"] = bbdd_estudi_hab["Nom DIST"].str.replace(r'^\d{2}\s', '', regex=True)
    bbdd_estudi_hab_mod["Nom DIST"] = bbdd_estudi_hab_mod["Nom DIST"].str.replace(r'^\d{2}\s', '', regex=True)

    return([bbdd_estudi_prom, bbdd_estudi_hab, bbdd_estudi_hab_mod])


bbdd_estudi_prom, bbdd_estudi_hab, bbdd_estudi_hab_mod = tidy_bbdd(2022)


############################################################  IMPORTAMOS BBDD FINAL 2023 ################################################
@st.cache_data(show_spinner="**Carregant les dades... Esperi, siusplau**", max_entries=500)
def tidy_bbdd_semestral(any):
    bbdd_estudi_prom = pd.read_excel(path + 'P3007 BBDD desembre APCE.xlsx', sheet_name='Promocions 2023')
    bbdd_estudi_prom.columns = bbdd_estudi_prom.iloc[0,:]
    bbdd_estudi_prom = bbdd_estudi_prom[bbdd_estudi_prom["ESTUDI"]==any]
    bbdd_estudi_prom['TIPO_aux'] = np.where(bbdd_estudi_prom['TIPO'].isin([1,2]), 'Habitatges unifamiliars', 'Habitatges plurifamiliars')

    mapping = {1: 'Unifamiliars aïllats', 
            2: 'Unifamiliars adossats', 
            3: 'Plurifamiliars en bloc obert', 
            4: 'Plurifamiliars en bloc tancat'}

    mapping1 = {1: "De nova Construcció",
                2: "Rehabilitació integral"}

    mapping2 = {1: "Pendent d'enderroc", 
            2: "Solar", 
            3: "Buidat", 
            4: "Cimentació",
            5: "Estructura",
            6: "Tancaments exteriors",
            7: "Tancaments interiors",
            8: "Claus en mà",
            9: "NS/NC"}

    mapping3 = {
                    1: 'A',
                    1.2:"A",
                    2: 'B',
                    2.3: "B",
                    3: 'C',
                    4: 'D',
                    4.5: "D",
                    5: 'E',
                    5.3 : "C",
                    6: "F",
                    7: "G",
                    8: "En tràmits",
                    9: "Sense informació"
    }

    mapping4 = {
                    0: "Altres",
                    1: "Plaça d'aparcament opcional",
                    2: "Plaça d'aparcament inclosa",
                    3: "Sense plaça d'aparcament",
    }



    bbdd_estudi_prom['TIPO'] = bbdd_estudi_prom['TIPO'].map(mapping)

    bbdd_estudi_prom['TIPH'] = bbdd_estudi_prom['TIPH'].map(mapping1)


    bbdd_estudi_prom['ESTO'] = bbdd_estudi_prom['ESTO'].map(mapping2)

    bbdd_estudi_prom['QENERGC'] = bbdd_estudi_prom['QENERGC'].map(mapping3)

    bbdd_estudi_prom['APAR'] = bbdd_estudi_prom['APAR'].map(mapping4)


    # Importar BBDD habitatges
    bbdd_estudi_hab = pd.read_excel(path + 'P3007 BBDD desembre APCE.xlsx', sheet_name='Habitatges 2023')
    bbdd_estudi_hab.columns = bbdd_estudi_hab.iloc[0,:]
    bbdd_estudi_hab = bbdd_estudi_hab[bbdd_estudi_hab["ESTUDI"]==any]





    # ["Total dormitoris","Banys i lavabos","Cuines estàndard","Cuines americanes","Terrasses, balcons i patis","Estudi/golfes","Safareig","Altres interiors","Altres exteriors"]

    # ["DORM", "LAV", "cuina_normal", "cuina_amer", "TER", "Golfes", "Safareig","Altres interiors","Altres exteriors" ]

    bbdd_estudi_hab['TIPOG'] = np.where(bbdd_estudi_hab['TIPO'].isin([1,2]), 'Habitatges unifamiliars', 'Habitatges plurifamiliars')
    bbdd_estudi_hab['TIPO'] = bbdd_estudi_hab['TIPO'].map(mapping)
    bbdd_estudi_hab['QENERGC'] = bbdd_estudi_hab['QENERGC'].map(mapping3)
    bbdd_estudi_hab['APAR'] = bbdd_estudi_hab['APAR'].map(mapping4)

    bbdd_estudi_hab = bbdd_estudi_hab.dropna(axis=1 , how ='all')



    bbdd_estudi_hab = bbdd_estudi_hab.rename(columns = {'V0006':'Total dormitoris_aux', 
                                                            "DORM": "Total dormitoris",
                                                            "LAV": "Banys i lavabos",
                                                            "TER": "Terrasses, balcons i patis",
                                                            'NOMD01C':'Superfície útil',
                                                            "Preu_m2_util": "Preu m2 útil",
                                                            "NOMD01F_2022": "Preu mitjà",
                                                            'NOMD01P':'Estudi/golfes', 
                                                            'NOMD01Q':'Safareig', 
                                                            'NOMD01K': 'Cuines estàndard', 
                                                            'NOMD01L': 'Cuines americanes', 
                                                            "NOMD01R": "Altres interiors", 
                                                            "NOMD01S":"Altres exteriors"})

    bbdd_estudi_prom = bbdd_estudi_prom.rename(columns = {'V0006':'Total dormitoris_aux', 
                                                            "DORM": "Total dormitoris",
                                                            "LAV": "Banys i lavabos",
                                                            "TER": "Terrasses, balcons i patis",
                                                            'NOMD01C':'Superfície útil',
                                                            "Preu_m2_util": "Preu m2 útil",
                                                            'NOMD01P':'Estudi/golfes', 
                                                            'NOMD01Q':'Safareig', 
                                                            'NOMD01K': 'Cuines estàndard', 
                                                            'NOMD01L': 'Cuines americanes', 
                                                            "NOMD01R": "Altres interiors", 
                                                            "NOMD01S":"Altres exteriors"})


    # Canviar de nom tots els equipaments
    bbdd_estudi_hab = bbdd_estudi_hab.rename(columns = {'EQUIC_1': 'Zona enjardinada', 
                                                        'EQUIC_2': 'Parc infantil',
                                                        'EQUIC_3': 'Piscina comunitària', 
                                                        'EQUIC_4': 'Traster', 
                                                        'EQUIC_5': 'Ascensor', 
                                                        'EQUIC_6': 'Equipament Esportiu',  
                                                        'EQUIC_7': 'Sala de jocs', 
                                                        'EQUIC_8': 'Sauna', 
                                                        "EQUIC_9_50": "Altres",
                                                        'EQUIC_99': 'Cap dels anteriors'})
    bbdd_estudi_prom = bbdd_estudi_prom.rename(columns = {'EQUIC_1': 'Zona enjardinada', 
                                                        'EQUIC_2': 'Parc infantil',
                                                        'EQUIC_3': 'Piscina comunitària', 
                                                        'EQUIC_4': 'Traster', 
                                                        'EQUIC_5': 'Ascensor', 
                                                        'EQUIC_6': 'Equipament Esportiu',  
                                                        'EQUIC_7': 'Sala de jocs', 
                                                        'EQUIC_8': 'Sauna', 
                                                        "QUAL_ALTRES": "Altres",
                                                        'EQUIC_99': 'Cap dels anteriors'})
    bbdd_estudi_prom["Ascensor"] = np.where(bbdd_estudi_prom["Ascensor"]>=1, 1, bbdd_estudi_prom["Ascensor"])
    bbdd_estudi_hab["Ascensor"] = np.where(bbdd_estudi_hab["Ascensor"]>=1, 1, bbdd_estudi_hab["Ascensor"])


    # Canviar de nom totes les qualitats
    bbdd_estudi_hab = bbdd_estudi_hab.rename(columns = {"QUALIC_5": "Aire condicionat", 
                                                        "QUALIC_6": "Bomba de calor", 
                                                        "QUALI_A": "Aerotèrmia", 
                                                        'QUALIC_7':"Calefacció", 
                                                        'QUALIC_8':"Preinstal·lació d'A.C./B. Calor/Calefacció", 
                                                        'QUALIC_9': 'Parquet', 
                                                        'QUALIC_10':'Armaris encastats',
                                                        'QUALIC_12':'Placa de cocció amb gas',
                                                        'QUALIC_13':'Placa de cocció vitroceràmica',
                                                        "QUALIC_14":"Placa d'inducció",
                                                        'QUALIC_22':'Plaques solars'})


    bbdd_estudi_prom = bbdd_estudi_prom.rename(columns = {"QUALIC_5": "Aire condicionat", 
                                                        "QUALIC_6": "Bomba de calor", 
                                                        "QUALI_A": "Aerotèrmia", 
                                                        'QUALIC_7':"Calefacció", 
                                                        'QUALIC_8':"Preinstal·lació d'A.C./B. Calor/Calefacció", 
                                                        'QUALIC_9': 'Parquet', 
                                                        'QUALIC_10':'Armaris encastats',
                                                        'QUALIC_12':'Placa de cocció amb gas',
                                                        'QUALIC_13':'Placa de cocció vitroceràmica',
                                                        "QUALIC_14":"Placa d'inducció",
                                                        'QUALIC_22':'Plaques solars'})
    #  Canviar nom a tipus de calefacció
    bbdd_estudi_prom = bbdd_estudi_prom.rename(columns = {'CALEFC_3': 'De gasoil', 
                                                        'CALEFC_4': 'De gas natural', 
                                                        'CALEFC_5': 'De propà', 
                                                        'CALEFC_6': "D'electricitat", 
                                                        'CALEFC_9': "No s'indica tipus"})




    bbdd_estudi_prom['TIPV'] = np.where(bbdd_estudi_prom['TIPV_1'] >= 1, "Venda a través d'immobiliària independent",
                                        np.where(bbdd_estudi_prom['TIPV_2'] >= 1, "Venda a través d'immobiliaria del mateix promotor",
                                                np.where(bbdd_estudi_prom['TIPV_3'] >= 1, "Venda directa del promotor", "Sense informació")))


    bbdd_estudi_prom['TIPOL_VENDA'] = np.where(bbdd_estudi_prom['TIPOL_VENDA_1'] == 1, "0D",
                                        np.where(bbdd_estudi_prom['TIPOL_VENDA_2'] == 1, "1D",
                                                np.where(bbdd_estudi_prom['TIPOL_VENDA_3'] == 1, "2D",
                                                        np.where(bbdd_estudi_prom['TIPOL_VENDA_4'] == 1, "3D",
                                                            np.where(bbdd_estudi_prom['TIPOL_VENDA_5'] == 1, "4D", 
                                                                np.where(bbdd_estudi_prom['TIPOL_VENDA_6'] == 1, "5+D", "NA"))))))

                        
                                                    
    #  "Venda a través d'immobiliària independent", "Venda a través d'immobiliaria del mateix promotor", "Venda directa del promotor"

    bbdd_estudi_hab['TIPH'] = bbdd_estudi_hab['TIPH'].map(mapping1)

    bbdd_estudi_hab['ESTO'] = bbdd_estudi_hab['ESTO'].map(mapping2)


    vars = ['Zona enjardinada', 'Parc infantil', 'Piscina comunitària', 
            'Traster', 'Ascensor', 'Equipament Esportiu', 'Sala de jocs', 
            'Sauna', 'Altres', "Aire condicionat", "Bomba de calor", 
            "Aerotèrmia", "Calefacció", "Preinstal·lació d'A.C./B. Calor/Calefacció", 
            "Parquet", "Armaris encastats", 'Placa de cocció amb gas', 
            'Placa de cocció vitroceràmica', "Placa d'inducció", 'Plaques solars', "APAR"]
    vars_aux = ['Zona enjardinada', 'Parc infantil', 'Piscina comunitària', 
            'Traster', 'Ascensor', 'Equipament Esportiu', 'Sala de jocs', 
            'Sauna', 'Altres', "Aire condicionat", "Bomba de calor", 
            "Aerotèrmia", "Calefacció", "Preinstal·lació d'A.C./B. Calor/Calefacció", 
            "Parquet", "Armaris encastats", 'Placa de cocció amb gas', 
            'Placa de cocció vitroceràmica', "Placa d'inducció", 'Plaques solars', "Safareig","Terrasses, balcons i patis"]
    for i in vars:
        bbdd_estudi_prom[i] = bbdd_estudi_prom[i].replace(np.nan, 0)
    for i in vars_aux:
        bbdd_estudi_hab[i] = bbdd_estudi_hab[i].replace(np.nan, 0)
    bbdd_estudi_hab["Calefacció"] = bbdd_estudi_hab["Calefacció"].replace(' ', 0) 
    bbdd_estudi_prom["Calefacció"] = bbdd_estudi_prom["Calefacció"].replace(' ', 0) 


    bbdd_estudi_hab["Tram_Sup_util"] = bbdd_estudi_hab["Tram_Sup_util"].str.replace(" ", "")
    bbdd_estudi_hab["Tram_Sup_util"] = bbdd_estudi_hab["Tram_Sup_util"].str[3:]



    # Afegir categories a algunes columnes de la base de dades d'habitatge

    room_dict =  {i: f"{i}D" if i <= 4 else "5+D" for i in range(0, 20)}
    toilet_dict = {i: f"{i} Bany" if i <= 1 else "2 i més Banys" for i in range(1, 20)}
    bbdd_estudi_hab_mod = bbdd_estudi_hab.copy()

    bbdd_estudi_hab_mod['Total dormitoris'] = bbdd_estudi_hab_mod['Total dormitoris'].map(room_dict)
    bbdd_estudi_hab_mod['Banys i lavabos'] = bbdd_estudi_hab_mod['Banys i lavabos'].map(toilet_dict)
    bbdd_estudi_hab_mod["Terrasses, balcons i patis"] = np.where(bbdd_estudi_hab_mod["Terrasses, balcons i patis"]>=1, 1, 0)

    bbdd_estudi_hab["Nom DIST"] = bbdd_estudi_hab["Nom DIST"].str.replace(r'^\d{2}\s', '', regex=True)
    bbdd_estudi_hab_mod["Nom DIST"] = bbdd_estudi_hab_mod["Nom DIST"].str.replace(r'^\d{2}\s', '', regex=True)

    return([bbdd_estudi_prom, bbdd_estudi_hab, bbdd_estudi_hab_mod])

bbdd_estudi_prom_2023, bbdd_estudi_hab_2023, bbdd_estudi_hab_mod_2023 = tidy_bbdd_semestral(2023)


############################################################  IMPORTAR HISTÓRICO DE MUNICIPIOS 2016 - 2022 ################################################

@st.cache_data(show_spinner="**Carregant les dades... Esperi, siusplau**", max_entries=500)
def import_hist_mun():
    mun_2018_2019 = pd.read_excel(path + "Resum 2018 - 2019.xlsx", sheet_name="Municipis 2018-2019")
    mun_2019 = mun_2018_2019.iloc[:,14:27]

    mun_2020_2021 = pd.read_excel(path + "Resum 2020 - 2021.xlsx", sheet_name="Municipis")
    mun_2020 = mun_2020_2021.iloc[:,:13]
    mun_2020 = mun_2020.dropna(how ='all',axis=0)
    mun_2021 = mun_2020_2021.iloc[:,14:27]
    mun_2021 = mun_2021.dropna(how ='all',axis=0)

    mun_2022 = pd.read_excel(path + "Resum 2022.xlsx", sheet_name="Municipis")
    mun_2022 = mun_2022.iloc[:,14:27]
    mun_2022 = mun_2022.dropna(how ='all',axis=0)

    mun_2023 = pd.read_excel(path + "Resum 2023.xlsx", sheet_name="Municipis")
    mun_2023 = mun_2023.iloc[:,14:27]
    mun_2023 = mun_2023.dropna(how ='all',axis=0)

    maestro_estudi = pd.read_excel(path + "Maestro estudi_oferta.xlsx", sheet_name="Maestro")

    return([mun_2019, mun_2020, mun_2021, mun_2022, mun_2023, maestro_estudi])
mun_2019, mun_2020, mun_2021, mun_2022, mun_2023, maestro_estudi = import_hist_mun()

############################################################  IMPORTAR HISTÓRICO DE DISTRITOS DE BCN 2016 - 2023 ################################################

@st.cache_data(show_spinner="**Carregant les dades... Esperi, siusplau**", max_entries=500)
def import_hist_dis():
    dis_2018_2019 = pd.read_excel(path + "Resum 2018 - 2019.xlsx", sheet_name="BCN+districtes+barris")
    dis_2019 = dis_2018_2019.iloc[:,14:27]

    dis_2020_2021 = pd.read_excel(path + "Resum 2020 - 2021.xlsx", sheet_name="BCN+districtes+barris")
    dis_2020 = dis_2020_2021.iloc[:,:13]
    dis_2020 = dis_2020.dropna(how ='all',axis=0)
    dis_2021 = dis_2020_2021.iloc[:,14:27]
    dis_2021 = dis_2021.dropna(how ='all',axis=0)

    dis_2022 = pd.read_excel(path + "Resum 2022.xlsx", sheet_name="BCN+districtes+barris")
    dis_2022 = dis_2022.iloc[:,14:27]
    dis_2022 = dis_2022.dropna(how ='all',axis=0)

    dis_2023 = pd.read_excel(path + "Resum 2023.xlsx", sheet_name="BCN districte+barris")
    dis_2023 = dis_2023.iloc[:,14:27]
    dis_2023 = dis_2023.dropna(how ='all',axis=0)

    return([dis_2019, dis_2020, dis_2021, dis_2022, dis_2023])
dis_2019, dis_2020, dis_2021, dis_2022, dis_2023 = import_hist_dis()

############################################################  IMPORTAR HISTÓRICO DE DISTRITOS DE BCN 2016 - 2023 ################################################

@st.cache_data(show_spinner="**Carregant les dades... Esperi, siusplau**", max_entries=500)
def tidy_data(mun_year, year):
    df =mun_year.T
    df.columns = df.iloc[0,:]
    df = df.iloc[1:,:].reset_index()
    df.columns.values[:3] = ['Any', 'Tipologia', "Variable"]
    df['Tipologia'] = df['Tipologia'].ffill()
    df['Any'] = year
    geo = df.columns[3:].values
    df_melted = pd.melt(df, id_vars=['Any', 'Tipologia', 'Variable'], value_vars=geo, value_name='Valor')
    df_melted.columns.values[3] = 'GEO'
    return(df_melted)

############################################################  CALCULOS PROVINCIAS, AMBITOS TERRITORIALES Y COMARCAS ################################################
def weighted_mean(data):
    weighted_sum = (data['Valor'] * data['Unitats']).sum()
    sum_peso = data['Unitats'].sum()
    # data["Valor"] = weighted_sum / sum_peso
    return weighted_sum / sum_peso

@st.cache_data(show_spinner="**Carregant les dades... Esperi, siusplau**", max_entries=500)
def geo_mun():
    df_vf_aux = pd.DataFrame()

    for df_frame, year in zip(["mun_2019", "mun_2020", "mun_2021", "mun_2022", "mun_2023"], [2019, 2020, 2021, 2022, 2023]):
        df_vf_aux = pd.concat([df_vf_aux, tidy_data(eval(df_frame), year)], axis=0)


    df_vf_aux['Variable']= np.where(df_vf_aux['Variable']=="Preu de     venda per      m² útil (€)", "Preu de venda per m² útil (€)", df_vf_aux['Variable'])
    df_vf_aux['Valor'] = pd.to_numeric(df_vf_aux['Valor'], errors='coerce')
    df_vf_aux['GEO'] = np.where(df_vf_aux['GEO']=="Municipis de Catalunya", "Catalunya", df_vf_aux['GEO'])
    df_vf_aux = df_vf_aux[~df_vf_aux['GEO'].str.contains("província|Província|Municipis")]

    df_vf_merged = pd.merge(df_vf_aux, maestro_estudi, how="left", on="GEO")
    df_vf_merged = df_vf_merged[~df_vf_merged["Província"].isna()].dropna(axis=1, how="all")
    df_vf = df_vf_merged[df_vf_merged["Variable"]!="Unitats"]
    df_unitats = df_vf_merged[df_vf_merged["Variable"]=="Unitats"].drop("Variable", axis=1)
    df_unitats = df_unitats.rename(columns={"Valor": "Unitats"})
    # df_vf[df_vf["Província"].isna()]["GEO"].unique()
    df_final_cat = pd.merge(df_vf, df_unitats, how="left")
    df_final = df_final_cat[df_final_cat["GEO"]!="Catalunya"]
    df_final_cat_aux1 = df_final_cat[df_final_cat["GEO"]=="Catalunya"][["Any", "Tipologia", "Variable","Valor"]]
    cat_df_aux2_melted = pd.melt(df_final_cat[df_final_cat["GEO"]=="Catalunya"][["Any", "Tipologia", "Unitats"]], id_vars=["Any", "Tipologia"], var_name="Variable", value_name="Unitats")
    cat_df_aux2_melted["Unitats"] = cat_df_aux2_melted["Unitats"].astype("int64")
    cat_df_aux2_melted = cat_df_aux2_melted.rename(columns={"Unitats":"Valor"})
    df_final_cat = pd.concat([df_final_cat_aux1, cat_df_aux2_melted], axis=0)


    ambits_df_aux1 = df_final.groupby(["Any", "Tipologia", "Variable", "Àmbits territorials"]).apply(weighted_mean).reset_index().rename(columns= {0:"Valor"})
    ambits_df_aux2 = df_final[["Any","Àmbits territorials","Tipologia", "GEO", "Unitats"]].groupby(["Any", "Àmbits territorials", "Tipologia"]).sum().reset_index()
    ambits_df_aux2_melted = pd.melt(ambits_df_aux2, id_vars=["Any", "Tipologia", "Àmbits territorials"], var_name="Variable", value_name="Unitats")
    ambits_df_aux2_melted["Unitats"] = ambits_df_aux2_melted["Unitats"].astype("int64")
    ambits_df_aux2_melted = ambits_df_aux2_melted.rename(columns={"Unitats":"Valor"})
    ambits_df = pd.concat([ambits_df_aux1, ambits_df_aux2_melted], axis=0)
    ambits_df = ambits_df.rename(columns={"Àmbits territorials":"GEO"})

    comarques_df_aux1 = df_final.groupby(["Any", "Tipologia", "Variable", "Comarques"]).apply(weighted_mean).reset_index().rename(columns= {0:"Valor"}).dropna(axis=0)
    comarques_df_aux2 = df_final[["Any","Comarques","Tipologia", "GEO", "Unitats"]].drop_duplicates(["Any","Comarques","Tipologia", "GEO", "Unitats"]).groupby(["Any", "Comarques", "Tipologia"]).sum().reset_index()
    comarques_df_aux2_melted = pd.melt(comarques_df_aux2, id_vars=["Any", "Tipologia", "Comarques"], var_name="Variable", value_name="Unitats")
    comarques_df_aux2_melted["Unitats"] = comarques_df_aux2_melted["Unitats"].astype("int64")
    comarques_df_aux2_melted = comarques_df_aux2_melted.rename(columns={"Unitats":"Valor"})
    comarques_df = pd.concat([comarques_df_aux1, comarques_df_aux2_melted], axis=0)
    comarques_df = comarques_df.rename(columns={"Comarques":"GEO"})


    provincia_df_aux1 = df_final.groupby(["Any", "Tipologia", "Variable", "Província"]).apply(weighted_mean).reset_index().rename(columns= {0:"Valor"})
    provincia_df_aux2 = df_final[["Any","Província","Tipologia", "GEO", "Unitats"]].drop_duplicates(["Any","Província","Tipologia", "GEO", "Unitats"]).groupby(["Any", "Província", "Tipologia"]).sum().reset_index()
    provincia_df_aux2_melted = pd.melt(provincia_df_aux2, id_vars=["Any", "Tipologia", "Província"], var_name="Variable", value_name="Unitats")
    provincia_df_aux2_melted["Unitats"] = provincia_df_aux2_melted["Unitats"].astype("int64")
    provincia_df_aux2_melted = provincia_df_aux2_melted.rename(columns={"Unitats":"Valor"})
    provincia_df = pd.concat([provincia_df_aux1, provincia_df_aux2_melted], axis=0)
    provincia_df = provincia_df.rename(columns={"Província":"GEO"})

    return([df_vf_aux, df_vf, df_final_cat, df_final, ambits_df, comarques_df, provincia_df])

df_vf_aux, df_vf, df_final_cat, df_final, ambits_df, comarques_df, provincia_df = geo_mun()

@st.cache_data(show_spinner="**Carregant les dades... Esperi, siusplau**", max_entries=500)
def geo_dis_long():
    df_vf_aux = pd.DataFrame()
    for df_frame, year in zip(["dis_2019", "dis_2020", "dis_2021", "dis_2022", "dis_2023"], [2019, 2020, 2021, 2022, 2023]):
        df_vf_aux = pd.concat([df_vf_aux, tidy_data(eval(df_frame), year)], axis=0)
    df_vf_aux['Variable']= np.where(df_vf_aux['Variable']=="Preu de     venda per      m² útil (€)", "Preu de venda per m² útil (€)", df_vf_aux['Variable'])
    df_vf_aux['Valor'] = pd.to_numeric(df_vf_aux['Valor'], errors='coerce')
    df_vf_aux = df_vf_aux[df_vf_aux['GEO']!="Municipi de Barcelona"]

    df_vf_aux = df_vf_aux[df_vf_aux["GEO"].isin(["Ciutat Vella", "01 Ciutat Vella",  "Eixample", "02 Eixample", "Sants-Montjuïc", "03 Sants-Montjuïc"
                                        "Les Corts", "04 Les Corts", "Sarrià - Sant Gervasi", "05 Sarrià - Sant Gervasi", "Gràcia", "06 Gràcia",
                                        "Horta-Guinardó", "07 Horta-Guinardó", "Nou Barris", "08 Nou Barris", "Sant Andreu", "09 Sant Andreu",
                                        "Sant Martí", "10 Sant Martí"])]
    for i in ["01 ", "02 ", "03 ", "04 ", "05 ", "06 ", "07 ", "08 ", "09 ", "10 "]:
        df_vf_aux["GEO"] = df_vf_aux["GEO"].str.replace(i, "")

    return(df_vf_aux)
df_dis_long = geo_dis_long()



############################################################  CATALUNYA: 2022 ################################################
if selected == "Catalunya":
    st.sidebar.header("**ESTUDI D'OFERTA DE NOVA CONSTRUCCIÓ**")
    edicio_any = ["2022","2023"]
    selected_edition = st.sidebar.radio("**Any**", edicio_any)
    if selected_edition=="2022":
        index_names = ["Introducció","Característiques", "Qualitats i equipaments", "Superfície i preus", "Comparativa 2022-2021"]
        selected_index = st.sidebar.radio("**Contingut**", index_names)

        if selected_index=="Introducció":
            st.subheader("**INTRODUCCIÓ**")
            st.write("""<p style="margin-top: 10px"> L’Estudi de l’Oferta d’Habitatge de Nova Construcció de 2022 ha inclòs un total de 84
                municipis de Catalunya, en els quals s’han censat 928
                promocions d’obra nova (87 menys que l’any passat) i un
                total de 21.796 habitatges, dels quals un 37,5% estan a
                la venda (8.181, un 30% més que l’any passat).
                Aquesta oferta activa -en funció de
                les promocions- és força similar a
                les províncies de Barcelona i Tarragona (36,2% i 33,2% respectivament), i s’incrementa significativament a Girona (52,1%) i Lleida (44,8%).
                De tots els municipis analitzats, el que compta amb més
                presència d’oferta és el de Barcelona, amb un total de
                199 promocions i 1.390 habitatges en venda. Addicionalment, els municipis amb més promocions de Catalunya són
                Sabadell, L’Hospitalet de Llobregat, Badalona, Terrassa i Vilanova i la Geltrú.
                Dels habitatges en oferta de venda a les promocions analitzades en aquest estudi un 25,5% estan finalitzats i un
                47,2% es troben en diferents fases constructives. 
                Per tipologies edificatòries, destaquen els habitatges plurifamiliars de bloc tancat, concretament, el 57,9% dels
                habitatges, mentre que els plurifamiliars de bloc obert registren un 38%. A més distància, es situen els habitatges
                unifamiliars adossats (3,8%) i els unifamiliars aïllats (0,4%).
                Finalment, la major part dels habitatges inclosos en l’estudi 2022 són d’obra nova (93,6%), reduint-se la rehabilitació integral
                a un 6,4% (4 dècimes menys que a 2021), majoritàriament concentrada als municipis de la província de Barcelona
                (88,9%) i de forma destacada al municipi de Barcelona (31,5% del total d’habitatges en venda).</p></body>""",
            unsafe_allow_html=True
        )
            left_col, right_col = st.columns((1, 1))
            with left_col:
                st.markdown("""**Nombre de promocions per província a Catalunya**""")
                @st.cache_data(show_spinner="**Carregant les dades... Esperi, siusplau**", max_entries=500)
                def map_prov_prom():
                    provprom_map = bbdd_estudi_prom[["PROVINCIA"]].value_counts().reset_index()
                    provprom_map.columns = ["NAME_2", "PROMOCIONS"]
                    shapefile_prov = gpd.read_file(path + "Provincias.geojson")
                    shapefile_prov = shapefile_prov[shapefile_prov["NAME_1"]=="Cataluña"]
                    fig, ax = plt.subplots(1,1, figsize=(10,10))
                    divider = make_axes_locatable(ax)
                    tmp = shapefile_prov.copy()
                    tmp = pd.merge(tmp, provprom_map, how="left", on="NAME_2")
                    # cax = divider.append_axes("right", size="3%", pad=-1) #resize the colorbar
                    cmap = colors.LinearSegmentedColormap.from_list("mi_paleta", ["#DAE4E0","#008B6C"]) 
                    tmp.plot(column='PROMOCIONS', ax=ax, cmap=cmap, legend=False)
                    tmp.geometry.boundary.plot(color='black', ax=ax, linewidth=0.3) #Add some borders to the geometries
                    for i, row in tmp.iterrows():
                        x, y = row['geometry'].centroid.coords[0]
                        ax.annotate(f"""{row['NAME_2']}\n{row["PROMOCIONS"]}""", xy=(x, y), xytext=(3,3), textcoords="offset points", fontsize=10, color="black")
                                        # bbox=dict(facecolor='white', alpha=0.5)
                                        # arrowprops=dict(facecolor='black', arrowstyle="->")
                                        
                    ax.axis('off')
                    fig.patch.set_alpha(0)
                    return(fig)
                st.pyplot(map_prov_prom())
            with right_col:
                st.markdown("**Nombre d'habitatges en oferta per municipis a Catalunya**")
                @st.cache_data(show_spinner="**Carregant les dades... Esperi, siusplau**", max_entries=500)
                def map_mun_hab_oferta():
                    prommun_map = bbdd_estudi_prom[["CODIMUN", "Municipi","HABIP"]].groupby(["CODIMUN", "Municipi"]).sum().reset_index()
                    prommun_map.columns = ["municipi", "Municipi_n", "Habitatges en oferta"]
                    prommun_map["municipi"] = prommun_map["municipi"].astype(float)

                    shapefile_mun = gpd.read_file(path + "shapefile_mun.geojson")
                    shapefile_mun["municipi"] = shapefile_mun["municipi"].astype(float)
                    tmp = pd.merge(shapefile_mun, prommun_map, how="left", on="municipi")
                    fig, ax = plt.subplots(1,1, figsize=(20,20))
                    divider = make_axes_locatable(ax)
                    cax = divider.append_axes("right", size="3%", pad=-1) #resize the colorbar
                    cmap = colors.LinearSegmentedColormap.from_list("mi_paleta", ["#AAC4BA","#008B6C"]) 

                    tmp.plot(column='Habitatges en oferta', ax=ax,cax=cax, cmap=cmap, legend=True)
                    tmp.geometry.boundary.plot(color='black', ax=ax, linewidth=0.3) #Add some borders to the geometries
                    ax.axis('off')
                    fig.patch.set_alpha(0)
                    return(fig)
                st.pyplot(map_mun_hab_oferta())

        if selected_index=="Característiques":
            left_col, right_col = st.columns((1, 1))
            with left_col:
                st.subheader("**CARACTERÍSTIQUES**")
                st.write("""
                <p>
                    Les principals tipologies en oferta als municipis catalans estudiats són els habitatges de 3 dormitoris i 2
                    banys (45,3%). Amb percentatges menors, però significatius es contemplen els habitatges de 2 dormitoris i 2
                    banys (16,8%), els de 2 dormitoris i 1 bany (12,0%), i els de 4 dormitoris i 2 banys (8,8%).
                    Els habitatges a la venda a Catalunya per nombre de dormitoris són els següents: els tipus loft (39); els
                    d’un dormitori (431) els de 2 dormitoris (2.432); els de tres dormitoris (4.138); els de quatre dormitoris (1.088), i
                    els de cinc o més dormitoris (53).
                </p>""",
                unsafe_allow_html=True
                )
            with right_col:
                def plot_caracteristiques():
                    table61_tipo = bbdd_estudi_hab.groupby(['Total dormitoris', 'Banys i lavabos']).size().div(len(bbdd_estudi_hab_mod)).reset_index(name='Proporcions').sort_values(by="Proporcions", ascending=False)
                    table61_tipo["Proporcions"] = table61_tipo["Proporcions"]*100
                    table61_tipo["Tipologia"] = np.where(table61_tipo["Banys i lavabos"]==1, table61_tipo["Total dormitoris"].astype(str) + " dormitoris i " + table61_tipo["Banys i lavabos"].astype(str) + " bany", table61_tipo["Total dormitoris"].astype(str) + " dormitoris i " + table61_tipo["Banys i lavabos"].astype(str) + " banys")
                    fig = px.bar(table61_tipo.head(4), x="Proporcions", y="Tipologia", orientation='h', title="", 
                    labels={'x':"Proporcions sobre el total d'habitatges", 'y':"Tipologia"})
                    fig.layout.xaxis.title.text = "Proporcions sobre el total d'habitatges"
                    fig.layout.yaxis.title.text = "Tipologia"
                    fig.layout.title.text = "Principals tipologies dels habitatges en oferta"
                    fig.update_traces(marker=dict(color="#66b9a7"))
                    return(fig)
                # st.write(plot_caracteristiques())
                st.plotly_chart(plot_caracteristiques(), use_container_width=True, responsive=True)

        if selected_index=="Qualitats i equipaments":
            st.subheader("**QUALITATS I EQUIPAMENTS**")
            st.write("""
            <p>
                Les qualitats més recurrents en els habitatges són: la bomba de calor -fred
                i calor- (83,6%), la placa d’inducció (69,8%), el parquet (62,5%), els armaris
                encastats (59,4%), l’aerotèrmia (47,3%), la calefacció instal·lada només
                calor (42,94%), la placa de cocció vitroceràmica (21,7%) i les plaques solars
                (12,5%).
                Quant a equipaments, el més comú és l’ascensor (91,6%), seguit a certa
                distància per la piscina comunitària (50,3%), el traster (48,4%) i la zona enjardinada
                (37,7%).
            </p>""",
            unsafe_allow_html=True
            )
            left_col, right_col = st.columns((1, 1))
            with left_col:
                st.write("""<p><b>Principals qualitats dels habitatges</b></p>""", unsafe_allow_html=True)
                def plot_qualitats():
                    table62_hab = bbdd_estudi_hab[["Aire condicionat","Bomba de calor","Aerotèrmia","Calefacció","Preinstal·lació d'A.C./B. Calor/Calefacció",'Parquet','Armaris encastats','Placa de cocció amb gas','Placa de cocció vitroceràmica',"Placa d'inducció",'Plaques solars']].rename(columns={"Aerotèrmia":"Aerotèrmia"}).sum(axis=0)
                    table62_hab = pd.DataFrame({"Qualitats":table62_hab.index, "Total":table62_hab.values})
                    table62_hab = table62_hab.set_index("Qualitats").apply(lambda row: (row / bbdd_estudi_hab.shape[0])*100).reset_index().sort_values("Total", ascending=True)
                    fig = px.bar(table62_hab, x="Total", y="Qualitats", orientation='h', title="", labels={'x':"Proporcions sobre el total d'habitatges", 'y':"Qualitats"})
                    fig.layout.xaxis.title.text = "Proporcions sobre el total d'habitatges"
                    fig.layout.yaxis.title.text = "Qualitats"
                    fig.update_traces(marker=dict(color="#66b9a7"))
                    return(fig)
                st.plotly_chart(plot_qualitats(), use_container_width=True, responsive=True)

            with right_col:
                st.write("""<p><b>Principals equipaments dels habitatges</b></p>""", unsafe_allow_html=True)
                def plot_equipaments():
                    table67_hab = bbdd_estudi_hab[["Zona enjardinada", "Parc infantil", "Piscina comunitària", "Traster", "Ascensor", "Equipament Esportiu", "Sala de jocs", "Sauna", "Altres", "Cap dels anteriors"]].sum(axis=0)
                    table67_hab = pd.DataFrame({"Equipaments":table67_hab.index, "Total":table67_hab.values})
                    table67_hab = table67_hab.set_index("Equipaments").apply(lambda row: row.mul(100) / bbdd_estudi_hab.shape[0]).reset_index().sort_values("Total", ascending=True)
                    fig = px.bar(table67_hab, x="Total", y="Equipaments", orientation='h', title="", labels={'x':"Proporcions sobre el total d'habitatges", 'y':"Equipaments"})
                    fig.layout.xaxis.title.text = "Proporcions sobre el total d'habitatges"
                    fig.layout.yaxis.title.text = "Equipaments"
                    fig.update_traces(marker=dict(color="#66b9a7"))
                    return(fig)
                st.plotly_chart(plot_equipaments(), use_container_width=True, responsive=True)

        if selected_index=="Superfície i preus":
            left_col, right_col = st.columns((1, 1))
            with left_col:
                st.subheader("SUPERFÍCIE I PREUS")
                st.write("""
                <p>
                    En general, conforme augmenta la superfície també ho
                    fa el nombre de dormitoris, situant-se la màxima recur-
                    rència en els habitatges de 3 dormitoris entre els 60m\u00b2 i els
                    90m\u00b2, i en els de 2 dormitoris amb superfícies inferiors
                    als 70m\u00b2.
                    La mitjana de la superfície útil dels habitatges en venda
                    en els municipis estudiats és de 80,7m\u00b2, amb un preu
                    mitjà de 368.809€ (4.532,6€/m\u00b2 útil). Per sota de la mitjana de preu, a nivell general, es situen els habitatges d’un,
                    de dos i de tres dormitoris. Si l’anàlisi es fa a partir de la
                    mitjana del preu m\u00b2 útil, per sota de la mitjana resten els
                    habitatges de 3 i 4 dormitoris.
                    El 16,8% del conjunt d’habitatges en oferta de venda
                    no supera els 210.000€. Entre aquests habitatges se situen el 46,6% de les d’un dormitori i el 29,2% dels de
                    dos dormitoris. A la banda més alta es troben el 9,9% d’habitatges amb preus superiors als 600.000€, entre els
                    quals es localitza el 66,0% dels de cinc o més dormitoris.
                    Els habitatges unifamiliars obtenen mitjanes de superfície força més altes (155,5m\u00b2), així com de preu
                    (515.392€), però el m\u00b2 útil (3.302€/m\u00b2) se situa per sota
                    la mitjana general, evidenciant que el desplaçament a
                    l’alça del preu no compensa el de la superfície.
                    Els habitatges plurifamiliars estan més propers a les
                    mitjanes generals, doncs aporten força més influència sobre aquestes, amb una mitjana de superfície de
                    77,5m\u00b2, un preu de venda de 362.492€, i un preu de venda per m\u00b2 útil de 4.586€.
                </p>""",
                unsafe_allow_html=True
                )

            with right_col:
                st.write("""<p><b>Preu mitjà per tipologia d'habitatge</b></p>""", unsafe_allow_html=True)
                def indicadors_preu_mitjanes():
                    table76_tipo = bbdd_estudi_hab_mod[["Total dormitoris", "TIPOG","Superfície útil", "Preu mitjà", "Preu m2 útil"]].set_index(["Total dormitoris", "TIPOG"]).groupby(["TIPOG", "Total dormitoris"]).apply(np.mean).reset_index()
                    table76_total = bbdd_estudi_hab_mod[["Total dormitoris","Superfície útil", "Preu mitjà", "Preu m2 útil"]].set_index(["Total dormitoris"]).groupby(["Total dormitoris"]).apply(np.mean).reset_index()
                    table76_total["TIPOG"] = "Total habitatges"
                    table76 = pd.concat([table76_tipo, table76_total], axis=0)
                    table76 = pd.merge(table76, bbdd_estudi_hab_mod[["TIPOG","Total dormitoris"]].groupby(["TIPOG","Total dormitoris"]).size().reset_index().rename(columns={0:"Total"}), how="left", on=["TIPOG","Total dormitoris"])
                    table76 = table76.rename(columns={"TIPOG":"Tipologia"})
                    fig = px.bar(table76, x="Preu mitjà", y="Total dormitoris", color="Tipologia", orientation='h', color_discrete_sequence=["#00D0A3","#AAC4BA","#008B6C"], barmode="group", title="", labels={'x':"Preu m\u00b2 útil (mitjana)", 'y':"Tipologia d'habitatge"})
                    fig.layout.xaxis = dict(title="Preu mitjà", tickformat=",d")
                    fig.layout.yaxis = dict(title="Tipologia d'habitatge")

                    fig.update_layout(font=dict(size=13), legend=dict(orientation='h', yanchor='bottom', y=1, xanchor='right', x=0.75))
                    return(fig)
                st.plotly_chart(indicadors_preu_mitjanes(), use_container_width=True, responsive=True)
            left, right = st.columns((1,1))
            with left:
                st.write("""<p><b>Preu per m\u00b2 útil per tipologia d'habitatge</b></p>""", unsafe_allow_html=True)
                def indicadors_preum2_mitjanes():
                    table76_tipo = bbdd_estudi_hab_mod[["Total dormitoris", "TIPOG","Superfície útil", "Preu mitjà", "Preu m2 útil"]].set_index(["Total dormitoris", "TIPOG"]).groupby(["TIPOG", "Total dormitoris"]).apply(np.mean).reset_index()
                    table76_total = bbdd_estudi_hab_mod[["Total dormitoris","Superfície útil", "Preu mitjà", "Preu m2 útil"]].set_index(["Total dormitoris"]).groupby(["Total dormitoris"]).apply(np.mean).reset_index()
                    table76_total["TIPOG"] = "Total habitatges"
                    table76 = pd.concat([table76_tipo, table76_total], axis=0)
                    table76 = pd.merge(table76, bbdd_estudi_hab_mod[["TIPOG","Total dormitoris"]].groupby(["TIPOG","Total dormitoris"]).size().reset_index().rename(columns={0:"Total"}), how="left", on=["TIPOG","Total dormitoris"])
                    table76 = table76.rename(columns={"TIPOG":"Tipologia"})
                    fig = px.bar(table76, x="Preu m2 útil", y="Total dormitoris", color="Tipologia", orientation='h', color_discrete_sequence=["#00D0A3","#AAC4BA","#008B6C"], barmode="group", title="", labels={'x':"Preu m\u00b2 útil (mitjana)", 'y':"Tipologia d'habitatge"})
                    fig.layout.xaxis = dict(title="Preu per m\u00b2 útil", tickformat=",d")
                    fig.layout.yaxis.title.text = "Tipologia d'habitatge"
                    fig.update_layout(font=dict(size=13), legend=dict(orientation='h', yanchor='bottom', y=1, xanchor='right', x=0.75))
                    return(fig)
                st.plotly_chart(indicadors_preum2_mitjanes(), use_container_width=True, responsive=True)
            with right:
                st.write("""<p><b>Superfície útil per tipologia d'habitatge</b></p>""", unsafe_allow_html=True)
                def indicadors_super_mitjanes():
                    table76_tipo = bbdd_estudi_hab_mod[["Total dormitoris", "TIPOG","Superfície útil", "Preu mitjà", "Preu m2 útil"]].set_index(["Total dormitoris", "TIPOG"]).groupby(["TIPOG", "Total dormitoris"]).apply(np.mean).reset_index()
                    table76_total = bbdd_estudi_hab_mod[["Total dormitoris","Superfície útil", "Preu mitjà", "Preu m2 útil"]].set_index(["Total dormitoris"]).groupby(["Total dormitoris"]).apply(np.mean).reset_index()
                    table76_total["TIPOG"] = "Total habitatges"
                    table76 = pd.concat([table76_tipo, table76_total], axis=0)
                    table76 = pd.merge(table76, bbdd_estudi_hab_mod[["TIPOG","Total dormitoris"]].groupby(["TIPOG","Total dormitoris"]).size().reset_index().rename(columns={0:"Total"}), how="left", on=["TIPOG","Total dormitoris"])
                    table76 = table76.rename(columns={"TIPOG":"Tipologia"})
                    fig = px.bar(table76, x="Superfície útil", y="Total dormitoris", color="Tipologia", orientation='h', color_discrete_sequence=["#00D0A3","#AAC4BA","#008B6C"], barmode="group", title="", labels={'x':"Preu m\u00b2 útil (mitjana)", 'y':"Tipologia d'habitatge"})
                    fig.layout.xaxis.title.text = "Superfície útil"
                    fig.layout.yaxis.title.text = "Tipologia d'habitatge"
                    fig.update_layout(font=dict(size=13), legend=dict(orientation='h', yanchor='bottom', y=1, xanchor='right', x=0.75))
                    return(fig)
                st.plotly_chart(indicadors_super_mitjanes(), use_container_width=True, responsive=True)

        if selected_index=="Comparativa 2022-2021":
            left_col, right_col = st.columns((1, 1))
            with left_col: 
                st.subheader("**COMPARATIVA 2022-2021**") 
                st.write("""
                <p>
                    El 2022, els municipis estudiats registren un nombre de promocions inferior en 87 unitats respecte de
                    2021, aconseguint les 928. En relació amb el nombre
                    d’habitatges, el total de 2022 (8.181 habitatges) suposa un increment del 30% respecte dels 6.294 habitatges
                    registrats el 2021. Cal fer esment que de les 1.015 promocions de 2021, 601 ja han estat totalment venudes
                    al 2022 i, en relació als habitatges de 2021, el 52,6%
                    han estat venuts. En definitiva, el cens dut a terme el
                    2022 -com va passar l’any anterior- suposa una important renovació de les unitats mostrals: el 55,4% de les
                    promocions són de nova incorporació, i pel que fa als
                    habitatges es van incorporar un 63,5% de nous respecte
                    a l’any 2021.
                    Respecte de les tipologies de promoció, les variacions
                    respecte 2021 són molt atenuades, mantenint-se la seva
                    distribució proporcional. Si aquesta mateixa anàlisi es
                    fa per habitatges, pràcticament no varien els números
                    de 2022 en relació amb 2021 i, lògicament per la seva
                    morfologia, els habitatges plurifamiliars són la majoria
                    (95,9% el 2022 vers 94,7% el 2021).
                </p>
                <p>
                    La superfície mitjana dels habitatges a la venda el
                    2022 és de 80,7m\u00b2, amb un descens del 4,9% respecte de 2021. Aquest descens es registra en els diferents
                    tipus d’habitatge, a excepció dels de 5 i més dormitoris, que registren un increment de superfície del 7,4%.
                    El preu mitjà de l’habitatge a la venda en els municipis
                    estudiats a Catalunya el 2022 és de 368.809€, un 2%
                    menys que el registrat el 2021. Aquest descens de preu
                    es dona només a la tipologia d’habitatges de 3 dormitoris (la més nombrosa), mentre que a la resta de les
                    tipologies el preu s’incrementa de forma molt lleu, entre
                    un 0,8% i un 2%, excepte els habitatges de 5 i més dormitoris, amb un augment del 5,7%, si bé només hi ha 53
                    unitats censades. Pel que fa al preu per m\u00b2 útil, en el conjunt dels municipis estudiats, és de 4.533€, valor que suposa un preu
                    superior en un 2,5% respecte del 2021.
                </p>
                <p>
                    Per tipologia, els habitatges unifamiliars registren un descens del
                    -9,0% pel que fa a superfície mitjana, i un lleuger -0,9%
                    pel que fa al preu mitjà de venda, mentre que el preu per
                    m\u00b2 útil s’incrementa de mitjana un 8,3%.
                    Per altra banda, els habitatges plurifamiliars veuen disminuïda la seva
                    superfície (-3,2%), i presenten variació quant a preu,
                    amb un descens del preu mitjà de venda del -1,6%, i un
                    augment d’un 2,0% pel que fa a preu m\u00b2 útil.
                </p>
                <p>
                    En aquest sentit, cal recordar que l’evolució de l’IPC a
                    l’exercici 2022 ha estat del 8%.
                </p>""",
                unsafe_allow_html=True
                )
            with right_col:
                st.markdown("")
                st.write("""<p><b>Variació anual (%) dels principals indicadors per tipologia d'habitatge</b></p>""", unsafe_allow_html=True)
                @st.cache_data(show_spinner="**Carregant les dades... Esperi, siusplau**", max_entries=500)
                def plot_var_CAT():
                    table117 = pd.read_excel(path + "Estudi_oferta_taules 2022.xlsx", sheet_name="table117", header=1).iloc[1:,]
                    table121 = pd.read_excel(path + "Estudi_oferta_taules 2022.xlsx", sheet_name="table121", header=1).iloc[1:,]
                    table125 = pd.read_excel(path + "Estudi_oferta_taules 2022.xlsx", sheet_name="table125", header=1).iloc[1:,]
                    table117 = table117[(table117["Província"].isna()) & (table117["Municipi"].isna())][["Variació % Preu m2 útil","Variació % Preu mitjà", "Variació % Superfície útil"]]
                    table121 = table121[(table121["Província"].isna()) & (table121["Municipi"].isna())][["Variació % Preu m2 útil","Variació % Preu mitjà", "Variació % Superfície útil"]]
                    table125 = table125[(table125["Província"].isna()) & (table125["Municipi"].isna())][["Variació % Preu m2 útil","Variació % Preu mitjà", "Variació % Superfície útil"]]
                    table_var = pd.concat([table117, table121, table125], axis=0)
                    table_var["Tipologia"] = ["Total habitatges", "Habitatges unifamiliars", "Habitatges plurifamiliars"]
                    table_var_melted = pd.melt(table_var, id_vars="Tipologia", var_name = "Variable")

                    fig = px.bar(table_var_melted, x="Tipologia", y="value", color="Variable", color_discrete_sequence=["#008B6C","#00D0A3","#AAC4BA"], barmode="group", title="", labels={'x':"Preu m\u00b2 útil (mitjana)", 'y':"Tipologia d'habitatge"})
                    fig.layout.xaxis.title.text = "Tipologia"
                    fig.layout.yaxis.title.text = "Variació anual (%)"
                    fig.update_layout(font=dict(size=13), legend=dict(orientation='h', yanchor='bottom', y=1, x=0))
                    return(fig)
                st.plotly_chart(plot_var_CAT(), use_container_width=True, responsive=True)

            def table_geo_cat(any_ini, any_fin):
                    df_cat = df_final_cat[(df_final_cat["Any"]>=any_ini) & (df_final_cat["Any"]<=any_fin)].drop_duplicates(["Any", "Tipologia", "Variable", "Valor"]).pivot(index=["Any"], columns=["Tipologia", "Variable"], values="Valor")
                    df_cat_n = df_cat.sort_index(axis=1, level=[0,1])
                    num_cols = df_cat_n.select_dtypes(include=['float64', 'int64']).columns
                    df_cat_n[num_cols] = df_cat_n[num_cols].round(0)
                    df_cat_n[num_cols] = df_cat_n[num_cols].astype(int)
                    num_cols = df_cat_n.select_dtypes(include=['float64', 'int']).columns
                    df_cat_n[num_cols] = df_cat_n[num_cols].applymap(lambda x: '{:,.0f}'.format(x).replace(',', '#').replace('.', ',').replace('#', '.'))
                    return(df_cat_n)
            st.markdown(table_geo_cat(2019, 2023).to_html(), unsafe_allow_html=True)
            st.markdown(filedownload(table_geo_cat(2019, 2022), f"Estudi_oferta_Catalunya.xlsx"), unsafe_allow_html=True)
############################################################  CATALUNYA: 2023 ################################################
    if selected_edition=="2023":
        index_names = ["Introducció","Característiques", "Superfície i preus", "Comparativa 2023-2022"]
        selected_index = st.sidebar.radio("**Contingut**", index_names)

        if selected_index=="Introducció":
            st.subheader("**INTRODUCCIÓ**")
            st.write("""<p style="margin-top: 10px"> 
            <p>
            Les dades exposades presenten els resultats de l’anàlisi del mercat residencial d’habitatges de nova construcció a Catalunya de l'any 2023.
            Es resumeixen les dades de l’oferta del mercat residencial d’obra nova, per tal de disposar d’informació actualitzada del sector i de la seva evolució, oferint-se aquestes dades en diferents nivells de 
            desagregació territorial (província, municipi, …). Aquest treball té una base censal, essent el fruit d’una recerca exhaustiva de les ofertes de les promocions d’habitatge d’obra nova mitjançant un treball de camp
            exhaustiu amb recerques on-line, telefòniques i algunes visites presencials. El cens parteix de la darrera actualització realitzada l’any precedent (2022). En els 135 municipis seleccionats per la seva significació en l’àmbit de l’habitatge 
            (33 municipis més que els municipis on es va dur a terme el treball de camp de l’edició de 2022, que van ser 102), s’ha inventariat l’oferta d’obra nova i llurs característiques fonamentals, tant quantitatives com qualitatives. 
            En l’execució del treball de camp no han estat incloses les promocions amb limitació d’informació disponible, bàsicament no han estat considerades com unitats vàlides per la mostra les promocions sense informació contrastada de preus 
            i superfícies. El resultat final de l’edició d’enguany inclou promocions a 116 municipis dels 135 referenciats com a punt de partida.
            </p>
            <p>
            L’estudi de 2023 inclou 116 municipis rellevants en l’àmbit de l’habitatge, distribuïts per tot el territori, en els quals s’han inventariat 1.123 promocions d’obra nova, amb un total de 10.296 habitatges a la venda. 
            Respecte el 2022, el nombre de promocions registradesha incrementat en 195 promocions i el nombre total d’habitatges a la venda ha passat de 8.181 a 10.296, es a dir, un 26% més.
            En relació a les bases mostrals de promocions i habitatges, les dades de 2023 inclouen 665 promocions de l’edició de 2022, es a dir, el 71,7% de les promocions de 2022, un any després continuen tenint algun habitatge en venda. 
            Pel que fa als habitatges, dels 8.181 censats l’any 2022, el 24,0% han estat venuts i, per tant, es mantenen en oferta 6.221 habitatges dels estudiats l’any passat. Per completar la mostra de 2023, 
            s’han incorporat 458 promocions noves que en el seu conjunt tenen una oferta de 4.075 habitatges.
            </p>
            <p>
            El municipi amb més presència d’oferta és el de Barcelona, amb un total de 224 promocions i 1.560 habitatges en venda. A continuació, els municipis amb més promocions són Sabadell amb 55 promocions i 663 habitatges, 
            Terrassa amb 51 promocions i 730 habitatges (és el segon municipi en ordre d’importància per número d’habitatges en oferta), Badalona amb 48 promocions i 315 habitatges i L’Hospitalet de Llobregat amb 46 promocions i 383 habitatges. 
            Per altra banda, s’han localitzat un total de 30 municipis amb una oferta inferior a 10 habitatges, corresponents a 1 o 2 promocions: en concret, 16 municipis a la província de Barcelona, 
            5 a la província de Girona, 3 a la província de Lleida i 6 a la província de Tarragona.        
            </p>
            """,
            unsafe_allow_html=True
        )
            left_col, right_col = st.columns((1, 1))
            with left_col:
                st.markdown("**Nombre de promocions per província a Catalunya**")
                @st.cache_data(show_spinner="**Carregant les dades... Esperi, siusplau**", max_entries=500)
                def map_prov_prom():
                    provprom_map = bbdd_estudi_prom_2023[["PROVINCIA"]].value_counts().reset_index()
                    provprom_map.columns = ["NAME_2", "PROMOCIONS"]
                    shapefile_prov = gpd.read_file(path + "Provincias.geojson")
                    shapefile_prov = shapefile_prov[shapefile_prov["NAME_1"]=="Cataluña"]
                    fig, ax = plt.subplots(1,1, figsize=(10,10))
                    divider = make_axes_locatable(ax)
                    tmp = shapefile_prov.copy()
                    tmp = pd.merge(tmp, provprom_map, how="left", on="NAME_2")
                    # cax = divider.append_axes("right", size="3%", pad=-1) #resize the colorbar
                    cmap = colors.LinearSegmentedColormap.from_list("mi_paleta", ["#DAE4E0","#008B6C"]) 
                    tmp.plot(column='PROMOCIONS', ax=ax, cmap=cmap, legend=False)
                    tmp.geometry.boundary.plot(color='black', ax=ax, linewidth=0.3) #Add some borders to the geometries
                    for i, row in tmp.iterrows():
                        x, y = row['geometry'].centroid.coords[0]
                        ax.annotate(f"""{row['NAME_2']}\n{row["PROMOCIONS"]}""", xy=(x, y), xytext=(3,3), textcoords="offset points", fontsize=10, color="black")
                                        # bbox=dict(facecolor='white', alpha=0.5)
                                        # arrowprops=dict(facecolor='black', arrowstyle="->")
                                        
                    ax.axis('off')
                    fig.patch.set_alpha(0)
                    return(fig)
                st.pyplot(map_prov_prom())
            with right_col:
                st.markdown("**Nombre d'habitatges en oferta per municipis a Catalunya**")
                @st.cache_data(show_spinner="**Carregant les dades... Esperi, siusplau**", max_entries=500)
                def map_mun_hab_oferta():
                    prommun_map = bbdd_estudi_prom_2023[["CODIMUN", "Municipi","HABIP"]].groupby(["CODIMUN", "Municipi"]).sum().reset_index()
                    prommun_map.columns = ["municipi", "Municipi_n", "Habitatges en oferta"]
                    prommun_map["municipi"] = prommun_map["municipi"].astype(int)

                    shapefile_mun = gpd.read_file(path + "shapefile_mun.geojson")
                    shapefile_mun["municipi"] = shapefile_mun["codiine"].astype(int)

                    tmp = pd.merge(shapefile_mun, prommun_map, how="left", on="municipi")
                    fig, ax = plt.subplots(1,1, figsize=(20,20))
                    divider = make_axes_locatable(ax)
                    cax = divider.append_axes("right", size="3%", pad=-1) #resize the colorbar
                    cmap = colors.LinearSegmentedColormap.from_list("mi_paleta", ["#AAC4BA","#008B6C"]) 

                    tmp.plot(column='Habitatges en oferta', ax=ax,cax=cax, cmap=cmap, legend=True)
                    tmp.geometry.boundary.plot(color='black', ax=ax, linewidth=0.3) #Add some borders to the geometries
                    ax.axis('off')
                    fig.patch.set_alpha(0)
                    return(fig)
                st.pyplot(map_mun_hab_oferta())
        if selected_index=="Característiques":
            left_col, right_col = st.columns((1, 1))
            with left_col:
                st.subheader("**CARACTERÍSTIQUES**")
                st.write("""
                <p>
                El prototip d’habitatge (mitjà) a Catalunya tindria les següents característiques: 2,7 dormitoris, 1,9 banys i/o lavabos, el 74,7% cuina americana i el 25,3% cuina estàndard, i amb 1,0 terrasses, balcons i/o patis.
                Segons el nombre d'habitacions: els tipus loft (40 habitatges) es caracteritzen per tenir un sol espai i majoritàriament amb cuina americana; els d’un sol dormitori (535 habitatges) majoritàriament tenen un sol bany (83,6%) 
                i cuina americana (93,3%); en els de dos dormitoris (3.100 habitatges) el 55,4% tenen més d’un bany, la cuina americana també és majoritària (86,3%), així com la disposició de terrasses, balcons i/o patis (75,0%); 
                en els de tres dormitoris (5.222 habitatges) la pràctica totalitat (97,7%) tenen més d’un bany, la cuina americana també és majoritària (70,7%) i el 83,0% disposen de terrasses, balcons i/o patis; 
                en els de quatre dormitoris (1.334 habitatges) pràcticament tots (el 99,9%) tenen més d’un bany, el 55,5% compten amb cuina americana, el 86,7% disposa de terrasses, balcons i/o patis i un 49,6% té safareig; 
                en els de cinc i més dormitoris (65 habitatges) tots tenen dos banys o més, la cuina americana també és majoritària (69,2%), el 96,9% disposen de terrasses, balcons i/o patis i un 52,3% disposen de safareig.
                Així, la principal tipologia en oferta seria la dels habitatges de 3 dormitoris i 2 banys (45,4%). Amb percentatges menors però significatius es contemplen els habitatges de 2 dormitoris i 2 banys (15,6%), 
                els de 2 dormitoris i 1 bany (13,4%) i els de 4 dormitoris i 2 banys (8,1%).
                </p>""",
                unsafe_allow_html=True
                )
            with right_col:
                def plot_caracteristiques():
                    table61_tipo = bbdd_estudi_hab_2023.groupby(['Total dormitoris', 'Banys i lavabos']).size().div(len(bbdd_estudi_hab_mod)).reset_index(name='Proporcions').sort_values(by="Proporcions", ascending=False)
                    table61_tipo["Proporcions"] = table61_tipo["Proporcions"]*100
                    table61_tipo["Tipologia"] = np.where(table61_tipo["Banys i lavabos"]==1, table61_tipo["Total dormitoris"].astype(str) + " dormitoris i " + table61_tipo["Banys i lavabos"].astype(str) + " bany", table61_tipo["Total dormitoris"].astype(str) + " dormitoris i " + table61_tipo["Banys i lavabos"].astype(str) + " banys")
                    fig = px.bar(table61_tipo.head(4), x="Proporcions", y="Tipologia", orientation='h', title="", 
                    labels={'x':"Proporcions sobre el total d'habitatges", 'y':"Tipologia"})
                    fig.layout.xaxis.title.text = "Proporcions sobre el total d'habitatges"
                    fig.layout.yaxis.title.text = "Tipologia"
                    fig.layout.title.text= "Principals tipologies dels habitatges en oferta (%)"
                    fig.update_traces(marker=dict(color="#66b9a7"))
                    return(fig)
                # st.write(plot_caracteristiques())
                st.plotly_chart(plot_caracteristiques(), use_container_width=True, responsive=True)


        if selected_index=="Superfície i preus":
            left_col, right_col = st.columns((1, 1))
            with left_col:
                st.subheader("SUPERFÍCIES I PREUS")
                st.write("""
                <p>
                En general, conforme augmenta la superfície, augmenta el nombre de dormitoris, situant-se la màxima recurrència en els habitatges de 3 dormitoris entre els 60 i els 90 m² (3.950 habitatges, 38,4% de l’oferta d’habitatges) 
                i en els de 2 dormitoris amb superfícies inferiors als 70 m² (2.379 habitatges, 23,1% de l’oferta d’habitatges). En els extrems es trobarien els 721 habitatges de menys de 50 m² bàsicament amb 1o 2 dormitoris i, 
                231 habitatges de més de 160 m² a l’entorn de 4 dormitoris. A la vista de les dades, s’expressa també una certa correlació entre les variables preu habitatge i nombre de dormitoris, 
                de tal manera que quants més dormitoris té en disposició l’habitatge, major és el seu preu de venda -en general-. 
                El 16,2% del conjunt d’habitatges en oferta de venda no supera els 210.000€ (l’any 2020 aquest percentatge era del 22,9% , l’any 2021 del 18,8% i l’any 2022 del 16,8% ), entre aquests habitatges es situen el 42,6% dels d’un dormitori.
                Seguint la lògica expressada, un major nombre de dormitoris, implica –en general- una major superfície, per tant a la relació entre la variable preu i nombre de dormitoris cal afegir-li la variable superfície. 
                Sempre tenint en compte la incidència d’altres variables (localització, qualitats, ...) que fan que aquesta relació no tingui un comportament lineal. Els dos pols de la relació superfície útil – preu, 
                serien el 53,5% dels habitatges de menys de 50 m² que es situen en preus inferiors a 210.000€ i el 64,5% d’habitatges de més de 160 m² que es situen en preus per sobre els 600.000€.
                </p>
                <p>      
                La mitjana de la superfície útil dels habitatges censats, és de 80,6 m² i la de preu de 365.798€ (4.492,7€/m² útil). Per sota de la mitjana de preu, a nivell general, es situen els habitatges d’un i de dos dormitoris. 
                Si l’anàlisi es fa a partir de la mitjana del preu/m\u00b2 útil, per sota la mitjana resten els habitatges de 3 i 4 dormitoris. En els habitatges unifamiliars s’obtenen mitjanes de superfície força més altes (145,4 m²), 
                així com de preu (540.465€), però el m² útil (3.741,5€) es situa per sota la mitjana general, evidenciant que el desplaçament a l’alça del preu no compensa el de la superfície. Els habitatges plurifamiliars estan més 
                propers a les mitjanes generals doncs aporten força més influència sobre aquestes, essent aquesta aportació de 77,2 m² de superfície i de 356.751€ de preu (4.531,6€/m² útil).   
                </p>         
                """,
                unsafe_allow_html=True
                )

            with right_col:
                st.write("""<p><b>Preu mitjà per tipologia d'habitatge</b></p>""", unsafe_allow_html=True)
                def indicadors_preu_mitjanes():
                    table76_tipo = bbdd_estudi_hab_mod_2023[["Total dormitoris", "TIPOG","Superfície útil", "Preu mitjà", "Preu m2 útil"]].set_index(["Total dormitoris", "TIPOG"]).groupby(["TIPOG", "Total dormitoris"]).apply(np.mean).reset_index()
                    table76_total = bbdd_estudi_hab_mod_2023[["Total dormitoris","Superfície útil", "Preu mitjà", "Preu m2 útil"]].set_index(["Total dormitoris"]).groupby(["Total dormitoris"]).apply(np.mean).reset_index()
                    table76_total["TIPOG"] = "Total habitatges"
                    table76 = pd.concat([table76_tipo, table76_total], axis=0)
                    table76 = pd.merge(table76, bbdd_estudi_hab_mod_2023[["TIPOG","Total dormitoris"]].groupby(["TIPOG","Total dormitoris"]).size().reset_index().rename(columns={0:"Total"}), how="left", on=["TIPOG","Total dormitoris"])
                    table76 = table76.rename(columns={"TIPOG":"Tipologia"})
                    fig = px.bar(table76, x="Preu mitjà", y="Total dormitoris", color="Tipologia", orientation='h', color_discrete_sequence=["#00D0A3","#AAC4BA","#008B6C"], barmode="group", title="", labels={'x':"Preu mitjà", 'y':"Tipologia d'habitatge"})
                    fig.layout.xaxis = dict(title="Preu mitjà", tickformat=",d")
                    fig.layout.yaxis.title.text = "Nombre d'habitacions"
                    fig.update_layout(font=dict(size=13), legend=dict(orientation='h', yanchor='bottom', y=1, xanchor='right', x=0.75))
                    return(fig)
                st.plotly_chart(indicadors_preu_mitjanes(), use_container_width=True, responsive=True)
            left, right = st.columns((1,1))
            with left:
                st.write("""<p><b>Preu per m\u00b2 útil per tipologia d'habitatge</b></p>""", unsafe_allow_html=True)
                def indicadors_preum2_mitjanes():
                    table76_tipo = bbdd_estudi_hab_mod_2023[["Total dormitoris", "TIPOG","Superfície útil", "Preu mitjà", "Preu m2 útil"]].set_index(["Total dormitoris", "TIPOG"]).groupby(["TIPOG", "Total dormitoris"]).apply(np.mean).reset_index()
                    table76_total = bbdd_estudi_hab_mod_2023[["Total dormitoris","Superfície útil", "Preu mitjà", "Preu m2 útil"]].set_index(["Total dormitoris"]).groupby(["Total dormitoris"]).apply(np.mean).reset_index()
                    table76_total["TIPOG"] = "Total habitatges"
                    table76 = pd.concat([table76_tipo, table76_total], axis=0)
                    table76 = pd.merge(table76, bbdd_estudi_hab_mod_2023[["TIPOG","Total dormitoris"]].groupby(["TIPOG","Total dormitoris"]).size().reset_index().rename(columns={0:"Total"}), how="left", on=["TIPOG","Total dormitoris"])
                    table76 = table76.rename(columns={"TIPOG":"Tipologia"})
                    fig = px.bar(table76, x="Preu m2 útil", y="Total dormitoris", color="Tipologia", orientation='h', color_discrete_sequence=["#00D0A3","#AAC4BA","#008B6C"], barmode="group", title="", labels={'x':"Preu m\u00b2 útil (mitjana)", 'y':"Tipologia d'habitatge"})
                    fig.layout.xaxis = dict(title="Preu per m\u00b2 útil", tickformat=",d")
                    fig.layout.yaxis.title.text = "Nombre d'habitacions"
                    fig.update_layout(font=dict(size=13), legend=dict(orientation='h', yanchor='bottom', y=1, xanchor='right', x=0.75))
                    return(fig)
                st.plotly_chart(indicadors_preum2_mitjanes(), use_container_width=True, responsive=True)
            with right:
                st.write("""<p><b>Superfície útil per tipologia d'habitatge</b></p>""", unsafe_allow_html=True)
                def indicadors_super_mitjanes():
                    table76_tipo = bbdd_estudi_hab_mod_2023[["Total dormitoris", "TIPOG","Superfície útil", "Preu mitjà", "Preu m2 útil"]].set_index(["Total dormitoris", "TIPOG"]).groupby(["TIPOG", "Total dormitoris"]).apply(np.mean).reset_index()
                    table76_total = bbdd_estudi_hab_mod_2023[["Total dormitoris","Superfície útil", "Preu mitjà", "Preu m2 útil"]].set_index(["Total dormitoris"]).groupby(["Total dormitoris"]).apply(np.mean).reset_index()
                    table76_total["TIPOG"] = "Total habitatges"
                    table76 = pd.concat([table76_tipo, table76_total], axis=0)
                    table76 = pd.merge(table76, bbdd_estudi_hab_mod_2023[["TIPOG","Total dormitoris"]].groupby(["TIPOG","Total dormitoris"]).size().reset_index().rename(columns={0:"Total"}), how="left", on=["TIPOG","Total dormitoris"])
                    table76 = table76.rename(columns={"TIPOG":"Tipologia"})
                    fig = px.bar(table76, x="Superfície útil", y="Total dormitoris", color="Tipologia", orientation='h', color_discrete_sequence=["#00D0A3","#AAC4BA","#008B6C"], barmode="group", title="", labels={'x':"Superfície útil", 'y':"Tipologia d'habitatge"})
                    fig.layout.xaxis.title.text = "Superfície útil"
                    fig.layout.yaxis.title.text = "Nombre d'habitacions"
                    fig.update_layout(font=dict(size=13), legend=dict(orientation='h', yanchor='bottom', y=1, xanchor='right', x=0.75))
                    return(fig)
                st.plotly_chart(indicadors_super_mitjanes(), use_container_width=True, responsive=True)

        if selected_index=="Comparativa 2023-2022":
            left_col, right_col = st.columns((1, 1))
            with left_col: 
                st.subheader("**COMPARATIVA 2023-2022**") 
                st.write("""
                <p>
                    L’any 2023 s’han registrat un total de 1.123 promocions, 195 més que les de 2022 (928 promocions). El nombre d'habitatges va augmentar de 8.181 al 2022 a 10.296 habitatges al 2023, que suposa un increment del 25,9%.
                    Cal esmentar que de les 928 promocions de 2022, 263 ja han estat totalment venudes al 2023 i, en el cas dels habitatges, el 24,0% han estat venuts.
                    Respecte de les quatre tipologies de promoció (unifamiliars aïllades o adossats i plurifamiliars en bloc obert o tancat), les variacions són molt atenuades respecte 2022, 
                    mantenint-se la seva distribució. Si aquest mateix anàlisi es fa per habitatges, les variacions són reduides i els habitatges plurifamiliars són majoria (95,1% en 2023, 95,9% en 2022). 
                </p>
                <p>
                    La superfície mitjana dels habitatges a la venda és de 80,6 m² (80,7 m² l’any 2022), amb una lleugera variació del -0,2%. Aquesta variació és irregular en els diferents tipus d’habitatges, 
                    assolint un descens màxim del -4,1% als habitatges tipus loft i un increment de l’1,9% als de 4 dormitoris. 
                </p>
                <p>
                    El preu mitjà de l’habitatge a la venda a Catalunya és de 365.798€, un 0,8% inferior al registrat en el cens de 2022. Aquest descens de preu es dona de manera més acusada als habitatges tipus loft (-5,0%) i de 2 dormitoris (-4,6%).
                    Contràriament, els habitatges de 5 i més dormitoris incrementen el seu preu en un 7,0% i el d’1 dormitori en un 5,1%. 
                </p>
                <p>
                    Pel que fa al preu per m² útil, en el conjunt dels municipis és de 4.492,7€, valor que suposa un preu inferior en gairebé un punt (0,9%) en referència a 2022. 
                    El comportament per tipologies es positiu en els habitatges de 5 i més dormitoris i d’1 dormitori, nul en els de 3 dormitoris i negatiu en els casos dels loft i de 2 i 4 dormitoris.
                </p>""",
                unsafe_allow_html=True
                )
            with right_col:
                st.markdown("")
                st.write("""<p><b>Variació anual (%) dels principals indicadors per tipologia d'habitatge</b></p>""", unsafe_allow_html=True)
                @st.cache_data(show_spinner="**Carregant les dades... Esperi, siusplau**", max_entries=500)
                def plot_var_CAT():
                    table117 = pd.read_excel(path + "Estudi_oferta_taules 2023.xlsx", sheet_name="table117", header=1).iloc[1:,]
                    table121 = pd.read_excel(path + "Estudi_oferta_taules 2023.xlsx", sheet_name="table121", header=1).iloc[1:,]
                    table125 = pd.read_excel(path + "Estudi_oferta_taules 2023.xlsx", sheet_name="table125", header=1).iloc[1:,]
                    table117 = table117[(table117["Província"].isna()) & (table117["Municipi"].isna())][["Variació % Preu m2 útil","Variació % Preu mitjà", "Variació % Superfície útil"]]
                    table121 = table121[(table121["Província"].isna()) & (table121["Municipi"].isna())][["Variació % Preu m2 útil","Variació % Preu mitjà", "Variació % Superfície útil"]]
                    table125 = table125[(table125["Província"].isna()) & (table125["Municipi"].isna())][["Variació % Preu m2 útil","Variació % Preu mitjà", "Variació % Superfície útil"]]
                    table_var = pd.concat([table117, table121, table125], axis=0)
                    table_var["Tipologia"] = ["Total habitatges", "Habitatges unifamiliars", "Habitatges plurifamiliars"]
                    table_var_melted = pd.melt(table_var, id_vars="Tipologia", var_name = "Variable")

                    fig = px.bar(table_var_melted, x="Tipologia", y="value", color="Variable", color_discrete_sequence=["#008B6C","#00D0A3","#AAC4BA"], barmode="group", title="", labels={'x':"Preu m\u00b2 útil (mitjana)", 'y':"Tipologia d'habitatge"})
                    fig.layout.xaxis.title.text = "Tipologia"
                    fig.layout.yaxis.title.text = "Variació anual (%)"
                    fig.update_layout(font=dict(size=13), legend=dict(orientation='h', yanchor='bottom', y=1, x=0))
                    return(fig)
                st.plotly_chart(plot_var_CAT(), use_container_width=True, responsive=True)
            def table_geo_cat(any_ini, any_fin):
                df_cat = df_final_cat[(df_final_cat["Any"]>=any_ini) & (df_final_cat["Any"]<=any_fin)].drop_duplicates(["Any", "Tipologia", "Variable", "Valor"]).pivot(index=["Any"], columns=["Tipologia", "Variable"], values="Valor")
                df_cat_n = df_cat.sort_index(axis=1, level=[0,1])
                num_cols = df_cat_n.select_dtypes(include=['float64', 'int64']).columns
                df_cat_n[num_cols] = df_cat_n[num_cols].round(0)
                df_cat_n[num_cols] = df_cat_n[num_cols].astype(int)
                num_cols = df_cat_n.select_dtypes(include=['float64', 'int']).columns
                df_cat_n[num_cols] = df_cat_n[num_cols].applymap(lambda x: '{:,.0f}'.format(x).replace(',', '#').replace('.', ',').replace('#', '.'))
                return(df_cat_n)
            st.markdown(table_geo_cat(2019, 2023).to_html(), unsafe_allow_html=True)
            st.markdown(filedownload(table_geo_cat(2019, 2022), f"Estudi_oferta_Catalunya.xlsx"), unsafe_allow_html=True)

############################################################  PROVÍNCIES I ÀMBITS TERRITORIALS ################################################

if selected == "Províncies i àmbits":
    def table_geo(geo, any_ini, any_fin, selected):
        if selected=="Àmbits territorials":
            df_prov_filtered = ambits_df[(ambits_df["GEO"]==geo) & (ambits_df["Any"]>=any_ini) & (ambits_df["Any"]<=any_fin)].pivot(index=["Any"], columns=["Tipologia", "Variable"], values="Valor")
            df_prov_n = df_prov_filtered.sort_index(axis=1, level=[0,1])
            num_cols = df_prov_n.select_dtypes(include=['float64', 'int64']).columns
            df_prov_n[num_cols] = df_prov_n[num_cols].round(0)
            df_prov_n[num_cols] = df_prov_n[num_cols].astype("float64")
            num_cols = df_prov_n.select_dtypes(include=['float64', 'int']).columns
            df_prov_n[num_cols] = df_prov_n[num_cols].applymap(lambda x: '{:,.0f}'.format(x).replace(',', '#').replace('.', ',').replace('#', '.'))
            return(df_prov_n)
        if selected=="Províncies" or selected=="Catalunya":
            df_prov_filtered = provincia_df[(provincia_df["GEO"]==geo) & (provincia_df["Any"]>=any_ini) & (provincia_df["Any"]<=any_fin)].pivot(index=["Any"], columns=["Tipologia", "Variable"], values="Valor")
            df_prov_n = df_prov_filtered.sort_index(axis=1, level=[0,1])
            num_cols = df_prov_n.select_dtypes(include=['float64', 'int64']).columns
            df_prov_n[num_cols] = df_prov_n[num_cols].round(0)
            df_prov_n[num_cols] = df_prov_n[num_cols].astype(int)
            num_cols = df_prov_n.select_dtypes(include=['float64', 'int']).columns
            df_prov_n[num_cols] = df_prov_n[num_cols].applymap(lambda x: '{:,.0f}'.format(x).replace(',', '#').replace('.', ',').replace('#', '.'))
            return(df_prov_n)
    
    st.sidebar.header("**PROVÍNCIES I ÀMBITS TERRITORIALS DE CATALUNYA**")
    edicio_any = ["2022","2023"]
    selected_edition = st.sidebar.radio("**Any**", edicio_any)

############################################################  PROVÍNCIES I ÀMBITS TERRITORIALS: 2022 ################################################

    if selected_edition=="2022":
        prov_names = ["Barcelona", "Girona", "Tarragona", "Lleida"]
        ambit_names = sorted([ambit_n for ambit_n in ambits_df["GEO"].unique().tolist() if ambit_n!="Catalunya"])
        selected_option = st.sidebar.radio("**Àrea geogràfica**", ["Províncies", "Àmbits territorials"])
        if selected_option=="Àmbits territorials":
            selected_geo = st.sidebar.selectbox('', ambit_names, index= ambit_names.index("Metropolità"))
            st.subheader(f"{selected_geo}")
            min_year, max_year = st.sidebar.slider("**Interval d'anys de la mostra**", value=[2019, 2022], min_value=2019, max_value=2022)
            st.markdown(table_geo(selected_geo, min_year, max_year, selected_option).to_html(), unsafe_allow_html=True)
            st.markdown(filedownload(table_geo(selected_geo, min_year, max_year, selected_option), f"Estudi_oferta_{selected_geo}.xlsx"), unsafe_allow_html=True)
        if selected_option=="Províncies":
            selected_geo = st.sidebar.selectbox('', prov_names, index= prov_names.index("Barcelona"))
            st.subheader(f"PROVÍNCIA DE {selected_geo.upper()}")
            if selected_geo=="Barcelona":
                st.write(f"""Els municipis analitzats a l’Estudi de l’Oferta d’Habitatge
                            de Nova Construcció de 2022 que pertanyen a
                            la província de Barcelona fan que aquesta se situï en primera
                            posició pel que fa a la mitjana de preu (389.716€)
                            i també quant al preu €/m\u00b2 de superfície útil (4.796€),
                            ambdós influenciats pel municipi de Barcelona en incidir
                            sobre les mitjanes de forma determinant, tant per la seva
                            aportació quantitativa com qualitativa. Addicionalment,
                            Barcelona se situa com la quarta província pel que fa a
                            la mitjana de superfície, de 79,6m\u00b2.
                            El nombre de promocions en oferta als municipis estudiats
                            a la província de Barcelona l’any 2022 era
                            de 730, amb 6.190 habitatges, xifra que representa el
                            78,7% del total de les promocions estudiades. El percentatge
                            d’habitatges que restaven per vendre és del
                            36,2% sobre un total de 17.121 habitatges existents
                            dins les promocions (en el moment d’elaborar aquest
                            estudi ja estaven venuts el 63,8% dels habitatges, majoritàriament
                            sobre plànol).
                            Pel que fa als habitatges unifamiliars, la mitjana de
                            superficie a la província se situa en 161,4m\u00b2, la mitjana
                            de preu de venda en 637.229€ i la de preu m\u00b2/ útil
                            en 3.813,6€. Pel que fa als habitatges plurifamiliars,
                            la superfície mitjana -en base als municipis estudiats
                            situats a la província- és de 77,3m\u00b2, amb una mitjana
                            de preu de venda de 382.726€, i un preu mitjà per m\u00b2
                            útil de 4.824€.""")
            if selected_geo=="Girona":
                st.write(f"""Els municipis analitzats a l’Estudi de l’Oferta d’Habitatge
                            de Nova Construcció de 2022 que pertanyen a
                            la província de Girona fan que aquesta se situï en tercera
                            posició en la mitjana de superfície (82,5m\u00b2), i en segona
                            posició respecte al preu mitjà (376.023€) i en el preu m\u00b2
                            de superfície útil (4.684€).
                            Pel que fa als habitatges plurifamiliars, la superfície
                            mitjana se situa en els 79,1m\u00b2, amb un preu mitjà
                            de 374.049€, i un preu per m\u00b2 de superfície útil
                            de 4.789€. Respecte dels habitatges unifamiliars,
                            aquestes mitjanes són de 131m\u00b2 de superfície, un
                            preu mitjà de 404.350€, i un preu per m\u00b2 de superfície
                            útil de 3.180€.
                            El nombre de promocions en oferta als municipis estudiats
                            a la província de Girona el 2022 era de 85 (un 9,2%
                            del total de les promocions estudiades a Catalunya, i 982
                            habitatges en venda.
                            El percentatge d’habitatges que restaven per vendre és
                            del 52,1% sobre un total de 1.884 habitatges existents
                            a les promocions de la província.""")
            if selected_geo=="Tarragona":
                st.write(f"""Els municipis analitzats a l’Estudi de l’Oferta d’Habitatge
                            de Nova Construcció de 2022 que pertanyen a la
                            província de Tarragona fan que aquesta se situï en segona
                            posició pel que fa a superfície mitjana (85,3m\u00b2), i
                            en tercera posició tant pel que fa a les mitjanes de preu
                            (244.164€) i de preu per m\u00b2 de superfície útil (2.958€).
                            Per tipologies d’habitatges, en els habitatges unifamiliars
                            les mitjanes registrades són: 167,2m\u00b2 de superfície,
                            amb un preu mitjà de 370.785€, i un preu per m\u00b2 de superfície
                            útil de 2.377€. Pel que fa als habitatges plurifamiliars,
                            la superfície mitjana se situa en els 73,6m\u00b2, amb
                            un preu mitjà de 226.195€, i un preu per m\u00b2 útil de 3.040€.
                            El nombre de promocions en oferta als municipis estudiats
                            a la província de Tarragona el 2022 era de 81, xifra
                            que representa un 8,7% del total de les promocions
                            estudiades a Catalunya (928 promocions). El nombre
                            d’habitatges que resten per vendre és de 692 unitats, un
                            33,2% sobre un total de 2.084 habitatges existents en les
                            promocions de la província.""")
            if selected_geo=="Lleida":
                st.write(f"""Els municipis analitzats a l’Estudi de l’Oferta d’Habitatge
                            de Nova Construcció de 2022 que pertanyen
                            a la província de Lleida obtenen la mitjana més alta de
                            superfície (86,5m\u00b2), i se situen en quarta posició pel que
                            fa a preu del m\u00b2 de superfície útil (2.351€).
                            Pel que fa habitatges plurifamiliars, la superfície mitja
                            provincial és de 83,8m\u00b2 i un preu mitjà per m\u00b2 útil de
                            2.292€. En el cas dels habitatges unifamiliars,
                            aquestes quantitats són de 131,7m\u00b2 de superfície mitjana
                            i de 3.327€ la mitjana del m\u00b2 de superfície útil.
                            El nombre de promocions en oferta als municipis estudiats
                            a la província de Lleida el 2022 era de 32 (amb 317
                            habitatges en venda), dada que representa un 3,4% del
                            total de les promocions estudiades (928 promocions). El
                            percentatge d’habitatges que restaven per vendre és del
                            44,8% sobre un total de 707 habitatges existents a les
                            promocions a la província.""")
            min_year, max_year = st.sidebar.slider("**Interval d'anys de la mostra**", value=[2019, 2022], min_value=2019, max_value=2022)
            st.markdown(table_geo(selected_geo, min_year, max_year, selected_option).to_html(), unsafe_allow_html=True)
            st.markdown(filedownload(table_geo(selected_geo, min_year, max_year, selected_option), f"Estudi_oferta_{selected_geo}.xlsx"), unsafe_allow_html=True)
            def tipog_donut(prov):
                donut_tipog = bbdd_estudi_hab[bbdd_estudi_hab["PROVINCIA"]==prov][["PROVINCIA", "TIPO"]].value_counts(normalize=True).reset_index()
                donut_tipog.columns = ["PROVINCIA", "TIPO", "Habitatges en oferta"]
                fig = go.Figure()
                fig.add_trace(go.Pie(
                    labels=donut_tipog["TIPO"],
                    values=donut_tipog["Habitatges en oferta"],
                    hole=0.5, 
                    showlegend=True, 
                    marker=dict(
                        colors=["#008B6C", "#00D0A3",  "#66b9a7", "#DAE4E0"], 
                        line=dict(color='#FFFFFF', width=1) 
                    ),
                    textposition='outside',
                    textinfo='percent+label' 
                ))
                fig.update_layout(
                    title=f'Habitatges en oferta per tipologia',
                    font=dict(size=12),
                    legend=dict(
                        x=0.85,  # Set legend position
                        y=0.85
                    )
                )
                return(fig)
            def num_dorms_prov(prov):
                table33_prov =  pd.crosstab(bbdd_estudi_hab_mod["PROVINCIA"], bbdd_estudi_hab_mod["Total dormitoris"]).reset_index().rename(columns={"PROVINCIA":"Província"})
                table33_prov = table33_prov[table33_prov["Província"]==prov].drop("Província", axis=1).T.reset_index()
                table33_prov.columns = ["Total dormitoris", "Habitatges en oferta"]

                fig = go.Figure(go.Bar(x=table33_prov["Total dormitoris"], y=table33_prov["Habitatges en oferta"], marker_color='#66b9a7'))
                fig.layout.yaxis = dict(title="Habitages en oferta", tickformat=",d")
                fig.update_layout(
                    title=f"Habitatges en oferta segons nombre d'habitacions",
                    xaxis_title="Nombre d'habitacions",
                )
                return(fig)
            def tipo_obra_prov(prov):
                table38hab_prov = bbdd_estudi_hab[["PROVINCIA", "TIPH"]].value_counts().reset_index().sort_values(["PROVINCIA", "TIPH"])
                table38hab_prov.columns = ["PROVINCIA", "TIPOLOGIA", "Habitatges"]
                table38hab_prov = table38hab_prov.pivot_table(index="PROVINCIA", columns="TIPOLOGIA", values="Habitatges").reset_index().rename(columns={"PROVINCIA":"Província"})
                table38hab_prov = table38hab_prov[table38hab_prov["Província"]==prov].drop("Província", axis=1).T.reset_index()
                table38hab_prov.columns = ["Tipus", "Habitatges en oferta"]
                fig = go.Figure()
                fig.add_trace(go.Pie(
                    labels=table38hab_prov["Tipus"],
                    values=table38hab_prov["Habitatges en oferta"],
                    hole=0.5, 
                    showlegend=True, 
                    marker=dict(
                        colors=["#008B6C",  "#00D0A3"], 
                        line=dict(color='#FFFFFF', width=1) 
                    ),
                    textposition='outside',
                    textinfo='percent+label' 
                ))
                fig.update_layout(
                    title=f'Habitatges en oferta per tipus (obra nova o rehabilitació)',
                    font=dict(size=12),
                    legend=dict(
                        x=0.7,  # Set legend position
                        y=0.85
                    )
                )
                return(fig)
            def metric_estat(prov):
                table11_prov = bbdd_estudi_prom[["PROVINCIA", "HABIP"]].groupby("PROVINCIA").sum().reset_index()
                hab_oferta = table11_prov[table11_prov["PROVINCIA"]==prov].iloc[0,1]
                table17_hab_prov = bbdd_estudi_hab[["PROVINCIA", "ESTO"]].value_counts().reset_index().sort_values(["PROVINCIA", "ESTO"])
                table17_hab_prov.columns = ["PROVINCIA","ESTAT", "PROMOCIONS"]
                table17_hab_prov = table17_hab_prov.pivot_table(index="PROVINCIA", columns="ESTAT", values="PROMOCIONS").reset_index()
                table17_hab_prov = table17_hab_prov[["PROVINCIA","Claus en mà"]].rename(columns={"PROVINCIA": "Província","Claus en mà":"Acabats sobre habitatges en oferta"})
                acabats_oferta = table17_hab_prov[table17_hab_prov["Província"]==prov].iloc[0,1]
                return([hab_oferta, acabats_oferta])
            def metric_rehab(prov):
                table38hab_prov = bbdd_estudi_hab[["PROVINCIA", "TIPH"]].value_counts().reset_index().sort_values(["PROVINCIA", "TIPH"])
                table38hab_prov.columns = ["PROVINCIA", "TIPOLOGIA", "Habitatges"]
                table38hab_prov = table38hab_prov.pivot_table(index="PROVINCIA", columns="TIPOLOGIA", values="Habitatges").reset_index().rename(columns={"PROVINCIA":"Província"})
                table38hab_prov = table38hab_prov[table38hab_prov["Província"]==prov].drop("Província", axis=1).T.reset_index()
                table38hab_prov.columns = ["Tipus", "Habitatges en oferta"]
                return([table38hab_prov.iloc[0,1], table38hab_prov.iloc[1,1]])
            def qualitats_prov(prov):
                table62_hab = bbdd_estudi_hab[bbdd_estudi_hab["PROVINCIA"]==prov][["Aire condicionat","Bomba de calor","Aerotèrmia","Calefacció","Preinstal·lació d'A.C./B. Calor/Calefacció",'Parquet','Armaris encastats','Placa de cocció amb gas','Placa de cocció vitroceràmica',"Placa d'inducció",'Plaques solars']].sum(axis=0)
                table62_hab = pd.DataFrame({"Equipaments":table62_hab.index, "Total":table62_hab.values})
                table62_hab = table62_hab.set_index("Equipaments").apply(lambda row: (row / bbdd_estudi_hab.shape[0])*100)
                table62_hab = table62_hab.sort_values("Total", ascending=True)
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=table62_hab["Total"],  # Use values as x-axis data
                    y=table62_hab.index,  # Use categories as y-axis data
                    orientation="h",  # Set orientation to horizontal
                    marker=dict(color="#66b9a7"),  # Set bar color
                ))
                fig.update_layout(
                    title="Qualitats d'habitatges en oferta",
                    xaxis_title="% d'habitatges en oferta",
                    yaxis_title="Qualitats",
                )
                return(fig)
            def equipaments_prov(prov):
                table67_hab = bbdd_estudi_hab[bbdd_estudi_hab["PROVINCIA"]==prov][["Zona enjardinada", "Parc infantil", "Piscina comunitària", "Traster", "Ascensor", "Equipament Esportiu", "Sala de jocs", "Sauna", "Altres", "Cap dels anteriors"]].sum(axis=0)
                table67_hab = pd.DataFrame({"Equipaments":table67_hab.index, "Total":table67_hab.values})
                table67_hab = table67_hab.set_index("Equipaments").apply(lambda row: row.mul(100) / bbdd_estudi_hab.shape[0])
                table67_hab = table67_hab.sort_values("Total", ascending=True)
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=table67_hab["Total"],  # Use values as x-axis data
                    y=table67_hab.index,  # Use categories as y-axis data
                    orientation="h",  # Set orientation to horizontal
                    marker=dict(color="#66b9a7"),  # Set bar color
                ))
                fig.update_layout(
                    title="Equipaments d'habitatges en oferta",
                    xaxis_title="% d'habitatges en oferta",
                    yaxis_title="Equipaments",
                )
                return(fig)
            
            left_col, right_col = st.columns((1,1))
            with left_col:
                st.plotly_chart(tipog_donut(selected_geo), use_container_width=True, responsive=True)
            with right_col:
                st.plotly_chart(num_dorms_prov(selected_geo), use_container_width=True, responsive=True)
            left_col, right_col = st.columns((1,1))
            with left_col:
                st.plotly_chart(qualitats_prov(selected_geo), use_container_width=True, responsive=True)
            with right_col:
                st.plotly_chart(equipaments_prov(selected_geo), use_container_width=True, responsive=True)
            left_col, right_col = st.columns((2, 1))
            with left_col:
                def cons_acabats(prov):
                    fig = go.Figure()
                    fig.add_trace(go.Pie(
                        labels=["Habitatges en construcció", "Habitatges acabats"],
                        values=[metric_estat(prov)[0] - metric_estat(prov)[1], metric_estat(prov)[1]],
                        hole=0.5, 
                        showlegend=True, 
                        marker=dict(
                            colors=["#008B6C",  "#00D0A3"], 
                            line=dict(color='#FFFFFF', width=1) 
                        ),
                        textposition='outside',
                        textinfo='percent+label' 
                    ))
                    fig.update_layout(
                        title=f'Habitatges en construcció i acabats',
                        font=dict(size=12),
                        legend=dict(
                            x=0.7,  # Set legend position
                            y=1.1
                        )
                    )
                    return(fig)
                st.plotly_chart(cons_acabats(selected_geo), use_container_width=True, responsive=True)
            with right_col:
                st.markdown("")
                st.markdown("")
                st.metric("**Habitatges en oferta**", format(int(metric_estat(selected_geo)[0]), ",d"))
                st.metric("**Habitatges en construcció**", format(int(metric_estat(selected_geo)[0] - metric_estat(selected_geo)[1]), ",d"))
                st.metric("**Habitatges acabats**", format(int(metric_estat(selected_geo)[1]), ",d"))
            left_col, right_col = st.columns((2, 1))
            with left_col:
                st.plotly_chart(tipo_obra_prov(selected_geo), use_container_width=True, responsive=True)
            with right_col:
                st.markdown("")
                st.markdown("")
                st.metric("**Habitatges de nova construcció**", format(int(metric_rehab(selected_geo)[0]), ",d"))
                st.metric("**Habitatges de rehabilitació integral**", format(int(metric_rehab(selected_geo)[1]), ",d"))

############################################################  PROVÍNCIES I ÀMBITS TERRITORIALS: 2023 ################################################

    if selected_edition=="2023":
        prov_names = ["Barcelona", "Girona", "Tarragona", "Lleida"]
        ambit_names = sorted([ambit_n for ambit_n in ambits_df["GEO"].unique().tolist() if ambit_n!="Catalunya"])
        selected_option = st.sidebar.radio("**Àrea geogràfica**", ["Províncies", "Àmbits territorials"])
        if selected_option=="Àmbits territorials":
            selected_geo = st.sidebar.selectbox('', ambit_names, index= ambit_names.index("Metropolità"))
            st.subheader(f"{selected_geo.upper()}")
            min_year, max_year = st.sidebar.slider("**Interval d'anys de la mostra**", value=[2019, 2023], min_value=2019, max_value=2023)
            st.markdown(table_geo(selected_geo, min_year, max_year, selected_option).to_html(), unsafe_allow_html=True)
            st.markdown(filedownload(table_geo(selected_geo, min_year, max_year, selected_option), f"Estudi_oferta_{selected_geo}.xlsx"), unsafe_allow_html=True)
        if selected_option=="Províncies":
            selected_geo = st.sidebar.selectbox('', prov_names, index= prov_names.index("Barcelona"))
            st.subheader(f"PROVÍNCIA DE {selected_geo.upper()}")
            if selected_geo=="Barcelona":
                st.write(f"""Els municipis analitzats a l’Estudi de l’Oferta d’Habitatge
                            de Nova Construcció a Catalunya 2023 que pertanyen a
                            la província de Barcelona fan que aquesta se situï en primera
                            posició pel que fa a la mitjana de preu (385.036€)
                            i també quant al preu €/m\u00b2 de superfície útil (4.757€),
                            ambdós influenciats pel municipi de Barcelona en incidir
                            sobre les mitjanes de forma determinant, tant per la seva
                            aportació quantitativa com qualitativa. Addicionalment,
                            Barcelona se situa com la quarta província pel que fa a
                            la mitjana de superfície, de 79,6m\u00b2.
                            El número de promocions en oferta als municipis estudiats
                            a la província de Barcelona l’any 2023 era
                            de 894, amb 8.012 habitatges, xifra que representa el
                            79,6% del total de les promocions estudiades. El percentatge
                            d’habitatges que restaven per vendre és del
                            38,7% sobre un total de 20.725 habitatges existents
                            dins les promocions (en el moment d’elaborar aquest
                            estudi ja estaven venuts el 61,3% dels habitatges, majoritàriament
                            sobre plànol).
                            Pel que fa als habitatges unifamiliars, la mitjana de
                            superficie a la província se situa en 149,0 m\u00b2, la mitjana
                            de preu de venda en 593.401€ i la de preu m\u00b2 útil
                            en 3.942,8€. Pel que fa als habitatges plurifamiliars,
                            la superfície mitjana és de 76,8 m\u00b2, amb una mitjana
                            de preu de venda de 376.425€, i un preu mitjà per m\u00b2
                            útil de 4.790,2€.""")
            if selected_geo=="Girona":
                st.write(f"""Els municipis analitzats a l’Estudi de l'Oferta d'Habitatge de 2023 que pertanyen a
                            la província de Girona fan que aquesta se situï en tercera
                            posició en la mitjana de superfície (82,9 m\u00b2), i en segona
                            posició respecte al preu mitjà (349.647€) i el preu m\u00b2
                            de superfície útil (4.244,9€).
                            Pel que fa als habitatges plurifamiliars, la superfície
                            mitjana se situa en els 79,6 m\u00b2, amb un preu mitjà
                            de 343.984€, i un preu per m\u00b2 de superfície útil
                            de 4.295€. Respecte dels habitatges unifamiliars,
                            aquestes mitjanes són de 140,1 m\u00b2 de superfície, un
                            preu mitjà de 446.945€, i un preu per m\u00b2 de superfície
                            útil de 3.392€.
                            El nombre de promocions en oferta als municipis estudiats
                            a la província de Girona al 2023 era de 109 (un 9,7%
                            del total de les promocions estudiades a Catalunya), que contenen 1200
                            habitatges en venda.
                            El percentatge d’habitatges que restaven per vendre és
                            del 51,3% sobre un total de 2.338 habitatges existents
                            a les promocions de la província.""")
            if selected_geo=="Tarragona":
                st.write(f"""Els municipis analitzats a l’Estudi de l'Oferta d'Habitatge de 2023 que pertanyen a la
                            província de Tarragona fan que aquesta se situï en segona
                            posició pel que fa a superfície mitjana (83,5m\u00b2), i
                            en tercera posició tant pel que fa a les mitjanes de preu
                            (254.667€) i de preu per m\u00b2 de superfície útil (3.029€).
                            Per tipologies d’habitatges, en els habitatges unifamiliars
                            les mitjanes registrades són: 140,5m\u00b2 de superfície,
                            amb un preu mitjà de 441.762, i un preu per m\u00b2 de superfície
                            útil de 3.354€. Pel que fa als habitatges plurifamiliars,
                            la superfície mitjana se situa en els 74,7\u00b2, amb
                            un preu mitjà de 225.741€, i un preu per m\u00b2 útil de 2.979€.
                            El nombre de promocions en oferta als municipis estudiats
                            a la província de Tarragona al 2023 era de 84, xifra
                            que representa un 7,4% del total de les promocions
                            estudiades a Catalunya. El percentatge d’habitatges que restaven per vendre és
                            del 32,3% sobre un total de 2.175 habitatges existents
                            a les promocions de la província.""")
            if selected_geo=="Lleida":
                st.write(f"""Els municipis analitzats a l’Estudi de l'Oferta d'Habitatge de 2023 que pertanyen
                            a la província de Lleida obtenen la mitjana més alta de
                            superfície (86,6 m\u00b2), i se situen en quarta posició pel que
                            fa a preu del m\u00b2 de superfície útil (2.428€).
                            Pel que fa els habitatges plurifamiliars, la superfície mitjana
                            provincial és de 82,7 m\u00b2 i un preu mitjà per m\u00b2 útil de
                            2.332€. En el cas dels habitatges unifamiliars,
                            aquestes quantitats són de 134,5 m\u00b2 de superfície mitjana
                            i de 3.586 la mitjana del preu m\u00b2 de superfície útil.
                            El nombre de promocions en oferta als municipis estudiats
                            a la província de Lleida al 2023 era de 36 (amb 382
                            habitatges en venda), dada que representa un 3,2% del
                            total de les promocions estudiades. El
                            percentatge d’habitatges que restaven per vendre és del
                            41,9% sobre un total de 911 habitatges existents a les
                            promocions a la província.""")
            min_year, max_year = st.sidebar.slider("**Interval d'anys de la mostra**", value=[2019, 2023], min_value=2019, max_value=2023)
            st.markdown(table_geo(selected_geo, min_year, max_year, selected_option).to_html(), unsafe_allow_html=True)
            st.markdown(filedownload(table_geo(selected_geo, min_year, max_year, selected_option), f"Estudi_oferta_{selected_geo}.xlsx"), unsafe_allow_html=True)
            def tipog_donut(prov):
                donut_tipog = bbdd_estudi_hab_2023[bbdd_estudi_hab_2023["PROVINCIA"]==prov][["PROVINCIA", "TIPO"]].value_counts(normalize=True).reset_index()
                donut_tipog.columns = ["PROVINCIA", "TIPO", "Habitatges en oferta"]
                fig = go.Figure()
                fig.add_trace(go.Pie(
                    labels=donut_tipog["TIPO"],
                    values=donut_tipog["Habitatges en oferta"],
                    hole=0.5, 
                    showlegend=True, 
                    marker=dict(
                        colors=["#008B6C", "#00D0A3",  "#AAC4BA", "#DAE4E0"], 
                        line=dict(color='#FFFFFF', width=1) 
                    ),
                    textposition='outside',
                    textinfo='percent+label' 
                ))
                fig.update_layout(
                    title=f'Habitatges en oferta per tipologia',
                    font=dict(size=12),
                    legend=dict(
                        x=0.85,  # Set legend position
                        y=0.85
                    )
                )
                return(fig)
            def num_dorms_prov(prov):
                table33_prov =  pd.crosstab(bbdd_estudi_hab_mod_2023["PROVINCIA"], bbdd_estudi_hab_mod_2023["Total dormitoris"]).reset_index().rename(columns={"PROVINCIA":"Província"})
                table33_prov = table33_prov[table33_prov["Província"]==prov].drop("Província", axis=1).T.reset_index()
                table33_prov.columns = ["Total dormitoris", "Habitatges en oferta"]

                fig = go.Figure(go.Bar(x=table33_prov["Total dormitoris"], y=table33_prov["Habitatges en oferta"], marker_color='#66b9a7'))
                fig.layout.yaxis = dict(title="Habitages en oferta", tickformat=",d")
                fig.update_layout(
                    title=f"Habitatges en oferta segons nombre d'habitacions",
                    xaxis_title="Nombre d'habitacions",
                )
                return(fig)
            def tipo_obra_prov(prov):
                table38hab_prov = bbdd_estudi_hab_2023[["PROVINCIA", "TIPH"]].value_counts().reset_index().sort_values(["PROVINCIA", "TIPH"])
                table38hab_prov.columns = ["PROVINCIA", "TIPOLOGIA", "Habitatges"]
                table38hab_prov = table38hab_prov.pivot_table(index="PROVINCIA", columns="TIPOLOGIA", values="Habitatges").reset_index().rename(columns={"PROVINCIA":"Província"})
                table38hab_prov = table38hab_prov[table38hab_prov["Província"]==prov].drop("Província", axis=1).T.reset_index()
                table38hab_prov.columns = ["Tipus", "Habitatges en oferta"]
                fig = go.Figure()
                fig.add_trace(go.Pie(
                    labels=table38hab_prov["Tipus"],
                    values=table38hab_prov["Habitatges en oferta"],
                    hole=0.5, 
                    showlegend=True, 
                    marker=dict(
                        colors=["#008B6C",  "#00D0A3"], 
                        line=dict(color='#FFFFFF', width=1) 
                    ),
                    textposition='outside',
                    textinfo='percent+label' 
                ))
                fig.update_layout(
                    title=f'Habitatges en oferta per tipus (obra nova o rehabilitació)',
                    font=dict(size=12),
                    legend=dict(
                        x=0.7,  # Set legend position
                        y=0.85
                    )
                )
                return(fig)
            def metric_estat(prov):
                table11_prov = bbdd_estudi_prom_2023[["PROVINCIA", "HABIP"]].groupby("PROVINCIA").sum().reset_index()
                hab_oferta = table11_prov[table11_prov["PROVINCIA"]==prov].iloc[0,1]
                table17_hab_prov = bbdd_estudi_hab_2023[["PROVINCIA", "ESTO"]].value_counts().reset_index().sort_values(["PROVINCIA", "ESTO"])
                table17_hab_prov.columns = ["PROVINCIA","ESTAT", "PROMOCIONS"]
                table17_hab_prov = table17_hab_prov.pivot_table(index="PROVINCIA", columns="ESTAT", values="PROMOCIONS").reset_index()
                table17_hab_prov = table17_hab_prov[["PROVINCIA","Claus en mà"]].rename(columns={"PROVINCIA": "Província","Claus en mà":"Acabats sobre habitatges en oferta"})
                acabats_oferta = table17_hab_prov[table17_hab_prov["Província"]==prov].iloc[0,1]
                return([hab_oferta, acabats_oferta])
            def metric_rehab(prov):
                table38hab_prov = bbdd_estudi_hab_2023[["PROVINCIA", "TIPH"]].value_counts().reset_index().sort_values(["PROVINCIA", "TIPH"])
                table38hab_prov.columns = ["PROVINCIA", "TIPOLOGIA", "Habitatges"]
                table38hab_prov = table38hab_prov.pivot_table(index="PROVINCIA", columns="TIPOLOGIA", values="Habitatges").reset_index().rename(columns={"PROVINCIA":"Província"})
                table38hab_prov = table38hab_prov[table38hab_prov["Província"]==prov].drop("Província", axis=1).T.reset_index()
                table38hab_prov.columns = ["Tipus", "Habitatges en oferta"]
                return([table38hab_prov.iloc[0,1], table38hab_prov.iloc[1,1]])
            left_col, right_col = st.columns((1,1))
            with left_col:
                st.plotly_chart(tipog_donut(selected_geo), use_container_width=True, responsive=True)
            with right_col:
                st.plotly_chart(num_dorms_prov(selected_geo), use_container_width=True, responsive=True)
            left_col, right_col = st.columns((2, 1))
            with left_col:
                def cons_acabats(prov):
                    fig = go.Figure()
                    fig.add_trace(go.Pie(
                        labels=["Habitatges en construcció", "Habitatges acabats"],
                        values=[metric_estat(prov)[0] - metric_estat(prov)[1], metric_estat(prov)[1]],
                        hole=0.5, 
                        showlegend=True, 
                        marker=dict(
                            colors=["#008B6C",  "#00D0A3"], 
                            line=dict(color='#FFFFFF', width=1) 
                        ),
                        textposition='outside',
                        textinfo='percent+label' 
                    ))
                    fig.update_layout(
                        title=f'Habitatges en construcció i acabats',
                        font=dict(size=12),
                        legend=dict(
                            x=0.7,  # Set legend position
                            y=1.1
                        )
                    )
                    return(fig)
                st.plotly_chart(cons_acabats(selected_geo), use_container_width=True, responsive=True)
            with right_col:
                st.markdown("")
                st.markdown("")
                st.metric("**Habitatges en oferta**", format(int(metric_estat(selected_geo)[0]), ",d"))
                st.metric("**Habitatges en construcció**", format(int(metric_estat(selected_geo)[0] - metric_estat(selected_geo)[1]), ",d"))
                st.metric("**Habitatges acabats**", format(int(metric_estat(selected_geo)[1]), ",d"))
            left_col, right_col = st.columns((2, 1))
            with left_col:
                st.plotly_chart(tipo_obra_prov(selected_geo), use_container_width=True, responsive=True)
            with right_col:
                st.markdown("")
                st.markdown("")
                st.metric("**Habitatges de nova construcció**", format(int(metric_rehab(selected_geo)[0]), ",d"))
                st.metric("**Habitatges de rehabilitació integral**", format(int(metric_rehab(selected_geo)[1]), ",d"))
############################################################  MUNICIPIS DE CATALUNYA ################################################
if selected == "Municipis":
    st.sidebar.header("**MUNICIPIS DE CATALUNYA**")
    edicio_any = ["2022","2023"]
    selected_edition = st.sidebar.radio("**Any**", edicio_any)

############################################################  MUNICIPIS: 2022 ################################################
    if selected_edition=="2022":
        mun_names = sorted([name for name in df_vf[(df_vf["Any"]==2022) & (~df_vf["Valor"].isna())]["GEO"].unique() if name != "Catalunya"])
        selected_mun = st.sidebar.selectbox('**Municipi seleccionat:**', mun_names, index= mun_names.index("Barcelona"))
        st.subheader(f"MUNICIPI DE {selected_mun.upper().split(',')[0].strip()}")
        def data_text(selected_mun):
            table80_mun = bbdd_estudi_hab_mod[bbdd_estudi_hab_mod["Municipi"]==selected_mun][["Municipi", "TIPOG", "Superfície útil", "Preu mitjà", "Preu m2 útil"]].groupby(["Municipi"]).agg({"Municipi":['count'], "Superfície útil": [np.mean], "Preu mitjà": [np.mean], "Preu m2 útil": [np.mean]}).reset_index()
            table25_mun = bbdd_estudi_hab[bbdd_estudi_hab_mod["Municipi"]==selected_mun][["Municipi", "TIPOG"]].value_counts(normalize=True).reset_index().rename(columns={0:"Proporció"})
            table61_hab = bbdd_estudi_hab[bbdd_estudi_hab_mod["Municipi"]==selected_mun].groupby(['Total dormitoris']).size().reset_index(name='Proporcions').sort_values(by="Proporcions", ascending=False)
            table61_lav = bbdd_estudi_hab[bbdd_estudi_hab_mod["Municipi"]==selected_mun].groupby(['Banys i lavabos']).size().reset_index(name='Proporcions').sort_values(by="Proporcions", ascending=False)

            try:
                proporcio_tipo = round(table25_mun[table25_mun["TIPOG"]=="Habitatges plurifamiliars"]["Proporció"].values[0]*100,2)
            except IndexError:
                proporcio_tipo = 0

            return([round(table80_mun["Preu mitjà"].values[0][0],2), round(table80_mun["Superfície útil"].values[0][0],2), 
                    round(table80_mun["Preu m2 útil"].values[0][0],2), proporcio_tipo, 
                    table61_hab["Total dormitoris"].values[0], table61_lav["Banys i lavabos"].values[0]])
        st.markdown(f"""Els resultats de l'Estudi d'Oferta de Nova Construcció del 2022 pel municipi de {selected_mun.split(',')[0].strip()} mostren que el preu mitjà dels habitatges en venda es troba 
        en {data_text(selected_mun)[0]:,.1f} € amb una superfície mitjana útil de {data_text(selected_mun)[1]:,.1f} m\u00b2. Per tant, el preu per m\u00b2 útil es troba en {data_text(selected_mun)[2]:,.1f} € de mitjana. Per tipologies, els habitatges plurifamiliars
        representen el {data_text(selected_mun)[3]:,.1f}% sobre el total d'habitatges, la resta corresponen a habitatges unifamiliars. L'habitatge modal o més freqüent de nova construcció té {data_text(selected_mun)[4]} habitacions i {data_text(selected_mun)[5]} banys o lavabos.""")

        def plotmun_streamlit(data, selected_mun, kpi):
            df = data[(data['Municipi']==selected_mun)]
            fig = px.histogram(df, x=kpi, title= "", labels={'x':kpi, 'y':'Freqüència'})
            fig.data[0].marker.color = "#66b9a7"
            fig.layout.xaxis.title.text = kpi
            fig.layout.yaxis.title.text = 'Freqüència'
            mean_val = df[kpi].mean()
            fig.layout.shapes = [dict(type='line', x0=mean_val, y0=0, x1=mean_val, y1=1, yref='paper', xref='x', 
                                    line=dict(color="black", width=2, dash='dot'))]
            return(fig)

        left_col, right_col = st.columns((1, 1))
        with left_col:
            st.markdown(f"""**Distribució de preus per m\u00b2 útil**""")
            st.plotly_chart(plotmun_streamlit(bbdd_estudi_hab_mod, selected_mun,"Preu m2 útil"), use_container_width=True, responsive=True)
        with right_col:
            st.markdown(f"""**Distribució de superfície útil**""")
            st.plotly_chart(plotmun_streamlit(bbdd_estudi_hab_mod, selected_mun, "Superfície útil"), use_container_width=True, responsive=True)

        st.markdown(f"""
        **Tipologia d'habitatges de les promocions**
        """)
        def count_plot_mun(data, selected_mun):
            df = data[data['Municipi']==selected_mun]
            df = df["TIPOG"].value_counts().sort_values(ascending=True)
            fig = px.bar(df, y=df.index, x=df.values, orientation='h', title="", 
                        labels={'x':"Número d'habitatges", 'y':"TIPOG"}, text= df.values)
            fig.layout.xaxis = dict(title="Nombre d'habitatges", tickformat=",d")
            fig.layout.yaxis.title.text = "Tipologia"
            fig.update_traces(marker=dict(color="#66b9a7"))
            return fig

        st.plotly_chart(count_plot_mun(bbdd_estudi_hab_mod, selected_mun), use_container_width=True, responsive=True)

        def dormscount_plot_mun(data, selected_mun):
            df = data[data['Municipi']==selected_mun]
            custom_order = ["0D", "1D", "2D", "3D", "4D", "5+D"]
            df = df["Total dormitoris"].value_counts().reindex(custom_order)
            fig = px.bar(df,  y=df.values, x=df.index,title="", labels={'x':"Número d'habitacions", 'y':"Número d'habitatges"}, text= df.values)
            fig.layout.yaxis = dict(title="Nombre d'habitatges", tickformat=",d")
            fig.layout.xaxis.title.text = "Nombre d'habitacions"
            fig.update_traces(marker=dict(color="#66b9a7"))
            return fig
        
        def lavcount_plot_mun(data, selected_mun):
            df = data[data['Municipi']==selected_mun]

            df = df["Banys i lavabos"].value_counts().sort_values(ascending=True)
            fig = px.bar(df,  y=df.values, x=df.index,title="", labels={'x':"Número de lavabos", 'y':"Número d'habitatges"}, text= df.values)
            fig.layout.yaxis = dict(title="Nombre d'habitatges", tickformat=",d")
            fig.layout.xaxis.title.text = "Nombre de lavabos"
            fig.update_traces(marker=dict(color="#66b9a7"))
            return fig

        left_col, right_col = st.columns((1, 1))
        with left_col:
            st.markdown("""**Habitatges a la venda segons número d'habitacions**""")
            st.plotly_chart(dormscount_plot_mun(bbdd_estudi_hab_mod, selected_mun), use_container_width=True, responsive=True)

        with right_col:
            st.markdown("""**Habitatges a la venda segons número de banys i lavabos**""")
            st.plotly_chart(lavcount_plot_mun(bbdd_estudi_hab_mod, selected_mun), use_container_width=True, responsive=True)


        st.subheader("Comparativa amb anys anteriors: Municipi de " + selected_mun.split(',')[0].strip())

        def table_mun(Municipi, any_ini, any_fin):
            df_mun_filtered = df_final[(df_final["GEO"]==Municipi) & (df_final["Any"]>=any_ini) & (df_final["Any"]<=any_fin)].drop(["Àmbits territorials","Corones","Comarques","Província", "codiine"], axis=1).pivot(index=["Any"], columns=["Tipologia", "Variable"], values="Valor")
            df_mun_unitats = df_final[(df_final["GEO"]==Municipi) & (df_final["Any"]>=any_ini) & (df_final["Any"]<=any_fin)].drop(["Àmbits territorials","Corones","Comarques","Província", "codiine"], axis=1).drop_duplicates(["Any","Tipologia","Unitats"]).pivot(index=["Any"], columns=["Tipologia"], values="Unitats")
            df_mun_unitats.columns= [("HABITATGES PLURIFAMILIARS", "Unitats"), ("HABITATGES UNIFAMILIARS", "Unitats"), ("TOTAL HABITATGES", "Unitats")]
            df_mun_n = pd.concat([df_mun_filtered, df_mun_unitats], axis=1)
            # df_mun_n[("HABITATGES PLURIFAMILIARS", "Unitats %")] = (df_mun_n[("HABITATGES PLURIFAMILIARS", "Unitats")]/df_mun_n[("TOTAL HABITATGES", "Unitats")])*100
            # df_mun_n[("HABITATGES UNIFAMILIARS", "Unitats %")] = (df_mun_n[("HABITATGES UNIFAMILIARS", "Unitats")] /df_mun_n[("TOTAL HABITATGES", "Unitats")])*100
            df_mun_n = df_mun_n.sort_index(axis=1, level=[0,1])
            num_cols = df_mun_n.select_dtypes(include=['float64', 'Int64']).columns
            df_mun_n[num_cols] = df_mun_n[num_cols].round(0)
            df_mun_n[num_cols] = df_mun_n[num_cols].astype("Int64")
            num_cols = df_mun_n.select_dtypes(include=['float64', 'Int64']).columns
            df_mun_n[num_cols] = df_mun_n[num_cols].applymap(lambda x: '{:,.0f}'.format(x).replace(',', '#').replace('.', ',').replace('#', '.'))
            return(df_mun_n)
        left_col, right_col = st.columns((1,1))
        with left_col:
            min_year, max_year = st.sidebar.slider("**Interval d'anys de la mostra:**", value=[2019, 2022], min_value=2019, max_value=2022)
        st.markdown(table_mun(selected_mun, min_year, max_year).to_html(), unsafe_allow_html=True)
        st.markdown(filedownload(table_mun(selected_mun, min_year, max_year), f"Estudi_oferta_{selected_mun}.xlsx"), unsafe_allow_html=True)
        st.markdown("")
        def plot_mun_hist_units(selected_mun, variable_int, any_ini, any_fin):
            df_preus = df_vf_aux[(df_vf_aux['Variable']==variable_int) & (df_vf_aux['GEO']==selected_mun) & (df_vf_aux["Any"]>=any_ini) & (df_vf_aux["Any"]<=any_fin)].drop(['Variable'], axis=1).reset_index().drop('index', axis=1)
            df_preus['Valor'] = np.where(df_preus['Valor']==0, np.NaN, round(df_preus['Valor'], 1))
            df_preus['Any'] = df_preus['Any'].astype(int)
            df_preus = df_preus[df_preus["Tipologia"]!="TOTAL HABITATGES"]
            fig = px.bar(df_preus, x='Any', y='Valor', color='Tipologia', color_discrete_sequence=["#AAC4BA","#00D0A3"], range_y=[0, None], labels={'Valor': variable_int, 'Any': 'Any'}, text= "Valor")
            fig.layout.yaxis = dict(title= variable_int,tickformat=",d")
            valid_years = sorted(df_preus['Any'].unique())
            fig.update_xaxes(tickvals=valid_years)
            fig.update_layout(font=dict(size=13), legend=dict(orientation='h', yanchor='bottom', y=1.05, xanchor='right', x=0.75))
            return fig
        def plot_mun_hist(selected_mun, variable_int, any_ini, any_fin):
            df_preus = df_vf[(df_vf['Variable']==variable_int) & (df_vf['GEO']==selected_mun) & (df_vf["Any"]>=any_ini) & (df_vf["Any"]<=any_fin)].drop(['Variable'], axis=1).reset_index().drop('index', axis=1)
            df_preus['Valor'] = np.where(df_preus['Valor']==0, np.NaN, round(df_preus['Valor'], 1))
            df_preus['Any'] = df_preus['Any'].astype(int)
            fig = px.bar(df_preus, x='Any', y='Valor', color='Tipologia', color_discrete_sequence=["#008B6C","#AAC4BA","#00D0A3"], range_y=[0, None], labels={'Valor': variable_int, 'Any': 'Any'}, text='Valor', barmode='group')
            fig.layout.yaxis = dict(title= variable_int,tickformat=",d")
            fig.update_layout(font=dict(size=13), legend=dict(orientation='h', yanchor='bottom', y=1, xanchor='right', x=0.75))
            return fig
        left_col, right_col = st.columns((1, 1))
        with left_col:
            st.markdown("""**Evolució dels habitatges de nova construcció per tipologia d'habitatge**""")
            st.plotly_chart(plot_mun_hist_units(selected_mun, "Unitats", min_year, max_year), use_container_width=True, responsive=True)
        with right_col:
            st.markdown("""**Evolució de la superfície útil mitjana per tipologia d'habitatge**""")
            st.plotly_chart(plot_mun_hist(selected_mun, 'Superfície mitjana (m² útils)', min_year, max_year), use_container_width=True, responsive=True)
        left_col, right_col = st.columns((1, 1))
        with left_col:
            st.markdown("""**Evolució del preu de venda per m\u00b2 útil  per tipologia d'habitatge**""")
            st.plotly_chart(plot_mun_hist(selected_mun, "Preu de venda per m² útil (€)", min_year, max_year), use_container_width=True, responsive=True)
        with right_col:
            st.markdown("""**Evolució del preu venda mitjà per tipologia d'habitatge**""")
            st.plotly_chart(plot_mun_hist(selected_mun, "Preu mitjà de venda de l'habitatge (€)", min_year, max_year), use_container_width=True, responsive=True)

############################################################  MUNICIPIS: 2023 ################################################
    if selected_edition=="2023":
        mun_names = sorted([name for name in df_vf[(df_vf["Any"]==2023) & (~df_vf["Valor"].isna())]["GEO"].unique() if name != "Catalunya"])
        selected_mun = st.sidebar.selectbox('**Municipi seleccionat:**', mun_names, index= mun_names.index("Barcelona"))
        st.subheader(f"MUNICIPI DE {selected_mun.upper().split(',')[0].strip()}")
        def data_text(selected_mun):
            table80_mun = bbdd_estudi_hab_2023[bbdd_estudi_hab_2023["Municipi"]==selected_mun][["Municipi", "TIPOG", "Superfície útil", "Preu mitjà", "Preu m2 útil"]].groupby(["Municipi"]).agg({"Municipi":['count'], "Superfície útil": [np.mean], "Preu mitjà": [np.mean], "Preu m2 útil": [np.mean]}).reset_index()
            table25_mun = bbdd_estudi_hab_2023[bbdd_estudi_hab_2023["Municipi"]==selected_mun][["Municipi", "TIPOG"]].value_counts(normalize=True).reset_index().rename(columns={0:"Proporció"})
            table61_hab = bbdd_estudi_hab_2023[bbdd_estudi_hab_2023["Municipi"]==selected_mun].groupby(['Total dormitoris']).size().reset_index(name='Proporcions').sort_values(by="Proporcions", ascending=False)
            table61_lav = bbdd_estudi_hab_2023[bbdd_estudi_hab_2023["Municipi"]==selected_mun].groupby(['Banys i lavabos']).size().reset_index(name='Proporcions').sort_values(by="Proporcions", ascending=False)
            try:
                proporcio_tipo = round(table25_mun[table25_mun["TIPOG"]=="Habitatges plurifamiliars"]["Proporció"].values[0]*100,2)
            except IndexError:
                proporcio_tipo = 0

            return([round(table80_mun["Preu mitjà"].values[0][0],2), round(table80_mun["Superfície útil"].values[0][0],2), 
                    round(table80_mun["Preu m2 útil"].values[0][0],2), proporcio_tipo, 
                    table61_hab["Total dormitoris"].values[0], table61_lav["Banys i lavabos"].values[0]])

        st.markdown(f"""Els resultats de l'Estudi d'Oferta de nova construcció del 2023 pel municipi de {selected_mun.split(',')[0].strip()} mostren que el preu mitjà dels habitatges en venda es troba 
        en {data_text(selected_mun)[0]:,.1f} € amb una superfície mitjana útil de {data_text(selected_mun)[1]:,.1f} m\u00b2. Per tant, el preu per m\u00b2 útil es troba en {data_text(selected_mun)[2]:,.1f} € de mitjana. Per tipologies, els habitatges plurifamiliars
        representen el {data_text(selected_mun)[3]:,.1f}% sobre el total d'habitatges, la resta corresponen a habitatges unifamiliars. L'habitatge modal o més freqüent de nova construcció té {data_text(selected_mun)[4]} habitacions i {data_text(selected_mun)[5]} banys o lavabos.""")

        def plotmun_streamlit(data, selected_mun, kpi):
            df = data[(data['Municipi']==selected_mun)]
            fig = px.histogram(df, x=kpi, title= "", labels={'x':kpi, 'y':'Freqüència'})
            fig.data[0].marker.color = "#66b9a7"
            fig.layout.xaxis.title.text = kpi
            fig.layout.yaxis.title.text = 'Freqüència'
            mean_val = df[kpi].mean()
            fig.layout.shapes = [dict(type='line', x0=mean_val, y0=0, x1=mean_val, y1=1, yref='paper', xref='x', 
                                    line=dict(color="black", width=2, dash='dot'))]
            return(fig)

        left_col, right_col = st.columns((1, 1))
        with left_col:
            st.markdown(f"""**Distribució de Preus per m\u00b2 útil**""")
            st.plotly_chart(plotmun_streamlit(bbdd_estudi_hab_mod_2023, selected_mun,"Preu m2 útil"), use_container_width=True, responsive=True)
        with right_col:
            st.markdown(f"""**Distribució de Superfície útil**""")
            st.plotly_chart(plotmun_streamlit(bbdd_estudi_hab_mod_2023, selected_mun, "Superfície útil"), use_container_width=True, responsive=True)
        st.markdown(f"""
        **Tipologia d'habitatges de les promocions**
        """)
        def count_plot_mun(data, selected_mun):
            df = data[data['Municipi']==selected_mun]
            df = df["TIPOG"].value_counts().sort_values(ascending=True)
            fig = px.bar(df, y=df.index, x=df.values, orientation='h', title="", 
                        labels={'x':"Número d'habitatges", 'y':"TIPOG"}, text= df.values)
            fig.layout.xaxis = dict(title="Nombre d'habitatges", tickformat=",d")
            fig.layout.yaxis.title.text = "Tipologia"
            fig.update_traces(marker=dict(color="#66b9a7"))
            return fig

        st.plotly_chart(count_plot_mun(bbdd_estudi_hab_mod_2023, selected_mun), use_container_width=True, responsive=True)

        def dormscount_plot_mun(data, selected_mun):
            df = data[data['Municipi']==selected_mun]
            custom_order = ["0D", "1D", "2D", "3D", "4D", "5+D"]
            df = df["Total dormitoris"].value_counts().reindex(custom_order)
            fig = px.bar(df,  y=df.values, x=df.index,title="", labels={'x':"Número d'habitacions", 'y':"Número d'habitatges"}, text= df.values)
            fig.layout.yaxis = dict(title="Nombre d'habitatges", tickformat=",d")
            fig.layout.xaxis.title.text = "Nombre d'habitacions"
            fig.update_traces(marker=dict(color="#66b9a7"))
            return fig
        
        def lavcount_plot_mun(data, selected_mun):
            df = data[data['Municipi']==selected_mun]

            df = df["Banys i lavabos"].value_counts().sort_values(ascending=True)
            fig = px.bar(df,  y=df.values, x=df.index,title="", labels={'x':"Número de lavabos", 'y':"Número d'habitatges"}, text= df.values)
            fig.layout.yaxis = dict(title="Nombre d'habitatges", tickformat=",d")
            fig.layout.xaxis.title.text = "Nombre de lavabos"
            fig.update_traces(marker=dict(color="#66b9a7"))
            return fig

        left_col, right_col = st.columns((1, 1))
        with left_col:
            st.markdown("""**Habitatges a la venda segons número d'habitacions**""")
            st.plotly_chart(dormscount_plot_mun(bbdd_estudi_hab_mod_2023, selected_mun), use_container_width=True, responsive=True)

        with right_col:
            st.markdown("""**Habitatges a la venda segons número de Banys i lavabos**""")
            st.plotly_chart(lavcount_plot_mun(bbdd_estudi_hab_mod_2023, selected_mun), use_container_width=True, responsive=True)


        st.subheader("Comparativa amb anys anteriors: Municipi de " + selected_mun.split(',')[0].strip())

        def table_mun(Municipi, any_ini, any_fin):
            df_mun_filtered = df_final[(df_final["GEO"]==Municipi) & (df_final["Any"]>=any_ini) & (df_final["Any"]<=any_fin)].drop(["Àmbits territorials","Corones","Comarques","Província", "codiine"], axis=1).pivot(index=["Any"], columns=["Tipologia", "Variable"], values="Valor")
            df_mun_unitats = df_final[(df_final["GEO"]==Municipi) & (df_final["Any"]>=any_ini) & (df_final["Any"]<=any_fin)].drop(["Àmbits territorials","Corones","Comarques","Província", "codiine"], axis=1).drop_duplicates(["Any","Tipologia","Unitats"]).pivot(index=["Any"], columns=["Tipologia"], values="Unitats")
            df_mun_unitats.columns= [("HABITATGES PLURIFAMILIARS", "Unitats"), ("HABITATGES UNIFAMILIARS", "Unitats"), ("TOTAL HABITATGES", "Unitats")]
            df_mun_n = pd.concat([df_mun_filtered, df_mun_unitats], axis=1)
            # df_mun_n[("HABITATGES PLURIFAMILIARS", "Unitats %")] = (df_mun_n[("HABITATGES PLURIFAMILIARS", "Unitats")]/df_mun_n[("TOTAL HABITATGES", "Unitats")])*100
            # df_mun_n[("HABITATGES UNIFAMILIARS", "Unitats %")] = (df_mun_n[("HABITATGES UNIFAMILIARS", "Unitats")] /df_mun_n[("TOTAL HABITATGES", "Unitats")])*100
            df_mun_n = df_mun_n.sort_index(axis=1, level=[0,1])
            num_cols = df_mun_n.select_dtypes(include=['float64', 'Int64']).columns
            df_mun_n[num_cols] = df_mun_n[num_cols].round(0)
            df_mun_n[num_cols] = df_mun_n[num_cols].astype("Int64")
            num_cols = df_mun_n.select_dtypes(include=['float64', 'Int64']).columns
            df_mun_n[num_cols] = df_mun_n[num_cols].applymap(lambda x: '{:,.0f}'.format(x).replace(',', '#').replace('.', ',').replace('#', '.'))
            return(df_mun_n)
        left_col, right_col = st.columns((1,1))
        with left_col:
            min_year, max_year = st.sidebar.slider("**Interval d'anys de la mostra:**", value=[2019, 2023], min_value=2019, max_value=2023)
        st.markdown(table_mun(selected_mun, min_year, max_year).to_html(), unsafe_allow_html=True)
        st.markdown(filedownload(table_mun(selected_mun, min_year, max_year), f"Estudi_oferta_{selected_mun}.xlsx"), unsafe_allow_html=True)
        st.markdown("")
        def plot_mun_hist_units(selected_mun, variable_int, any_ini, any_fin):
            df_preus = df_vf_aux[(df_vf_aux['Variable']==variable_int) & (df_vf_aux['GEO']==selected_mun) & (df_vf_aux["Any"]>=any_ini) & (df_vf_aux["Any"]<=any_fin)].drop(['Variable'], axis=1).reset_index().drop('index', axis=1)
            df_preus['Valor'] = np.where(df_preus['Valor']==0, np.NaN, round(df_preus['Valor'], 1))
            df_preus['Any'] = df_preus['Any'].astype(int)
            df_preus = df_preus[df_preus["Tipologia"]!="TOTAL HABITATGES"]
            fig = px.bar(df_preus, x='Any', y='Valor', color='Tipologia', color_discrete_sequence=["#AAC4BA","#00D0A3"], range_y=[0, None], labels={'Valor': variable_int, 'Any': 'Any'}, text= "Valor")
            fig.layout.yaxis = dict(title="Unitats", tickformat=",d")
            valid_years = sorted(df_preus['Any'].unique())
            fig.update_xaxes(tickvals=valid_years)
            fig.update_layout(font=dict(size=13), legend=dict(orientation='h', yanchor='bottom', y=1.05, xanchor='right', x=0.75))
            return fig
        def plot_mun_hist(selected_mun, variable_int, any_ini, any_fin):
            df_preus = df_vf[(df_vf['Variable']==variable_int) & (df_vf['GEO']==selected_mun) & (df_vf["Any"]>=any_ini) & (df_vf["Any"]<=any_fin)].drop(['Variable'], axis=1).reset_index().drop('index', axis=1)
            df_preus['Valor'] = np.where(df_preus['Valor']==0, np.NaN, round(df_preus['Valor'], 1))
            df_preus['Any'] = df_preus['Any'].astype(int)
            fig = px.bar(df_preus, x='Any', y='Valor', color='Tipologia', color_discrete_sequence=["#008B6C","#AAC4BA","#00D0A3"], range_y=[0, None], labels={'Valor': variable_int, 'Any': 'Any'}, text='Valor', barmode='group')
            fig.layout.yaxis = dict(title= variable_int,tickformat=",d")
            fig.update_layout(font=dict(size=13), legend=dict(orientation='h', yanchor='bottom', y=1, xanchor='right', x=0.75))
            return fig
        left_col, right_col = st.columns((1, 1))
        with left_col:
            st.markdown("""**Evolució dels habitatges de nova construcció per tipologia d'habitatge**""")
            st.plotly_chart(plot_mun_hist_units(selected_mun, "Unitats", min_year, max_year), use_container_width=True, responsive=True)
        with right_col:
            st.markdown("""**Evolució de la superfície útil mitjana per tipologia d'habitatge**""")
            st.plotly_chart(plot_mun_hist(selected_mun, 'Superfície mitjana (m² útils)', min_year, max_year), use_container_width=True, responsive=True)
        left_col, right_col = st.columns((1, 1))
        with left_col:
            st.markdown("""**Evolució del preu de venda per m\u00b2 útil  per tipologia d'habitatge**""")
            st.plotly_chart(plot_mun_hist(selected_mun, "Preu de venda per m² útil (€)", min_year, max_year), use_container_width=True, responsive=True)
        with right_col:
            st.markdown("""**Evolució del preu venda mitjà per tipologia d'habitatge**""")
            st.plotly_chart(plot_mun_hist(selected_mun, "Preu mitjà de venda de l'habitatge (€)", min_year, max_year), use_container_width=True, responsive=True)


############################################################  DISTRICTES DE BARCELONA ################################################
if selected=="Districtes de Barcelona":
    st.sidebar.header("**DISTRICTES DE BARCELONA**")
    edicio_any = ["2022","2023"]
    selected_edition = st.sidebar.radio("**Any**", edicio_any)


############################################################  DISTRICTES DE BARCELONA: 2022 ################################################
    if selected_edition=="2022":
        dis_names_aux_num = sorted(bbdd_estudi_prom["Nom DIST"].dropna().unique().tolist())
        dis_names_aux = [i[3:] for i in dis_names_aux_num]
        selected_dis = st.sidebar.selectbox('**Districte seleccionat:**', dis_names_aux)
        st.subheader("DISTRICTES DE BARCELONA")
        st.write(f"""Dels 3.278 habitatges pertanyents a les 199 promocions
                    registrades a la ciutat de Barcelona, resta per vendre el
                    42,4%. El comportament per districtes és força diferenciat
                    i oscil·la entre Ciutat Vella, on l’oferta és del 58,6%
                    dels habitatges, a Sant Martí i Les Corts, on aquesta
                    oferta disminueix fins a situar-se en un 25,4% i un 19,5%
                    respectivament. Per barris, aquest comportament evidencia
                    encara més les diferències: a Sant Antoni, Can
                    Baró, Porta, la Maternitat i Sant Ramon, Vallvidrera, el
                    Tibidabo i les Planes, el Turó de la Peira, Verdun, Prosperitat
                    i la Trinitat Vella resten per vendre la totalitat dels
                    habitatges, o la Font de la Guatlla, Sants, Sant Pere,
                    Santa Caterina i la Ribera, i Sants-Badal, on resten per
                    vendre més del 80% dels habitatges. En l’extrem contrari
                    se situen la Clota, el Poblenou, la Bordeta, el Poble Sec
                    i la Marina del Prat Vermell, on resten per vendre menys
                    del 10% dels habitatges.
                    Del 42,4% d’habitatges en oferta de venda al municipi de
                    Barcelona el 40,3% d’aquests estan acabats i el 44,1%
                    es troben en alguna fase constructiva.
                    L’oferta dels habitatges a la venda es concentra en la tipologia
                    de 2 dormitoris (41,7%) i de 3 dormitoris (35,5%),
                    reduint-se al 12,0% els d’1 dormitori i al 8,1% els de 4
                    dormitoris. Encara en percentatges menors es situen
                    l’1,8% d’habitatges tipus loft i el 0,9% d’habitatges de
                    cinc o més dormitoris.
                    A la ciutat de Barcelona és on la rehabilitació integral
                    té més presència, assolint el 30,7% de les promocions,que comporta el 31,5% dels habitatges en oferta. Per
                    districtes, la presència de la rehabilitació integral és desigual:
                    a Sarrià-Sant Gervasi, Nou Barris, Gràcia, Horta-
                    Guinardó i Sant Martí està per sota del 15%, mentre que
                    hi ha districtes on conforma la majoria de l’oferta com
                    Ciutat Vella (85,7%), l’Eixample (74,2%). Una situació
                    que es reflecteix més nítidament si l’anàlisi es trasllada
                    a escala de barris, registrant-se 27 barris (dels 52 barris
                    de la ciutat amb promocions actives) sense cap habitatge
                    en oferta provinent de la rehabilitació integral, mentre
                    hi ha barris on la totalitat de la seva oferta prové de la
                    rehabilitació integral: Sant Pere, Santa Caterina i la Ribera,
                    l’antiga Esquerra de l’Eixample, la Maternitat i Sant
                    Ramon i el Poble Sec. Destacar també l’alt percentatge
                    de promocions de rehabilitació integral al Barri Gòtic,
                    la Dreta de l’Eixample i el Raval.
                    El ventall entre els 1.390 habitatges en oferta respecte
                    a la superfície, el preu mitjà, i el preu per metre quadrat
                    útil és amplíssim si s’observa pels districtes de la ciutat.
                    A tall d’exemple, el preu mitjà màxim del metre quadrat
                    útil s’obté a l’Eixample (10.818€) i Sarrià-Sant Gervasi
                    (10.771€), i el preu mitjà mínim s’obté a Sant Andreu
                    (5.254€) i a Nou Barris (4.986€).
                    Així, la mitjana dels habitatges a la venda al municipi
                    de Barcelona és de 80,9m\u00b2 de superfície útil, amb un
                    preu de 630.559€ i un preu mitjà del metre quadrat útil
                    de 7.487€.""")
        st.subheader(f"{selected_dis.upper()}")
        def data_text(selected_dis):
            table80_dis = bbdd_estudi_hab[(bbdd_estudi_hab["Municipi"]=="Barcelona") & (bbdd_estudi_hab["Nom DIST"]==selected_dis)][["Nom DIST", "TIPOG", "Superfície útil", "Preu mitjà", "Preu m2 útil"]].groupby(["Nom DIST"]).agg({"Nom DIST":['count'], "Superfície útil": [np.mean], "Preu mitjà": [np.mean], "Preu m2 útil": [np.mean]}).reset_index()
            table25_dis = bbdd_estudi_hab[(bbdd_estudi_hab["Municipi"]=="Barcelona") & (bbdd_estudi_hab["Nom DIST"]==selected_dis)][["Nom DIST", "TIPOG"]].value_counts(normalize=True).reset_index().rename(columns={0:"Proporció"})
            table61_hab = bbdd_estudi_hab[(bbdd_estudi_hab["Municipi"]=="Barcelona") & (bbdd_estudi_hab["Nom DIST"]==selected_dis)].groupby(['Total dormitoris']).size().reset_index(name='Proporcions').sort_values(by="Proporcions", ascending=False)
            table61_lav = bbdd_estudi_hab[(bbdd_estudi_hab["Municipi"]=="Barcelona") & (bbdd_estudi_hab["Nom DIST"]==selected_dis)].groupby(['Banys i lavabos']).size().reset_index(name='Proporcions').sort_values(by="Proporcions", ascending=False)

            return([round(table80_dis["Preu mitjà"].values[0][0],2), round(table80_dis["Superfície útil"].values[0][0],2), 
                    round(table80_dis["Preu m2 útil"].values[0][0],2), round(table25_dis[table25_dis["TIPOG"]=="Habitatges plurifamiliars"]["Proporció"].values[0]*100,2), 
                    table61_hab["Total dormitoris"].values[0], table61_lav["Banys i lavabos"].values[0]])

        st.markdown(f"""Els resultats de l'Estudi d'Oferta de Nova Construcció de 2022 pel districte de {selected_dis} de la ciutat de Barcelona mostren que el preu mitjà dels habitatges en venda es troba 
        en {data_text(selected_dis)[0]:,.1f} € amb una superfície mitjana útil de {data_text(selected_dis)[1]:,.1f} m\u00b2. Per tant, el preu per m\u00b2 útil es troba en {data_text(selected_dis)[2]:,.1f} € de mitjana. Per tipologies, els habitatges plurifamiliars
        representen el {data_text(selected_dis)[3]:,.1f}% sobre el total d'habitatges. L'habitatge modal o més freqüent de nova construcció té {data_text(selected_dis)[4]} habitacions i {data_text(selected_dis)[5]} banys o lavabos.""")
        def plotdis_streamlit(data, selected_dis, kpi):
            df = data[(data['Nom DIST']==selected_dis)]
            fig = px.histogram(df, x=kpi, title= "", labels={'x':kpi, 'y':'Freqüència'})
            fig.data[0].marker.color = "#66b9a7"
            fig.layout.xaxis.title.text = kpi
            fig.layout.yaxis.title.text = 'Freqüència'
            mean_val = df[kpi].mean()
            fig.layout.shapes = [dict(type='line', x0=mean_val, y0=0, x1=mean_val, y1=1, yref='paper', xref='x', 
                                    line=dict(color="black", width=2, dash='dot'))]
            return(fig)
        
        left_col, right_col = st.columns((1, 1))
        with left_col:
            st.markdown(f"""**Distribució de preus per m\u00b2 útil**""")
            st.plotly_chart(plotdis_streamlit(bbdd_estudi_hab_mod, selected_dis,"Preu m2 útil"), use_container_width=True, responsive=True)
        with right_col:
            st.markdown(f"""**Distribució de superfície útil**""")
            st.plotly_chart(plotdis_streamlit(bbdd_estudi_hab_mod, selected_dis, "Superfície útil"), use_container_width=True, responsive=True)

        st.markdown(f"""
        **Tipologia d'habitatges de les promocions**
        """)
        def count_plot_dis(data, selected_dis):
            df = data[data['Nom DIST']==selected_dis]
            df = df["TIPOG"].value_counts().sort_values(ascending=True)
            fig = px.bar(df, y=df.index, x=df.values, orientation='h', title="", 
                        labels={'x':"Número d'habitatges", 'y':"TIPOG"}, text= df.values)
            fig.layout.xaxis.title.text = "Número d'habitatges"
            fig.layout.yaxis.title.text = "Tipologia"
            fig.update_traces(marker=dict(color="#66b9a7"))
            return fig

        st.plotly_chart(count_plot_dis(bbdd_estudi_hab_mod, selected_dis), use_container_width=True, responsive=True)
        def dormscount_plot_dis(data, selected_dis):
            df = data[data['Nom DIST']==selected_dis]
            custom_order = ["0D", "1D", "2D", "3D", "4D", "5+D"]
            df = df["Total dormitoris"].value_counts().reindex(custom_order)
            fig = px.bar(df,  y=df.values, x=df.index,title="", labels={'x':"Número d'habitacions", 'y':"Número d'habitatges"}, text= df.values)
            fig.layout.yaxis.title.text = "Número d'habitatges"
            fig.layout.xaxis.title.text = "Número d'habitacions"
            fig.update_traces(marker=dict(color="#66b9a7"))
            return fig
        def lavcount_plot_dis(data, selected_dis):
            df = data[data['Nom DIST']==selected_dis]

            df = df["Banys i lavabos"].value_counts().sort_values(ascending=True)
            fig = px.bar(df,  y=df.values, x=df.index,title="", labels={'x':"Número de lavabos", 'y':"Número d'habitatges"}, text= df.values)
            fig.layout.yaxis.title.text = "Número d'habitatges"
            fig.layout.xaxis.title.text = "Número de lavabos"
            fig.update_traces(marker=dict(color="#66b9a7"))
            return fig
        left_col, right_col = st.columns((1, 1))
        with left_col:
            st.markdown("""**Habitatges a la venda segons número d'habitacions**""")
            st.plotly_chart(dormscount_plot_dis(bbdd_estudi_hab_mod, selected_dis), use_container_width=True, responsive=True)

        with right_col:
            st.markdown("""**Habitatges a la venda segons número de banys i lavabos**""")
            st.plotly_chart(lavcount_plot_dis(bbdd_estudi_hab_mod, selected_dis), use_container_width=True, responsive=True)


        st.subheader(f"Comparativa amb anys anteriors: Districte de {selected_dis}")
        def geo_dis(districte, any_ini, any_fin):
            df_vf_aux = pd.DataFrame()
            for df_frame, year in zip(["dis_2019", "dis_2020", "dis_2021", "dis_2022"], [2019, 2020, 2021, 2022]):
                df_vf_aux = pd.concat([df_vf_aux, tidy_data(eval(df_frame), year)], axis=0)
            df_vf_aux['Variable']= np.where(df_vf_aux['Variable']=="Preu de     venda per      m² útil (€)", "Preu de venda per m² útil (€)", df_vf_aux['Variable'])
            df_vf_aux['Valor'] = pd.to_numeric(df_vf_aux['Valor'], errors='coerce')

            df_vf_aux = df_vf_aux[df_vf_aux['GEO']!="Municipi de Barcelona"]
            df_vf_aux["GEO"] = df_vf_aux["GEO"].str.replace(r"\d+\s", "")
            df_vf_aux = df_vf_aux[df_vf_aux["GEO"].isin(["Ciutat Vella", "Eixample", "Sants-Montjuïc", 
                                                        "Les Corts", "Sarrià - Sant Gervasi", "Gràcia", 
                                                        "Horta-Guinardó", "Nou Barris", "Sant Andreu",
                                                        "Sant Martí"])]
            df_vf_aux = df_vf_aux[df_vf_aux["GEO"]==districte]
            df_wide = pd.pivot(data=df_vf_aux, index="Any", columns=["Tipologia", "Variable"], values="Valor")
            num_cols = df_wide.select_dtypes(include=['float64', 'int64']).columns
            df_wide[num_cols] = df_wide[num_cols].round(0)
            df_wide[num_cols] = df_wide[num_cols].astype("Int64")
            num_cols = df_wide.select_dtypes(include=['float64', 'Int64']).columns
            df_wide[num_cols] = df_wide[num_cols].applymap(lambda x: '{:,.0f}'.format(x).replace(',', '#').replace('.', ',').replace('#', '.'))
            df_wide = df_wide[(df_wide.index>=any_ini) & (df_wide.index<=any_fin)]
            return(df_wide)
        left_col, right_col = st.columns((1,1))
        with left_col:
            min_year, max_year = st.sidebar.slider("**Interval d'anys de la mostra:**", value=[2019, 2022], min_value=2019, max_value=2022)
        st.markdown(geo_dis(selected_dis, min_year, max_year).to_html(), unsafe_allow_html=True)
        st.markdown(filedownload(geo_dis(selected_dis, min_year, max_year), f"Estudi_oferta_{selected_dis}.xlsx"), unsafe_allow_html=True)
        def plot_dis_hist_units(selected_dis, variable_int, any_ini, any_fin):
            df_preus = df_dis_long[(df_dis_long['Variable']==variable_int) & (df_dis_long['GEO']==selected_dis) & (df_dis_long["Any"]>=any_ini) & (df_dis_long["Any"]<=any_fin)].drop(['Variable'], axis=1).reset_index().drop('index', axis=1)
            df_preus['Valor'] = np.where(df_preus['Valor']==0, np.NaN, round(df_preus['Valor'], 1))
            df_preus['Any'] = df_preus['Any'].astype(int)
            df_preus = df_preus[df_preus["Tipologia"]!="TOTAL HABITATGES"]
            fig = px.bar(df_preus[df_preus["Valor"]>0], x='Any', y='Valor', color='Tipologia', color_discrete_sequence=["#AAC4BA","#00D0A3"], range_y=[0, None], labels={'Valor': variable_int, 'Any': 'Any'}, text= "Valor")
            fig.layout.yaxis = dict(title= variable_int,tickformat=",d")
            valid_years = sorted(df_preus['Any'].unique())
            fig.update_xaxes(tickvals=valid_years)
            fig.update_layout(font=dict(size=13), legend=dict(orientation='h', yanchor='bottom', y=1.05, xanchor='right', x=0.75))
            return fig
        def plot_dis_hist(selected_dis, variable_int, any_ini, any_fin):
            df_preus = df_dis_long[(df_dis_long['Variable']==variable_int) & (df_dis_long['GEO']==selected_dis) & (df_dis_long["Any"]>=any_ini) & (df_dis_long["Any"]<=any_fin)].drop(['Variable'], axis=1).reset_index().drop('index', axis=1)
            df_preus['Valor'] = np.where(df_preus['Valor']==0, np.NaN, round(df_preus['Valor'], 1))
            df_preus['Any'] = df_preus['Any'].astype(int)
            fig = px.bar(df_preus[df_preus["Valor"]>0], x='Any', y='Valor', color='Tipologia', color_discrete_sequence=["#008B6C","#AAC4BA","#00D0A3"], range_y=[0, None], labels={'Valor': variable_int, 'Any': 'Any'}, text='Valor', barmode='group')
            fig.layout.yaxis = dict(title= variable_int,tickformat=",d")
            fig.update_layout(font=dict(size=13), legend=dict(orientation='h', yanchor='bottom', y=1, xanchor='right', x=0.75))
            return fig
        
        left_col, right_col = st.columns((1, 1))
        with left_col:
            st.markdown("")
            st.markdown("")
            st.markdown("""**Evolució dels habitatges de nova construcció per tipologia d'habitatge**""")
            st.plotly_chart(plot_dis_hist_units(selected_dis, "Unitats", min_year, max_year), use_container_width=True, responsive=True)
        with right_col:
            st.markdown("")
            st.markdown("")
            st.markdown("""**Evolució de la superfície útil mitjana per tipologia d'habitatge**""")
            st.plotly_chart(plot_dis_hist(selected_dis, 'Superfície mitjana (m² útils)', min_year, max_year), use_container_width=True, responsive=True)
        left_col, right_col = st.columns((1, 1))
        with left_col:
            st.markdown("""**Evolució del preu de venda per m\u00b2 útil  per tipologia d'habitatge**""")
            st.plotly_chart(plot_dis_hist(selected_dis, "Preu de venda per m² útil (€)", min_year, max_year), use_container_width=True, responsive=True)
        with right_col:
            st.markdown("""**Evolució del preu venda mitjà per tipologia d'habitatge**""")
            st.plotly_chart(plot_dis_hist(selected_dis, "Preu mitjà de venda de l'habitatge (€)", min_year, max_year),use_container_width=True, responsive=True)

############################################################  DISTRICTES DE BARCELONA: 2023 ################################################
    if selected_edition=="2023":
        dis_names_aux_num = sorted(bbdd_estudi_prom_2023["Nom DIST"].dropna().unique().tolist())
        dis_names_aux = [i[3:] for i in dis_names_aux_num]
        selected_dis = st.sidebar.selectbox('**Districte seleccionat:**', dis_names_aux)
        st.subheader("DISTRICTES DE BARCELONA")
        st.write(f"""<p>
                    A la ciutat de Barcelona, l’estudi d’aquest any 2023 inclou un total de 224 promocions i 1.560 habitatges destinats a la venda, d’un total de 3.813 habitatges.
                    Els districtes amb major nombre de promocions són Horta-Guinardó (40), Eixample (35) i Sant Martí (29). Els que disposen de menor nombre de promocions són Nou Barris (9) i Les Corts (6). 
                    La quantificació del nombre d’habitatges en oferta de venda modifica l’ordre resultant per nombre de promocions, així els districtes amb més habitatges a la venda són  Eixample (256), Horta-Guinardó (255), Sant Andreu (209) i Sant Martí (203). 
                    Els que disposen de l’oferta més escassa són Nou Barris (66) i Les Corts (24). 
                    L’oferta dels habitatges a la venda es concentra en la tipologia de 2 dormitoris (41,4%) i de 3 dormitoris (36,3%), reduint-se al 12,5% els d’1 dormitori i al 7,3% els de 4 dormitoris. 
                    Encara en percentatges menors es situen l’1,5% d’habitatges tipus loft i 1,0% d’habitatges de cinc o més dormitoris. 
                    </p>   
                    <p>
                    En general, existeix una correspondència directa entre la superfície i el nombre de dormitoris de l’habitatge en oferta. 
                    Aquesta correspondència comporta que el 54,4% dels habitatges d’un dormitori tinguin superfícies iguals o inferiors als 50m², que el 56,2% dels habitatges de dos dormitoris tinguin superfícies entre els 50 i 70m², 
                    que el 46,7% dels habitatges de tres dormitoris tinguin entre 70 i 90m² i que el 50,9% dels habitatges de quatre dormitoris tinguin superfícies entre els 80 i els 100 m².
                    Els preus mitjans per superfícies oscil·len des dels 305.645 euros en els habitatges de menys de 50 m², fins els 1.888.514 euros pels habitatges de més de 160 m² (52 habitatges). 
                    Més concretament, els valors mitjans estimats, en general, configurarien un habitatge tipus de 80,7 m² amb un preu de 628.339€ i un preu del m² de superfície útil de 7.429€.
                    El ventall entre els 1.560 habitatges en oferta, respecte a la superfície, el preu i el preu per metre quadrat útil és amplíssim si s’observa pels districtes de la ciutat, 
                    serveixi a tall de mostra la mitjana del preu màxim del metre quadrat útil que s’obté a Sarrià-Sant Gervasi (10.361€) i l’Eixample (9.949€), i la mitjana del preu mínim que s’obté a Sant Andreu (5.405€) i Nou Barris (5.368€).
                    El preu de venda per metre quadrat útil dels habitatges a la venda varia lleugerament en un -0,8% en relació a 2022 (que el situa en 7.429€/m2).
                    Aquest ajust és el resultat d’uns valor molt semblants en superfície mitjana i preu mitjà de venda els dos anys estudiats al municipi de Barcelona. 
                    Les variacions de preus presenten comportaments diferents en funció del districte, destaquem un increment del 13,9% en el preu per metre quadrat útil a Gràcia o del 10,7% a Sant Martí i un descens del 8,0% a l’Eixample.
                    </p>
                    """, unsafe_allow_html=True)
        st.subheader(f"{selected_dis.upper()}")
        def data_text(selected_dis):
            table80_mun = bbdd_estudi_hab_2023[(bbdd_estudi_hab_2023["Municipi"]=="Barcelona") & (bbdd_estudi_hab_2023["Nom DIST"]==selected_dis)][["Nom DIST", "TIPOG", "Superfície útil", "Preu mitjà", "Preu m2 útil"]].groupby(["Nom DIST"]).agg({"Nom DIST":['count'], "Superfície útil": [np.mean], "Preu mitjà": [np.mean], "Preu m2 útil": [np.mean]}).reset_index()
            table25_mun = bbdd_estudi_hab_2023[(bbdd_estudi_hab_2023["Municipi"]=="Barcelona") & (bbdd_estudi_hab_2023["Nom DIST"]==selected_dis)][["Nom DIST", "TIPOG"]].value_counts(normalize=True).reset_index().rename(columns={0:"Proporció"})
            table61_hab = bbdd_estudi_hab_2023[(bbdd_estudi_hab_2023["Municipi"]=="Barcelona") & (bbdd_estudi_hab_2023["Nom DIST"]==selected_dis)].groupby(['Total dormitoris']).size().reset_index(name='Proporcions').sort_values(by="Proporcions", ascending=False)
            table61_lav = bbdd_estudi_hab_2023[(bbdd_estudi_hab_2023["Municipi"]=="Barcelona") & (bbdd_estudi_hab_2023["Nom DIST"]==selected_dis)].groupby(['Banys i lavabos']).size().reset_index(name='Proporcions').sort_values(by="Proporcions", ascending=False)

            return([round(table80_mun["Preu mitjà"].values[0][0],2), round(table80_mun["Superfície útil"].values[0][0],2), 
                    round(table80_mun["Preu m2 útil"].values[0][0],2), round(table25_mun[table25_mun["TIPOG"]=="Habitatges plurifamiliars"]["Proporció"].values[0]*100,2), 
                    table61_hab["Total dormitoris"].values[0], table61_lav["Banys i lavabos"].values[0]])

        st.markdown(f"""Els resultats de l'Estudi d'Oferta de nova construcció del 2023 pel districte de {selected_dis} de la ciutat de Barcelona mostren que el preu mitjà dels habitatges en venda es troba 
        en {data_text(selected_dis)[0]:,.1f} € amb una superfície mitjana útil de {data_text(selected_dis)[1]:,.1f} m\u00b2. Per tant, el preu per m\u00b2 útil es troba en {data_text(selected_dis)[2]:,.1f} € de mitjana. Per tipologies, els habitatges plurifamiliars
        representen el {data_text(selected_dis)[3]:,.1f}% sobre el total d'habitatges. L'habitatge modal o més freqüent de nova construcció té {data_text(selected_dis)[4]} habitacions i {data_text(selected_dis)[5]} banys o lavabos.""")
        def plotdis_streamlit(data, selected_dis, kpi):
            df = data[(data['Nom DIST']==selected_dis)]
            fig = px.histogram(df, x=kpi, title= "", labels={'x':kpi, 'y':'Freqüència'})
            fig.data[0].marker.color = "#66b9a7"
            fig.layout.xaxis.title.text = kpi
            fig.layout.yaxis.title.text = 'Freqüència'
            mean_val = df[kpi].mean()
            fig.layout.shapes = [dict(type='line', x0=mean_val, y0=0, x1=mean_val, y1=1, yref='paper', xref='x', 
                                    line=dict(color="black", width=2, dash='dot'))]
            return(fig)
        
        left_col, right_col = st.columns((1, 1))
        with left_col:
            st.markdown(f"""**Distribució de Preus per m\u00b2 útil**""")
            st.plotly_chart(plotdis_streamlit(bbdd_estudi_hab_mod_2023, selected_dis,"Preu m2 útil"), use_container_width=True, responsive=True)
        with right_col:
            st.markdown(f"""**Distribució de Superfície útil**""")
            st.plotly_chart(plotdis_streamlit(bbdd_estudi_hab_mod_2023, selected_dis, "Superfície útil"), use_container_width=True, responsive=True)

        st.markdown(f"""
        **Tipologia d'habitatges de les promocions**
        """)
        def count_plot_dis(data, selected_dis):
            df = data[data['Nom DIST']==selected_dis]
            df = df["TIPOG"].value_counts().sort_values(ascending=True)
            fig = px.bar(df, y=df.index, x=df.values, orientation='h', title="", 
                        labels={'x':"Número d'habitatges", 'y':"TIPOG"}, text= df.values)
            fig.layout.xaxis.title.text = "Número d'habitatges"
            fig.layout.yaxis.title.text = "Tipologia"
            fig.update_traces(marker=dict(color="#66b9a7"))
            return fig

        st.plotly_chart(count_plot_dis(bbdd_estudi_hab_mod_2023, selected_dis), use_container_width=True, responsive=True)
        def dormscount_plot_dis(data, selected_dis):
            df = data[data['Nom DIST']==selected_dis]
            custom_order = ["0D", "1D", "2D", "3D", "4D", "5+D"]
            df = df["Total dormitoris"].value_counts().reindex(custom_order)
            fig = px.bar(df,  y=df.values, x=df.index,title="", labels={'x':"Número d'habitacions", 'y':"Número d'habitatges"}, text= df.values)
            fig.layout.yaxis.title.text = "Número d'habitatges"
            fig.layout.xaxis.title.text = "Número d'habitacions"
            fig.update_traces(marker=dict(color="#66b9a7"))
            return fig
        def lavcount_plot_dis(data, selected_dis):
            df = data[data['Nom DIST']==selected_dis]

            df = df["Banys i lavabos"].value_counts().sort_values(ascending=True)
            fig = px.bar(df,  y=df.values, x=df.index,title="", labels={'x':"Número de lavabos", 'y':"Número d'habitatges"}, text= df.values)
            fig.layout.yaxis.title.text = "Número d'habitatges"
            fig.layout.xaxis.title.text = "Número de lavabos"
            fig.update_traces(marker=dict(color="#66b9a7"))
            return fig
        left_col, right_col = st.columns((1, 1))
        with left_col:
            st.markdown("""**Habitatges a la venda segons número d'habitacions**""")
            st.plotly_chart(dormscount_plot_dis(bbdd_estudi_hab_mod_2023, selected_dis), use_container_width=True, responsive=True)

        with right_col:
            st.markdown("""**Habitatges a la venda segons número de Banys i lavabos**""")
            st.plotly_chart(lavcount_plot_dis(bbdd_estudi_hab_mod_2023, selected_dis), use_container_width=True, responsive=True)


        st.subheader(f"Comparativa amb anys anteriors: Districte de {selected_dis}")
        def geo_dis(districte, any_ini, any_fin):
            df_vf_aux = pd.DataFrame()
            for df_frame, year in zip(["dis_2019", "dis_2020", "dis_2021", "dis_2022", "dis_2023"], [2019, 2020, 2021, 2022, 2023]):
                df_vf_aux = pd.concat([df_vf_aux, tidy_data(eval(df_frame), year)], axis=0)
            df_vf_aux['Variable']= np.where(df_vf_aux['Variable']=="Preu de     venda per      m² útil (€)", "Preu de venda per m² útil (€)", df_vf_aux['Variable'])
            df_vf_aux['Valor'] = pd.to_numeric(df_vf_aux['Valor'], errors='coerce')

            df_vf_aux = df_vf_aux[df_vf_aux['GEO']!="Municipi de Barcelona"]
            df_vf_aux["GEO"] = df_vf_aux["GEO"].str.replace(r"\d+\s", "")
            df_vf_aux = df_vf_aux[df_vf_aux["GEO"].isin(["Ciutat Vella", "Eixample", "Sants-Montjuïc", 
                                                        "Les Corts", "Sarrià - Sant Gervasi", "Gràcia", 
                                                        "Horta-Guinardó", "Nou Barris", "Sant Andreu",
                                                        "Sant Martí"])]
            df_vf_aux = df_vf_aux[df_vf_aux["GEO"]==districte]
            df_wide = pd.pivot(data=df_vf_aux, index="Any", columns=["Tipologia", "Variable"], values="Valor")
            num_cols = df_wide.select_dtypes(include=['float64', 'int64']).columns
            df_wide[num_cols] = df_wide[num_cols].round(0)
            df_wide[num_cols] = df_wide[num_cols].astype("Int64")
            num_cols = df_wide.select_dtypes(include=['float64', 'Int64']).columns
            df_wide[num_cols] = df_wide[num_cols].applymap(lambda x: '{:,.0f}'.format(x).replace(',', '#').replace('.', ',').replace('#', '.'))
            df_wide = df_wide[(df_wide.index>=any_ini) & (df_wide.index<=any_fin)]
            return(df_wide)
        left_col, right_col = st.columns((1,1))
        with left_col:
            min_year, max_year = st.sidebar.slider("**Interval d'anys de la mostra:**", value=[2019, 2023], min_value=2019, max_value=2023)
        st.markdown(geo_dis(selected_dis, min_year, max_year).to_html(), unsafe_allow_html=True)
        st.markdown(filedownload(geo_dis(selected_dis, min_year, max_year), f"Estudi_oferta_{selected_dis}.xlsx"), unsafe_allow_html=True)
        def plot_dis_hist_units(selected_dis, variable_int, any_ini, any_fin):
            df_preus = df_dis_long[(df_dis_long['Variable']==variable_int) & (df_dis_long['GEO']==selected_dis) & (df_dis_long["Any"]>=any_ini) & (df_dis_long["Any"]<=any_fin)].drop(['Variable'], axis=1).reset_index().drop('index', axis=1)
            df_preus['Valor'] = np.where(df_preus['Valor']==0, np.NaN, round(df_preus['Valor'], 1))
            df_preus['Any'] = df_preus['Any'].astype(int)
            df_preus = df_preus[df_preus["Tipologia"]!="TOTAL HABITATGES"]
            fig = px.bar(df_preus, x='Any', y='Valor', color='Tipologia', color_discrete_sequence=["#AAC4BA","#00D0A3"], range_y=[0, None], labels={'Valor': variable_int, 'Any': 'Any'}, text= "Valor")
            fig.layout.yaxis = dict(title= variable_int,tickformat=",d")
            fig.update_layout(font=dict(size=13), legend=dict(orientation='h', yanchor='bottom', y=1.05, xanchor='right', x=0.75))
            return fig
        def plot_dis_hist(selected_dis, variable_int, any_ini, any_fin):
            df_preus = df_dis_long[(df_dis_long['Variable']==variable_int) & (df_dis_long['GEO']==selected_dis) & (df_dis_long["Any"]>=any_ini) & (df_dis_long["Any"]<=any_fin)].drop(['Variable'], axis=1).reset_index().drop('index', axis=1)
            df_preus['Valor'] = np.where(df_preus['Valor']==0, np.NaN, round(df_preus['Valor'], 1))
            df_preus['Any'] = df_preus['Any'].astype(int)
            fig = px.bar(df_preus, x='Any', y='Valor', color='Tipologia', color_discrete_sequence=["#008B6C","#AAC4BA","#00D0A3"], range_y=[0, None], labels={'Valor': variable_int, 'Any': 'Any'}, text='Valor', barmode='group')
            fig.layout.yaxis = dict(title= variable_int,tickformat=",d")
            valid_years = sorted(df_preus['Any'].unique())
            fig.update_xaxes(tickvals=valid_years)
            fig.update_layout(font=dict(size=13), legend=dict(orientation='h', yanchor='bottom', y=1, xanchor='right', x=0.75))
            return fig
        
        left_col, right_col = st.columns((1, 1))
        with left_col:
            st.markdown("")
            st.markdown("")
            st.markdown("""**Evolució dels habitatges de nova construcció per tipologia d'habitatge**""")
            st.plotly_chart(plot_dis_hist_units(selected_dis, "Unitats", min_year, max_year), use_container_width=True, responsive=True)
        with right_col:
            st.markdown("")
            st.markdown("")
            st.markdown("""**Evolució de la superfície útil mitjana per tipologia d'habitatge**""")
            st.plotly_chart(plot_dis_hist(selected_dis, 'Superfície mitjana (m² útils)', min_year, max_year), use_container_width=True, responsive=True)
        left_col, right_col = st.columns((1, 1))
        with left_col:
            st.markdown("""**Evolució del preu de venda per m\u00b2 útil  per tipologia d'habitatge**""")
            st.plotly_chart(plot_dis_hist(selected_dis, "Preu de venda per m² útil (€)", min_year, max_year), use_container_width=True, responsive=True)
        with right_col:
            st.markdown("""**Evolució del preu venda mitjà per tipologia d'habitatge**""")
            st.plotly_chart(plot_dis_hist(selected_dis, "Preu mitjà de venda de l'habitatge (€)", min_year, max_year),use_container_width=True, responsive=True)


if selected=="Contacte":
    CONTACT_EMAIL = "estudis@apcecat.cat"
    st.write("")
    st.subheader(":mailbox: Contacteu-nos!")
    contact_form = f"""
    <form action="https://formsubmit.co/{CONTACT_EMAIL}" method="POST">
        <input type="hidden" name="_captcha" value="false">
        <input type="text" name="name" placeholder="Nom" required>
        <input type="email" name="email" placeholder="Correu electrònic" required>
        <textarea name="message" placeholder="La teva consulta aquí"></textarea>
        <button type="submit" class="button">Enviar ✉</button>
    </form>
    """
    st.markdown(contact_form, unsafe_allow_html=True)



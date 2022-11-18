import json
import math
import sys
import time

import urllib3
import threading
import requests
from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QPixmap, QIcon, QPalette, QColor
from PyQt6.QtWidgets import QMainWindow, QFrame, QApplication, QGridLayout, QLineEdit, QPushButton, QWidget, QDialog, \
    QLabel, QTableWidget, QTableWidgetItem

LONGUEUR = 800
HAUTEUR = 800
NB_MAX_POKEMON = 9


class Pokemon:
    def __init__(self, id, nom, poids, taille, types, urlImage, vie, attaque, defense, attaque_speciale, defense_speciale, vitesse):
        self.id = id
        self.nom = nom
        self.poids = poids
        self.taille = taille
        self.types = types
        self.urlImage = urlImage
        self.vie = vie
        self.attaque = attaque
        self.defense = defense
        self.attaque_speciale = attaque_speciale
        self.defense_speciale = defense_speciale
        self.vitesse = vitesse

    def from_api(nom):
        req = requests.get(f"https://pokeapi.co/api/v2/pokemon/{nom}")
        if req.status_code == 200:
            info_json = json.loads(req.text)
            types = []
            for e in info_json["types"]:
                types.append(e["type"]["name"])
            return Pokemon(info_json["id"], nom, info_json["weight"], info_json["height"], types, info_json["sprites"]["back_default"], info_json["stats"][0]["base_stat"], info_json["stats"][1]["base_stat"], info_json["stats"][2]["base_stat"], info_json["stats"][3]["base_stat"], info_json["stats"][4]["base_stat"], info_json["stats"][5]["base_stat"])
        else:
            raise Exception("Erreur ce pokémon n'existe pas")

    def donnees_images(self):
        req = requests.get(self.urlImage)
        if req.status_code == 200:
            return req.content
        else:
            raise ("Image du pokémon non reconnu")

    def __str__(self):
        types_format = ", ".join(self.types)
        return f"id = {self.id}\nnom = {self.nom}\npoids = {self.poids}\ntaille = {self.taille}\ntypes = {types_format}\nvie = {self.vie}\nattaque = {self.attaque}\ndefense = {self.defense}\nattaque spéciale = {self.attaque_speciale}\ndéfense spéciale = {self.defense_speciale}\nvitesse = {self.vitesse}\n"


class Pokedex(QWidget):
    def __init__(self):
        super().__init__()
        self.nbPokemon = 0
        self.resize(LONGUEUR, HAUTEUR)
        self.setWindowTitle("Pokédex")
        self.grille = QGridLayout()
        self.barreDeRecherche = QLineEdit()
        self.barreDeRecherche.setPlaceholderText("entrer un nom de pokémon")
        self.barreDeRecherche.returnPressed.connect(lambda: self.ajoutPokemon(self.barreDeRecherche.text()))
        self.boutonRecherche = QPushButton("recherche")
        self.boutonRecherche.clicked.connect(lambda: self.ajoutPokemon(self.barreDeRecherche.text()))

        self.tableEquipe = QTableWidget(NB_MAX_POKEMON, 7)
        self.tableEquipe.setIconSize(QSize(80, 80))
        self.tableEquipe.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tableEquipe.setHorizontalHeaderLabels(
            ["Id du Pokémon", "Nom du Pokémon", "Poids du Pokémon", "Taille du Pokémon", "Types du pokémon",
             "image du pokémon", "Infos complémentaires"])
        self.tableEquipe.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.tableEquipe.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.tableEquipe.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.tableEquipe.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.tableEquipe.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.tableEquipe.horizontalHeader().setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.tableEquipe.horizontalHeader().setSectionResizeMode(6, QtWidgets.QHeaderView.ResizeMode.Stretch)

        self.boutonEffacer = QPushButton("tout effacer")
        self.boutonEffacer.clicked.connect(lambda: self.effacerPokedex())

        self.grille.addWidget(self.barreDeRecherche, 0, 0)
        self.grille.addWidget(self.boutonRecherche, 0, 1)
        self.grille.addWidget(self.boutonEffacer, 0, 2)
        self.grille.addWidget(self.tableEquipe, 1, 0)
        self.setLayout(self.grille)
        self.show()

    def effacerPokedex(self):
        self.tableEquipe.clearContents()
        self.nbPokemon = 0

    def ajoutPokemon(self, nom):

        if self.nbPokemon < NB_MAX_POKEMON:
            try:
                self.tableEquipe.setRowHeight(self.nbPokemon, 80)
                pokemon = Pokemon.from_api(nom)
                self.tableEquipe.setItem(self.nbPokemon, 0, QTableWidgetItem(str(pokemon.id)))
                self.tableEquipe.setItem(self.nbPokemon, 1, QTableWidgetItem(pokemon.nom))
                self.tableEquipe.setItem(self.nbPokemon, 2, QTableWidgetItem(str(pokemon.poids)))
                self.tableEquipe.setItem(self.nbPokemon, 3, QTableWidgetItem(str(pokemon.taille)))
                self.tableEquipe.setItem(self.nbPokemon, 4, QTableWidgetItem(", ".join(pokemon.types)))

                celluleImage = QTableWidgetItem()
                pixmapCellule = QPixmap()
                pixmapCellule.loadFromData(pokemon.donnees_images())
                iconCellule = QIcon(pixmapCellule)
                celluleImage.setIcon(iconCellule)
                self.tableEquipe.setItem(self.nbPokemon, 5, celluleImage)
                bouton_info_complementaire = QPushButton()
                bouton_info_complementaire.setText("plus d'infos...")
                bouton_info_complementaire.clicked.connect(lambda: afficher_info_complementaire())
                self.tableEquipe.setCellWidget(self.nbPokemon, 6, bouton_info_complementaire)
                self.nbPokemon += 1
                print(pokemon)
            except Exception as pokemon_non_trouve:
                def switch_couleur():
                    self.barreDeRecherche.setStyleSheet("QLineEdit {background-color: rgba(255, 0, 0, 127);}")

                    time.sleep(1.0)
                    self.barreDeRecherche.setStyleSheet("QLineEdit {background-color: rgba(255, 0, 0, 0);}")

                print(pokemon_non_trouve)
                threadCouleur = threading.Thread(target=switch_couleur)
                threadCouleur.start()

            def afficher_info_complementaire(self):
                pass


def main():
    app = QApplication(sys.argv)
    pokedex = Pokedex()
    sys.exit(app.exec())

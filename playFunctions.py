from random import shuffle
from utils import *
import tidalapi
from random import randint
import json
import requests

# Fonction qui prends en entrée une playlist et qui récupère le mix de chaque piste
# unrated (list[tidalapi.Track]) : Liste des pistes pour lesquelles la récupération du mix à échoué [Paramère Entrée/Sortie] ! Pas de récupération si non renseigné !
# Console (bool) : Affiche ou non les étapes du traitement dans la console
# IndexMax (int) : Est le nombre de titre à traiter maximum, par défaut il traitera toute la playlist
def recuperationMixOfPlaylists(tracks : list[tidalapi.Track], unrated : list[tidalapi.Track] = [], Console : bool = True, indexMax : int = -1) -> list[list[tidalapi.Track]]:
    iMax = indexMax if indexMax!=-1 else len(tracks)
    res : list[list[tidalapi.Track]] = []
    for i in range(iMax):
        try:
            print(f"{i} : {tracks[i].name} - {tracks[i].artist.name}") if Console else None
            mix : tidalapi.mix = tracks[i].get_radio_mix()
            res.append(mix.items())
            # res.append(tracks[i].get_track_radio()) # Non fonctionnel
        except:
            unrated.append(tracks[i])
            print(f"Erreur lors du traitement de la piste {tracks[i].name} - {tracks[i].artist.name}") if Console else None
    return res

# Fonction qui prends une liste de mix (list[list[tidalapi.Track]])
# L'idée est de trouver si les premiers titres de chaque mix se trouvent dans un autre mix
# Console (bool) : Affiche ou non les étapes du traitement dans la console
def MergeMixByIntersect(listOfMix : list[list[tidalapi.Track]], Console : bool = True) -> list[list[tidalapi.Track]]:
    res = []
    playlist = []
    for l in listOfMix:                 # Récupération des premiers titres de chaque mix
        playlist.append(l.pop(0))
    for i in range (len(listOfMix)):    # Parcours de chaque mix pour trouver si on trouve des titres en commun avec notre playlist
        print(f"Traitement de la piste {i} : {playlist[i].name}") if Console else None
        inter = IntersectionTrackList(listOfMix[i],playlist)
        if len(inter)>0:
            res.append(inter)
        else:
            res.append([playlist[i]])
    return res

# Fonction qui fais un merge entre des playlists en fonctions du nombre d'éléments en commmun
# L : Liste des playlists à traiter
# untraited : liste des playlists qui ont aucune intersection avec les autres playlists (par défaut vide) [Paramètre Entrée/Sortie] ! Pas de récupération si non renseigné !
# interMin : Nombre d'éléments en commun minimum pour faire un merge (par défaut 1)
# lAbsrobtion : Nombre de playlist maximum qu'une playlist peut en absorber une autre (par défaut 10)
# lAsborbe : Nombre de playlist maximum qu'une playlist peut être absorbé par une autre (par défaut 1)
# Console : Affiche ou non les étapes du traitement dans la console
def MegePlaylistByIntersect(L : list[list[tidalapi.Track]], untraited : list[tidalapi.Track] = [], interMin : int = 1, lAbsrobtion : int = 10, lAsborbe : int = 1, Console : bool = True):
    res = [[] for _ in range(len(L))]         # Résultat final
    Abso = [[0,0,True] for _ in range(len(L))]     # (Nombre de playlist absorbé, Nombre de playlist qui m'absorbe, J'ai le droit d'être utiliser)
    order = [i for i in range(len(L))]        # Ordre de d'accès aux playlists
    shuffle(order)
    for i in range(len(L)):
        print(f"Traitement de la liste {i} : {len(L[i])} éléments") if Console else None
        tmp = []
        for j in order:
            if Abso[i][2] and Abso[i][0]<=lAbsrobtion and j!=i:                 # J'ai absorbé mon max ou je n'ai pas le droit de traiter
                if Abso[j][2] and Abso[j][1]<=lAsborbe:                         # J'ai été absorbé mon max ou je n'ai pas le droit de traiter
                    intersect = IntersectionTrackList(L[i],L[j])
                    if len(intersect)>=interMin:                                # Cas ou on respecte toutes les conditions
                        appendList(tmp,Merge(L[i],L[j]).copy(),True)
                        Abso[i][0] += 1
                        Abso[j][1] += 1
                    else:                                                       # Pas assez de titre en commun
                        pass
                else:                                                           # Cas ou on a déjà traité j
                    pass
            else:                                                               # Je suis moi-même
                pass
        if Abso[i][0]>0:
            res[i] = tmp.copy()
        else:
            if Abso[i][1]==0 and Abso[i][2]:
                print(f"Je n'ai pas été traité : {i}") if Console else None
                untraited.append(L[i])
    return res

# Fonction qui retourne une liste de l'union des playlists qui ont une taille inférieur au seuil
# ListOfPLaylist : Liste des playlists à traiter
# seuil : Seuil de taille maximum authorisé pour une playlist (par défaut 1)
def removeToLittle(ListOfPlaylist : list[list[tidalapi.Track]],seuil : int = 1) -> list[tidalapi.Track]:
    res = []
    for i in range(len(ListOfPlaylist)):
        if len(ListOfPlaylist[i])<=seuil:
            appendList(res,ListOfPlaylist[i].copy(),True)
            ListOfPlaylist[i] = []
    return res

# Fonciton qui supprime les playlists dupliquées
# L : Liste des playlists à traiter
# s : Seuil de similarité pour considérer que deux playlists sont les mêmes (par défaut 0)
# Deux playlists sont considiérées similaire si elles ont au moins len(la plus petite playlist) - s éléments en commun
def supprDuplicatedPlaylist(L : list[list[tidalapi.Track]],s : int = 0, Console : bool = True) -> None:
    for i in range(len(L)):
        for j in range(len(L)):
            try:
                if i!=j and sameContent(L[i],L[j],s):
                        appendList(L[i],L[j],True)
                        L[j] = []
                        print("Suppression de playlist avec les même contenu") if Console else None
                else:
                    # Rien à faire
                    pass
            except ValueError as e:
                print(f"Erreur lors du traitement des playlists {i} et {j} : {e}") if Console else None

# Fonction qui renvoie sous forme de texte le nom d'artistes de musiques pris aléatoirement
# L : Une playlist
# MaxArtist : le nombre Max de titre d'ou viennent les artistes
def getNameByArtists(L : list[tidalapi.Track],MaxArtist : int = 3) -> str | None:
    res = ""
    if len(L)==0:
        return None
    else:
        toPick = []
        for i in range(MaxArtist):
            pick = randint(0,len(L))
            while len(toPick)<len(L) and (pick in toPick):
                pick = randint(0,len(L))
        for i in toPick:
            res = res + L[i].artist + " "

# Fonction qui supprime toutes les playlists vides
def deleteEmptyPlaylist(L : list[list[tidalapi.Track]]):
    indexToDelete = []
    for i in range(len(L)-1,-1,-1):        # On fait un parcours décroissant pour trouver les listes vides et ensuite les supprimer de la fin vers le début
        if len(L[i])==0:
            indexToDelete.append(i)
    for i in indexToDelete:             # On supprime
        L.pop(i)


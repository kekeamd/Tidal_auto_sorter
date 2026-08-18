import os
import tidalapi
import Coherence
from random import choice as randchoose
from random import randint
import requests as rq

def clear():
    os.system("cls")

# Renvoie la liste la plus petite (si égale renvoie L1)
def minList(L1 : list[any] , L2 : list[any]) -> list[any]:
    return L1 if len(L1)<=len(L2) else L2

# Renvoie la liste la plus grande (si égale renvoie L1)
def maxList(L1 : list[any] , L2 : list[any]) -> list[any]:
    return L1 if len(L1)>=len(L2) else L2

# Renvoie l'intersection de deux listes de Track
def IntersectionTrackList(L1 : list[tidalapi.Track],L2 : list[tidalapi.Track],WithArtist : bool = True):
    res = []
    for i in L1:
        for j in L2:
            if i.name == j.name and (i.artist.name == j.artist.name or not WithArtist):
                res.append(i)
    return res

# def VerifMix(t,listOfOhter,nbEtape,traité : list[tidalapi.Track] = []):
#     mix = t.get_radio_mix()

def isInWithName(t : tidalapi.Track ,listOfOhter : list[tidalapi.Track]):
    for el in listOfOhter:
        if (el.name == t.name) and (el.artist.name == t.artist.name):
            return True
    return False

def Merge(L1 : list[tidalapi.Track],L2 : list[tidalapi.Track]):
    res = []
    for e in L1:
        if not isInWithName(e,res):
            res.append(e)
    for e2 in L2:
        if not isInWithName(e2,res):
            res.append(e2)
    return res

# Fonction qui verse tout les éléments de L2 dans L1
# Supprime les duplicata
# isTrack : bool qui détérmine si les éléments à traiter son des titres
def appendList(dst,src,isTrack : bool = False):
    for e in src:
        if isTrack and not isInWithName(e,dst):          # Cas ou on traite des titres
            dst.append(e)
        elif (not isTrack) and (not (e in dst)):                             # Cas classique
            dst.append(e)

# Vérifie si deux playlists sont similaire
# Si une playlist est inclus dans l'autre on les considèreras similaire
def sameContent(L1,L2,seuil : int = -1):
    nbsim=0
    smallest = minList(L1,L2)
    biggest = maxList(L2,L1)
    s = len(smallest) - (0 if seuil==-1 else seuil) - 1 # - 1 car basé sur la taille des listes
    if len(smallest)==0:
        s = 0
    if s<0:
        raise ValueError("SameContent : Seuil doit être supérieur ou égal à 0 et inférieur ou égal à la taille de la plus petite liste")
    if len(biggest)<len(smallest):
        raise ValueError("SameContent : Il ya un eu problème de calcul")
    for e in smallest:
        if isInWithName(e,biggest):
            nbsim+=1
    if nbsim<s:
        return False
    else:
        return True

# Fonction qui affiche les types de sort
# type : si en dehors des cas affiche tout
def printSortType(type : int = -1):
    match type:
        case 1:
            print("1 : Tri par mix de chaque piste (Verification de la présence des titres dans les mix de chaque piste)")
        case 2:
            print("2 : Tri par mix + merge")
        case 3:
            print("3 : Tri par genre (Comparaison de genre entre toutes les pistes)")
        case _:
            print("1 : Tri par mix de chaque piste (Verification de la présence des titres dans les mix de chaque piste)")
            print("2 : Tri par mix + merge")
            print("3 : Tri par genre (Comparaison de genre entre toutes les pistes)")

# Affiche proprement une liste
# message, messsage à affichier avant (Par défaut "Elements : ")
def afficheListe(l : list[str], message : str = "Elements : ", tab : bool = True, index : bool = False, short : bool = True):
    if len(l)==0:
        return None
    itemType = None
    print("====================")
    print(message) #============================== Message de devanture de liste
    print("====================")
    accepted=[tidalapi.Track,tidalapi.playlist.Playlist,tidalapi.playlist.UserPlaylist,tidalapi.artist,int,str,list]
    itemType = type(l[0])
    if not (itemType in accepted):
        raise(TypeError(f"utils.choice : le type {itemType} n'est pas pris en charge !({accepted})"))
    for i in range(len(l)):
        e = l[i] # Element qu'on regarde
        if itemType != list:
            print("     ",end="") if tab else None
            print(f"{i} - ",end="") if index else print("- ",end="")
        if type(e)!=itemType: #====================================================================== Vérification d'une incohérence                                                                     
            raise(TypeError(f"Un élément de la liste à un type étrange (Ne correspond pas au reste : {type(e)} ==> {itemType})"))
        
        #print(itemType)
        
        if itemType == tidalapi.Track: #============================================================= Cas Track
            print(f"{e.full_name} - {e.artist.name}")
        elif itemType == tidalapi.playlist.Playlist or itemType == tidalapi.playlist.UserPlaylist: #= Cas Playlist
            if short: # Affichage COURT des playlists : Nom sans les titres
                print(f"{e.name} - {e.num_tracks}")
            else: # Affichage LONG des playlists : Avec les titres
                affichePlaylist(e,f"{e.name} - {e.num_tracks}",True,False)
        
        elif itemType == tidalapi.artist.Artist: #=================================================== Cas Artist
            print(f"{e.name}")
        
        elif itemType == list: #===================================================================== Cas Liste
            afficheListe(e,f"Liste numéro {i}")
        
        else: #====================================================================================== Autres cas
            print(f"{e}")
    print("====================")

# Fonction qui permet d'afficher les éléments d'une playlist
# Message : Le nom de la Playlist par défaut
# tab : Une tabulation devant les titres ?
# index : Les titres doivent être indexé ou pas ?
def affichePlaylist(p : tidalapi.playlist.Playlist | tidalapi.playlist.UserPlaylist, message : str = None, tab : bool = True, index : bool = True):
    if type(p) != tidalapi.playlist.Playlist and type(p) != tidalapi.playlist.UserPlaylist:
        raise(TypeError(f"utils.choice : le type {type(p)} n'est pas pris en charge !(tidalapi.playlist.Playlist ou tidalapi.playlist.UserPlaylist)"))
    if message == None:
        message = f"{p.name} - {p.num_tracks}"
    TrackList = p.tracks()
    print("====================")
    print(message)
    print("====================")
    for i in range(len(TrackList)):
        e = TrackList[i]
        print("     ",end="") if tab else None
        print(f"{i} - ",end="") if index else print("- ",end="")
        print(f"{e.full_name} - {e.artist.name}")
    print("====================")

# Renvoie l'intersection de deux listes de type "primitf"
def Intersection(L1 : list[str | int] ,L2 : list[str | int]) -> list[str | int]:
    res = []
    smallest = minList(L1,L2)
    biggest = maxList(L2,L1)
    for e in smallest:
        if e in biggest and not( e in res):
            res.append(e)
    return res

# Renvoie si une liste est incluse dans l'autre
def Include(L1 : list[str | int] ,L2 : list[str | int]) -> bool:
    return len(Intersection(L1,L2)) == len(minList(L1,L2))

# Affiche les selections de genres
def affiche_genre_selection(L : list[list[str]], message : str = "\nVos selections : ") -> None:
    print(message)
    for i in range(len(L)):
        afficheListe(L[i],f"Selection {i} : ")

# Fonction ayant pour SEULE utilité d'affiché l'ensemble des données de data
# Rappel de structure :
# data = {'playlists' : [], 'typeSort' : -1, 'AfficheConsole' : True, 'typeGenreSort' : -1, 'genresList' : []}
def affiche_data(data : dict,savedPlaylistsNames : list[str]) -> None:
    print(f"Affichage console : {data["AfficheConsole"]}\n")
    print(f"Cohérence des playlists : {Coherence.Coherence(data["coherence"]).name}\n")
    print("===============")
    print("Type de tri :")
    printSortType(data["typeSort"])
    print("===============")
    if data["typeSort"] == 3 and data["typeGenreSort"] != -1:
        print("\n===============================")
        print("Tri par genre choisi : ",end="")
        print("1 : Automatique") if data["typeGenreSort"] == 1 else None
        if data["typeGenreSort"] == 2:
            print("2 : Manuel")
            try:
                affiche_genre_selection(data["genreList"],"\nVoici les séléctions de genres : ")
            except:
                pass
        print("===============================")
    print("")
    afficheListe(savedPlaylistsNames,"Voici les playlist qui vont être triées :",False,False)




# Permet de faire une demande de selection à l'utilisateur à partir d'une liste
# l : La liste des élément dans lesquels il faut faire la séléction
# maxItems : Le nombre maximum d'items à choisir (-1 pour aucune limite)
# OriginalItems : Paramètre selon lequel on renvoie une liste de nombre (Les éléments séléctionner) ou la liste des éléments séléctionner
# default : Element à mettre dans la liste final si rien n'est choisi /!\ N'accepte pas les éléments qui ne sont pas dans la liste de base /!\
# min : nombre d'éléments minimum à sélectionner
# infoSupp : Message à marquer en supplément
def choice(l: list, message : str = "Liste d'éléments à choisir",
            maxItems : int = -1,
            OriginalItems : bool = False,
            default : any | None = None,
            short : bool = False,
            minItems : bool = 1) -> (list | list[int]):
    itemType = None
    if len(l)==0 or maxItems==0:
        return []
    accepted=[tidalapi.Track,tidalapi.playlist.Playlist,tidalapi.playlist.UserPlaylist,tidalapi.artist,int,str,list]
    itemType = type(l[0])
    if not (itemType in accepted):
        raise(TypeError(f"utils.choice : le type {itemType} n'est pas pris en charge !({accepted})"))
    choosed : list[int] = []
    check=None
    while((check!='N' and check!='S' and check != 'X' and check !='') and (maxItems==-1 or (maxItems>=0 and maxItems>len(choosed))) or (len(choosed)<minItems)):
        clear()
        afficheListe(l,message,False,True,short) # On affiche les éléments qui PEUVENT être SELECTIONNER
        if len(choosed)>0: # On affiche les éléments déjà SELECTIONNER
            choosed_element : list[any] = []
            for e in choosed:
                if itemType != tidalapi.artist:
                    choosed_element.append(l[e])
                else:
                    choosed_element.append(l[e].name)
            afficheListe(choosed_element,"\nElements séléctionner :",True,True,True)
        
        print("\nVeuillez choisir les éléments que vous souhaitez séléctionner !")
        print("Format accepté : ")
        print("- numero_item (Permet d'ajouter UN élément à la selection)")
        print("- numero_item,numero_item... (Permert d'ajouter une liste d'éléments à la selection)")
        print("- 'N' | 'S' | 'X' | '' (Permet de terminer la saisie ) /!\\ NE PAS METTRE LES ' /!\\")
        saisie = input("\nVotre saisie : ")
        for e in saisie.split(','):
            is_number=True
            try:
                e = int(e.strip())
            except:
                is_number=False # On a pas saisie un nombre ?
                check = e.upper()
            if is_number:
                if not (e in choosed) and e<len(l):
                    if (maxItems==-1 or (maxItems>=0 and maxItems>len(choosed))):
                        choosed.append(e)
                    else:
                        pass # Nombre maximum de choix atteint !
                else:
                    print(f"Elément {e} déjà dans la saisie !")
        choosed.sort()
    res = []
    if len(choosed)==0 and default!=None:
        try:
            choosed.append(l.index(default))
        except:
            pass
    if OriginalItems: # Liste d'éléments
        for i in choosed:
            res.append(l[i])
    else:             # Liste d'int
        res=choosed
    return res

# Fonction qui récupére les genres d'une piste
# Ajout la piste à notre liste
# track : la musique dont il faut récupéré les genres
# Renvoie True si la récupération à réussi
def get_genre_of_track(track : tidalapi.Track,track_url : str,header : str, Console = True, DEV = False) -> bool:
    genres = []
    url = f"{track_url}{track.id}?include=genres"
    resp = rq.get(url,headers=header,timeout=30)
    if resp.status_code != 200:
        if resp.status_code !=404:
            raise RuntimeError(f"get_genre_of_track -> Problème avec la demande API (track : {track.id}) (status_code : {resp.status_code})\n{resp.json()}")
        else:
            print(f"Info : Le titre ({track.id} : {track.name} - {track.artist.name}) n'a visiblement pas de genre") if Console else None
    else:
        datas = resp.json()["included"]
        for i in range (len(datas)):
            try:
                genres.append(datas[i]["attributes"]["genreName"])
            except Exception as e:
                print(f"TrackAndGenre : _get_genre_of_track -> Problème lors de la récupération du genre de la piste : {track.name} - {track.artist.name}")
                print(e) if DEV else None
    return genres

# Fonction qui permet de décider d'un nom à partir d'une liste de musique (tidalapi.Track)
# NameType = 
# - 0 -> Générer à partir des genres
# - 1 -> Générer à partir des artistes
def generateName(l : list[tidalapi.Track],NameType : int, track_url : str,header : str, Console = True, DEV = False):
    name = ""
    emptyName = ["Playlist vide", "Playlist du néant", "Playlist du vide", "Playlist fantôme", "Playlist en apesanteur", "Playlist zéro son", "Playlist du silence", "Playlist paumée", "Playlist orpheline", "Playlist désertée", "Playlist 404", "Playlist mystère", "Playlist sans âme", "Playlist qui attend", "Playlist en jachère", "Playlist oubliée", "Playlist coquille vide", "Playlist creuse", "Playlist en sommeil", "Playlist muette"]
    if len(l)==0:
        name = randchoose(emptyName)
    else:
        if NameType == 0: #==================================================  Genre
            genreFinal=[]
            genresD = {}
            genresL = []
            for track in l:                                                     # Set le nombre d'apparition
                print(f"Récupération des genres de {track.name} - {track.artist.name}") if Console else None
                TrackGenre = get_genre_of_track(track,track_url,header,Console,DEV)
                for g in TrackGenre:
                    if g in genresL:
                        genresD[g] = genresD[g]+1
                    else:
                        genresL.append(g)
                        genresD[g] = 1
            for i in range (min(randint(1,5),len(genresL))): # Vérif min ?
                max=0
                Gmax = None
                for g in genresD.keys():
                    if g in genresL and genresD[g]>max:
                        max = genresD[g]
                        Gmax = g
                genreFinal.append(Gmax)
                genresL.remove(Gmax)
            for e in genreFinal:
                name += f"{e}, "
            name = name[:-2]
        elif NameType == 1: #================================================ Artistes
            artFinal=[]
            artD = {}
            artL = []
            for track in l:                    # Set le nombre d'apparition
                artistes = track.artists
                for a in artistes:
                    if a.name in artL:
                        artD[a.name] = artD[a.name]+1
                    else:
                        artL.append(a.name)
                        artD[a.name] = 1
            for i in range (min(5,len(artL))): # Vérif max ?
                max=0
                Amax = None
                for a in artD.keys():
                    if a in artL and artD[a]>max:
                        max = artD[a]
                        Amax = a
                artFinal.append(Amax)
                artL.remove(Amax)
            for e in artFinal:
                name += f"{e}({artD[e] if DEV else None}), "
            name = name[:-2]
    return name
import os
import tidalapi
import Coherence

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
    itemType = None
    print("====================")
    print(message) # Message de devanture de liste
    print("====================")
    accepted=[tidalapi.Track,tidalapi.playlist.Playlist,tidalapi.playlist.UserPlaylist,tidalapi.artist,int,str,list]
    itemType = type(l[0])
    if not (itemType in accepted):
        raise(TypeError(f"utils.choice : le type {itemType} n'est pas pris en charge !({accepted})"))
    for i in range(len(l)):
        e = l[i] # Element qu'on regarde
        print("     ",end="") if tab else None
        print(f"{i} - ",end="") if index else print("- ",end="")
        if type(e)!=itemType:
            raise(TypeError(f"Un élément de la liste à un type étrange (Ne correspond pas au reste : {type(e)} ==> {itemType})"))
        if itemType == tidalapi.Track: # Cas Track
            print(f"{e.full_name} - {e.artist.name}")
        elif itemType == tidalapi.playlist.Playlist or itemType == tidalapi.playlist.UserPlaylist: # Cas Playlist
            if short: # Affichage COURT des playlists : Nom sans les titres
                print(f"{e.name} - {e.num_tracks}")
            else: # Affichage LONG des playlists : Avec les titres
                affichePlaylist(e,f"{e.name} - {e.num_tracks}",True,False)
        elif itemType == tidalapi.artist.Artist: # Cas Artist
            print(f"{e.name}")
        else:
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
        print("===============")
        afficheListe(L[i],f"Selection {i} : ")
        print("===============\n")

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
def choice(l: list, message : str = "Liste d'éléments à choisir", maxItems : int = -1, OriginalItems : bool = False, default : any | None = None, short : bool = False) -> (list | list[int]):
    itemType = None
    if len(l)==0 or maxItems==0:
        return []
    accepted=[tidalapi.Track,tidalapi.playlist.Playlist,tidalapi.playlist.UserPlaylist,tidalapi.artist,int,str,list]
    itemType = type(l[0])
    if not (itemType in accepted):
        raise(TypeError(f"utils.choice : le type {itemType} n'est pas pris en charge !({accepted})"))
    choosed : list[int] = []
    saisie=None
    while((saisie!='N' and saisie!='S' and saisie != 'X' and saisie !='') and (maxItems==-1 or (maxItems>=0 and maxItems>len(choosed)))):
        clear()
        print(message,"\n")
        afficheListe(l,message,False,True,short) # On affiche les éléments qui PEUVENT être SELECTIONNER
        if len(choosed)>0: # On affiche les éléments déjà SELECTIONNER
            print("\nElements séléctionner :\n")
            for e in choosed:
                print(f"- {e}")
        print("\nVeuillez choisir les éléments que vous souhaitez séléctionner !")
        print("Format accepté : ")
        print("- numero_item (Permet d'ajouter UN élément à la selection)")
        print("- numero_item,numero_item... (Permert d'ajouter une liste d'éléments à la selection)")
        print("- 'N' | 'S' | 'X' | '' (Permet de terminer la saisie ) /!\\ NE PAS METTRE LES ' /!\\")
        saisie = input("\nVotre saisie : ")
        saisie.upper()
        for e in saisie.split(','):
            is_number=True
            try:
                e = int(e.strip())
            except:
                is_number=False # On a pas saisie un nombre ?
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

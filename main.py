# Project import
from utils import *
from playFunctions import *
from TrackAndGenre import TrackAndGenre
from Coherence import Coherence
from gestionCoherence import GestionCoherence

# Library import
from pathlib import Path
from random import shuffle
import tidalapi
from tidalapi import Quality
import requests
import logging
import json

DEV : bool = True                                           # Affichage Dev
TIDALAPI = {'clientid' : "", 'clientsecret' : ""}           # Identifiants Tidal API (https://developer.tidal.com/) [DECLARATION UNIQUEMENT]
TIDAL_API_URL = "https://openapi.tidal.com/v2"              # URL pour les requests à l'API v2 de tidal (Utiliser notemment pour le genre)
BYPASS_API = True                                           # Evite l'obligation de configurer les infos api (CLIENT ID & CLIENT SECRET) 
# Identifiants TIDALAPI Inutile ?

data = {'playlists' : [], 'typeSort' : -1, 'AfficheConsole' : True, 'typeGenreSort' : -1, 'genresList' : [], 'coherence' : Coherence.MOYEN.value}

#======================================================================================================
#==================================================================================FONCTION A DEPLACER
#======================================================================================================



#======================================================================================================
#==================================================================================LOGIN
#======================================================================================================
clear()

userPath = Path(__file__).parent / Path("userData")

# Fichier des données utilisateur
if not Path(userPath).exists():
    Path(userPath).mkdir()

# logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)

#======================================================================================================
# Gestion de la session (Connexion du compte utilisateur)

session_file = Path(userPath / "tidal-session-oauthn.json")
config = tidalapi.Config()

# Gestion du fichier API
if not BYPASS_API:
    if not Path(userPath / 'api_data.json').is_file():
        f = open(userPath / 'api_data.json','w')
        json.dump(TIDALAPI,f,indent=4)
        f.close()
    else:
        f = open(userPath / 'api_data.json','r')
        TIDALAPI=json.load(f)
        try:                                                # Si les identifants API sont fournis dans api_data.json on les appliques
            config.client_id = TIDALAPI['clientid']
            config.client_secret = TIDALAPI['clientsecret']
        except:                                             # Sinon on ne fais rien
            print("Fichier Mal encodé !! Réécriture propre et VIDE !")
            json.dump(TIDALAPI,f,indent=4)
        f.close()

    if (TIDALAPI['clientid']=="" or TIDALAPI['clientsecret']=="") and DEV: # AFFICHAGE EN MODE DEV UNIQUEMENT
        print("ATTENTION ! PAS D'IDENTIFANTS API")
    elif DEV:                                                      # AFFICHAGE EN MODE DEV UNIQUEMENT
        print("IDENTIFANTS API FOURNI MAIS PAS VERIFIER")

session = tidalapi.Session(config)                                          # Creation de la session
try:
    session.login_session_file(session_file)
except Exception as e:
    os.remove(session_file)
    print("Un problème est survenue lors du load des anciens paramètres")
    print("Fichier config supprimé, veuillez relancer et vous reconnecter")
    print(f"Erreur : {e}") if DEV else None
    exit()
session.save_session_to_file(userPath / "tidal-session-oauthn.json")

if session.check_login():                                                   # Verification qu'on est bien connecté
    print("Vous êtes connecté !")
    print(f"Username : {session.user.username}")
    print(f"First name : {session.user.first_name}")
    print(f"Last name : {session.user.last_name}")
else:
    print("Erreur lors de la connexion ! Veuillez relancer !")
    exit()

#======================================================================================================

#======================================================================================================
#==================================================================================TESTS

"""
Go do somes tests :)
"""

#======================================================================================================

#======================================================================================================
#================================================================================== CHOIX
#======================================================================================================


session.audio_quality = Quality.hi_res_lossless
playlists : list[tidalapi.Playlist] = session.user.playlists()
dataPath : Path = userPath / "lastSession.json"
toSort : list[tidalapi.Playlist] = []
useLast : bool = False
Console : bool = data["AfficheConsole"]
calculatedPlaylist = []                 # Liste regroupant toutes les playlists calculé
unrated = []                            # Liste regroupant les titres qui ont posé problème
LittePlaylist = []                      # Liste regroupant les titres des playlists trop petites
if Path(dataPath).is_file():
    f = open(dataPath,"r")
    data = json.load(f)
    f.close()
    savedPlaylists = []
    IHaveAnError = False
    for e in data['playlists']:
        try:
            savedPlaylists.append(tidalapi.Playlist(session,e))
        except:
            IHaveAnError = True
            print("Données OUTDATED !")
    while True and not IHaveAnError:
        print("===============================")
        print("Données de dernières session :\n")
        affiche_data(data,savedPlaylists)
        print("\n===============================\n")
        saisie = input("Voulez-vous utiliser les données de dernière session ? O/N ou Y/N : ")
        if saisie.lower() in ['o','y','n']:
            useLast = saisie.lower()=='o' or saisie.lower() == 'y'
            toSort=savedPlaylists if useLast else []
            clear()
            break
        else:
            clear()
            print("Mauvaise saisie !")

if not useLast:                                                     # On demande des choix tout neufs
    toSort = choice(playlists,"Liste de vos playlists (Choisissez lesquels trier) : ",-1,True,None,True)
    clear()
    afficheListe(toSort,"Voici les playlist qui vont être triées :" )

    while True:
        print("===============================")
        print("Veuillez choisir une méthode de tri : ")
        printSortType()
        print("X : Quitter")
        print("===============================")
        saisie = input("Votre choix : ")
        if saisie in ['1','2','3']:
            sort = int(saisie)
            saisie = input("Vous avez choisi la méthode de tri n°"+saisie+" ! Veuillez confirmer -> Entrer pour continuer ou 'N' pour changer de méthode : ")
            if saisie.lower()!='n':
                break
            else:
                clear()
        elif saisie.lower()=='x':
            print("Au revoir !")
            exit()
        else:
            clear()
            print("Mauvaise entrée. Veuillez entrer 1, 2 ou 3.")

    clear()
    while True:
        print("===============================")
        print("Voulez-vous afficher les étapes du tri dans la console ? (O/N ou Y/N)")
        print("===============================")
        saisie = input("Votre choix (Appuyer sur Entrer sera compté comme O) : ")
        if saisie.lower() in ['o','n','y','']:
            Console = saisie.lower()=='o' or saisie.lower()=='y' or saisie == ''
            break
        else:
            clear()
            print("Mauvaise entrée. Veuillez entrer O ou N.")

    clear()
    while True:
        print("===============================")
        print("Choissiez la cohérences des playlists qui seront créé : ")
        print("1 : FAIBLE (Playlists plus grandes)")
        print("2 : MOYENNE (Playlists de taille modéré, peut contenir des incohérences)")
        print("3 : FORT (Playlists plus petites, cohérence maximale)")
        print("===============================")
        saisie = input("Votre choix (Appuyer sur Entrer prendra MOYENNE) : ")
        match saisie:
            case '1':
                data["coherence"] = Coherence.FAIBLE.value
                break
            case '2':
                data["coherence"] = Coherence.MOYEN.value
                break
            case '3':
                data["coherence"] = Coherence.FORT.value
                break
            case '':
                data["coherence"] = Coherence.MOYEN.value
                break
            case _:
                clear()
                print("Saisie incorrect !")
            
#======================================================================================================
#==================================== RAPPEL DES CHOIX ================================================

clear()

if useLast:
    Console = data["AfficheConsole"]
    sort = data["typeSort"]
else:
    tmp = []
    for e in toSort:
        tmp.append(e.id)
    data["playlists"]=tmp
    data["AfficheConsole"]=Console
    data["typeSort"]=sort
    data["typeGenreSort"] = -1
    data["genresList"] = []
    f = open(dataPath,"w")
    json.dump(data,f,indent=4)
    f.close()
coherence = GestionCoherence(userPath,Coherence(data["coherence"]),DEV)


print("===============================")
print("Rappel :")

affiche_data(data,toSort)

print("\n===============================")
if input("Appuyer sur Entrer pour continuer, n'importe quel touche pour sortir ") != "":
    print("Au revoir !")
    exit()

calculatedPlaylist : list[tidalapi.Track] = None

#======================================================================================================

#======================================================================================================
#==================================== CAS TRI 1 OU 2 ==================================================

if sort==1 or sort==2:
    print("Vous avez choisi la méthode de tri par mix de chaque piste !")
    MyPlaylists =[]
    for p in toSort:                                                        # Boucle de récupération des mix intersection
        
        myTracks = p.tracks()                                               # Récupération des pistes
        prob=[]
        listOfList = []
        
        print(f"\nTri de la playlist {p.name} en cours...")

        listOfList = recuperationMixOfPlaylists(myTracks,prob,Console)      # Récupération des mix

        listOfList = MergeMixByIntersect(listOfList)                        # Vérification de l'existance des titre dans les autres mix 

        for l in listOfList:
            MyPlaylists.append(l)
        
        for e in prob:                                                      # Playlist des titres qui ont eu un problème à la récupération des mix
            unrated.append(e)

    print("")
    unuszed = []
    if saisie=='2':
        abso = coherence.getAbsorbtion()
        calculatedPlaylist = MegePlaylistByIntersect(MyPlaylists,unuszed,coherence.getintersectionMinimal(),abso[0],abso[1],Console)
    else:
        calculatedPlaylist = MyPlaylists
    listMin = coherence.getlisteMinimal()
    



    # =============================================================================================== ENVOIE DES PLAYLISTS PROBLEMATIQUES DANS UNE PLAYLIST A PART
    for l in unuszed:                                                                               # Gestion des playlists non traitées
        appendList(LittePlaylist,l,True)

    appendList(LittePlaylist,removeToLittle(calculatedPlaylist,listMin),True)                                 # Envoie des playlists trop petite dans LittlePlaylist

    supprDuplicatedPlaylist(calculatedPlaylist)                                                          # Suppression des duplicata

#======================================================================================================

elif sort == 3:
    # TIDALAPI = {'clientid' : "", 'clientsecret' : ""} RAPPEL STRUCTURE
    if (TIDALAPI['clientid'] =="" or TIDALAPI['clientsecret']=="") and not BYPASS_API:      # Gestion Identifiants API /!\ USELESS /!\
        clear()
        print("Information d'API non renseigné !")
        print("Il est nécessaire d'avoir des indentifiants TIDAL API pour utiliser le tri par genre !")
        while True:
            saisie = input("Voulez-vous les entrée maintenant ? (Y/N ou O/N) (H pour aide)")
            clear()
            if saisie.lower() in ['y','o','n','h']:
                match saisie.lower():
                    case 'y' | 'o':
                        break
                    case 'n':
                        print("Au revoir !")
                        exit()
                    case 'h':
                        print("Vous pouvez vous créer un compte TIDAL API à cet adresse : https://developer.tidal.com/")
                        print("Il est nécessaire de créer un projet afin d'obtenir des identifants")
                        print("Les identifants API son : ")
                        print("CLIENT ID\n et \nCLIENT SECRET")
                        print("Comment les mettre dans cette application : ")
                        print("- En répondant aux demandes dans le terminal")
                        print("- En modifiant directement le fichier ./userData/api_data.json")
        tmp=0
        while tmp<2:
            if TIDALAPI['clientid'] =="":
                id = input("Veuillez saisir votre CLIENT ID : \n-> ")
            if TIDALAPI['clientsecret']=="":
                secret = input("Veuillez saisir votre CLIENT SECRET : \n-> ")
            clear()
            if id!="":
                TIDALAPI['clientid']=id
                tmp+=1
            else:
                print("CLIENT ID mal entré !")
            if secret!="":
                TIDALAPI['clientsecret']=secret
                tmp+=1
            else:
                print("CLIENT SECRET mal entré !")
        clear()
        f = open(userPath / 'api_data.json','w')
        json.dump(TIDALAPI,f,indent=4)
        f.close()
        print("Veuillez relancer le programme afin que vos paramètres soient pris en compte")
        exit()
    else:                                                                           # API GERE OU BYPASS
        clear()
        header = {"Authorization": f"Bearer {session.access_token}","Content-Type": "application/vnd.api+json",} # Header pour les demandes API
        # Test de la validité de l'api :
        print("TEST DE L'API") if DEV else None
        track_url = f"{TIDAL_API_URL}/tracks/"
        url = f"{TIDAL_API_URL}/userCollectionPlaylists/me"
        if (requests.get(url, headers=header, timeout=30).status_code) != 200:          # Vérification de l'API avec une requests bidon
            print("Problème de récupération d'information avec l'API (Vérifier vos identifiants et authorisations)")
            exit()
        else:
            all_tracks = []
            print("API OK") if DEV else None
        for p in toSort:                            # Boucle pour chaque Playlists à gérer
            print(f"\nRécupération des pistes de : {p.name}")
            appendList(all_tracks,p.tracks(),True)
            print("\n")
        MyPlaylist = TrackAndGenre(track_url,header,Console=Console,DEV=DEV)
        MyPlaylist.set_tracks_without_playlists(all_tracks)
        MyPlaylist.load_all_genres(unrated)
        all_genres = MyPlaylist.get_all_genres()
        genreList = [[]]
        # ===========================================================================
        # ========================= CHOIX AUTO/MANUEL ===============================
        clear()
        if useLast and data["typeGenreSort"] != -1:
            print("===============================")
            print("Utilisation des anciens paramètres !")
            print("===============================")
            genreList = data["genreList"]
            affiche_genre_selection(genreList,"Listes des selections : ")
            saisie = input("Appuyer sur X pour quitter, n'importe quel autre saisie pour continuer : ")
            if saisie.lower() == 'x':
                print("Au revoir")
                exit()
        else:
            while True:
                print("=====================================")
                print("2 types de tri sont proposé : ")
                print("===============")
                print("1 : Tri automatique, ici vous choisissez un niveau de cohérence.[W.I.P.]")
                print("     Celui-ci déterminera le nombre de genre que des pistes doivent avoir en commun afin d'être dans la même playlist")
                print("===============")
                print("2 : Tri manuel, ici on vous proposera une liste de genres.")
                print("     Vous composerez un 'menu', c'est-à-dire une liste de genre afin de composer une playlist")
                print("===============")
                print("X : Quitter")
                print("=====================================")
                saisie = input("\nVotre Choix : ")
                if saisie == '1' or saisie == '2':
                    data['typeGenreSort'] = int(saisie)
                    break
                elif saisie.lower() == 'x':
                    print("Au revoir !")
                    exit()
                else:
                    clear()
                    print("Saisie incorrect ! ")
                    print(saisie) if DEV else None
            clear()
            nextStep = False
            while True:
                if data['typeGenreSort'] == 1:                                  # Tri automatique
                    print("Non implémenté -> W.I.P.")
                    exit()
                elif data['typeGenreSort']==2:                                  # Tri manuel
                    if not nextStep:
                        print("=====================================")
                        afficheListe(all_genres,"Liste des genres : ")
                        if len(genreList[0])>0:
                            print("===============")
                            affiche_genre_selection(genreList)
                            print("===============")
                            print(f"\nVotre selection actuel : ")
                            afficheListe(genreList[len(genreList)-1],"Genres :")
                            print("===============")
                        print("\nVeuillez choisir un genre a ajouter à votre selection actuel (N/S pour passer à l'étape suivante)")
                        print("=====================================")
                        saisie = input("Votre choix : ")
                        try:
                            if saisie.lower() != "n" and saisie.lower() != 's':
                                choice = all_genres[int(saisie)]
                                if not choice in genreList[len(genreList)-1]: 
                                    genreList[len(genreList)-1].append(choice)
                                clear()
                            else:
                                nextStep = True
                        except Exception as e:
                            clear()
                            print("Entrée incorrect !")
                            print(f"Saisie : {saisie}") if DEV else None
                            print(f"Erreur : {e}") if DEV else None
                            nextStep = False
                    if nextStep:                                                # Demande de fin de selection
                        clear()
                        print("RAPPEL : ")
                        print("===============")
                        affiche_genre_selection(genreList)
                        print("===============")
                        print(f"\nVotre selection actuel : ")
                        afficheListe(genreList[len(genreList)-1],"Genres :")
                        print("===============")
                        print("\nQue voulez vous faire ?")
                        print("A - Ajouter un genre à votre selection actuelle")
                        print("S/N - Passer à une nouvelle selection")
                        print("X - Terminer la selection et passer à la phase de tri")
                        saisie = input("\nVotre Choix : ")
                        saisie = saisie.lower()
                        if saisie == 'a':
                            clear()
                            nextStep = False
                        elif saisie == 's' or saisie == 'n':
                            clear()
                            genreList.append([])
                            nextStep = False
                        elif saisie == 'x':
                            clear()
                            break
                        else:
                            clear()
                            print("Saisie incorrect !")
                else:
                    # FAILSAFE
                    print(f"Valeur de typeGenreSort incohérente ! {data['typeGenreSort']}")
            data['genreList'] = genreList
            f = open(dataPath,'w')                                                              # Sauvegarde des nouveaux settings
            json.dump(data,f,indent=4)
            f.close()
        # ===========================================================================
        # ============================= TRI PAR GENRE ===============================
        for l in genreList:
            calculatedPlaylist.append(MyPlaylist.get_tracks_of_genres(l,coherence.getNbrGenres()))
        # ===========================================================================


# ===========================================================================
# ============================= GESTION PLAYLIST ============================
Tmax=0
clear()
deleteEmptyPlaylist(calculatedPlaylist)                             # Supprime les playlists vides
print("=====================================")
print("Size of calculatedPlaylist : ",len(calculatedPlaylist),"\n")
for i in range(len(calculatedPlaylist)):
    if len(calculatedPlaylist[i])==0:
        print(f"\nPlaylist {i} vide")
    else:
        afficheListe(calculatedPlaylist[i],f"Playlist numéro {i}, Taille : {len(calculatedPlaylist[i])}",index=False)
        if len(calculatedPlaylist[i])>Tmax: # Gestion des infos ! 
            Tmax = len(calculatedPlaylist[i])
print("\n===============")
print("Nombre de playlists différentes : ",len(calculatedPlaylist))
print("Taille de la plus grande playlist : ",Tmax)
if len(calculatedPlaylist)==0:
    print("Cause possible de Playlists vides : ")
    print(f"     - Condition trop exigentes (ex : +5 genres par selections et coherence en {coherence.getCoherence().name})")
    print("     - Pas assez de titre dans les playlists en entrée")
print("===============")
print("")
print("=====================================")
print(f"Voici les pistes qui n'ont pas pu être traitées (size : {len(unrated)}) : ")
print("===============")
for e in unrated:
    print(e.name,e.artist.name)
print("")
print("=====================================")
print(f"Voici le merge des playlists non traitées (size : {len(LittePlaylist)}) : ")
print("===============")
for e in LittePlaylist:
    print(e.name,e.artist.name)
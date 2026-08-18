import tidalapi
import playFunctions
import utils
import requests

class TrackAndGenre():
    
    # track_url : url de l'api TIDAL pour les tracks
    # header : infos à envoyer à l'api, notamment l'authentification
    # playlist : une playlist
    # Console : Les retours console de la classe
    # DEV : Les retours console pour DEV de la classe
    # timeout : temps avant qu'on considère le serveur comme injoinagble lorsqu'on fais une request
    def __init__(self, track_url : str ,header : str, playlist : tidalapi.playlist = None,Console : bool = True, DEV : bool = False, timeout : int = 30):
        self._playlist : tidalapi.playlist = playlist
        self._track_url : str = track_url
        self._header : str = header
        self._Console : bool = Console
        self._tracks_and_genre : dict[tidalapi.Track,list[str]] = {}
        self._timeout : int = timeout
        self._DEV : bool = DEV
        if playlist != None:
            self.load_tracks(playlist)
            self.load_all_genres()
    
    # Permet de mettre des titres sans passer par une playlist
    def set_tracks_without_playlists(self,tracks : tidalapi.Track):
        self._tracks_and_genre.clear()
        for track in tracks:
            self._tracks_and_genre[track] = []
    
    # Renvoie la liste de tout les titres
    def get_tracks(self) -> list[tidalapi.Track]:
        res = []
        for track in self._tracks_and_genre.keys():
            res.append(track)
        return res
    
    # Permet de set une playlist
    def setPlaylist(self,playlist : tidalapi.playlist) -> None:
        if isinstance(playlist,(tidalapi.playlist.Playlist)): # Fonction de vérification de type
            self._playlist = playlist
            self._tracks_and_genre.clear()
        else:
            raise ValueError(f"TrackAndGenre : setPlaylist -> Le type de playlist doit être tidalapi.playlist. Type : {type(playlist)}")
    
    # Permet de récupérer la playlist
    def getPlaylist(self) -> tidalapi.playlist:
        return self._playlist
    
    def getConsole(self) -> bool:
        return self._Console
    
    def setConsole(self,Console : bool) -> None:
        if Console != True or Console != False:
            raise ValueError("L'argument Console doit être un bool !")
        else:
            self._Console = Console
    
    def getDEV(self) -> bool:
        return self._DEV
    
    def setDEV(self,DEV : bool) -> None:
        if DEV != True or DEV != False:
            raise ValueError("L'argument DEV doit être un bool !")
        else:
            self._DEV = DEV
    
    # Fonction qui load les tracks d'une playlist dans la classe
    def load_tracks(self,p : tidalapi.playlist) -> None:
        try:
            self.setPlaylist(p)
            self._tracks_and_genre = {}
            tmp = p.tracks()
            for t in tmp:
                self._tracks_and_genre[t] = []
        except Exception as e:
            print(f"TrackAndGenre : load_tracks -> Problème de récupération des tracks\n{e}")

    # Fonction qui récupére les genres d'une piste
    # Ajout la piste à notre liste
    # track : la musique dont il faut récupéré les genres
    # Renvoie True si la récupération à réussi
    def _get_genre_of_track(self,track : tidalapi.Track) -> bool:
        success = True
        genres = []
        url = f"{self._track_url}{track.id}?include=genres"
        resp = requests.get(url,headers=self._header,timeout=self._timeout)
        if resp.status_code != 200:
            if resp.status_code !=404:
                raise RuntimeError(f"TrackAndGenre : _get_genre_of_track -> Problème avec la demande API (track : {track.id}) (status_code : {resp.status_code})\n{resp.json()}")
            else:
                print(f"Info : Le titre ({track.id} : {track.name} - {track.artist.name}) n'a visiblement pas de genre") if self._Console else None
                success = False
        else:
            datas = resp.json()["included"]
            for i in range (len(datas)):
                try:
                    genres.append(datas[i]["attributes"]["genreName"])
                except Exception as e:
                    print(f"TrackAndGenre : _get_genre_of_track -> Problème lors de la récupération du genre de la piste : {track.name} - {track.artist.name}")
                    print(e) if self._DEV else None
                    success = False
        self._tracks_and_genre[track] = genres
        return success
    
    # Fonction qui renvoie le genre d'une piste
    # Renvoie une liste de genres
    def get_genre_of_track(self,track : tidalapi.Track) -> list[str]:
        res = []
        if track in self._tracks_and_genre:
            if self._tracks_and_genre[track] is None:
                self._get_genre_of_track(track)
            res = self._tracks_and_genre[track]
        else:
            raise(ValueError("TrackAndGenre : get_genre_of_track -> Le genre de la track demandé n'existe pas dans l'objet !"))
        return res

    # Fonction qui récupère les genres de nos tracks
    # prob : liste des tracks qui n'ont pas pu être traité [PARAMETRE I/O] ! PAS DE RECUPERATION SI VIDE
    def load_all_genres(self, prob : list[tidalapi.Track] = []) -> None:
        i = 0
        print("Récupération des genres des musiques :") if self._Console else None
        for track in self._tracks_and_genre.keys():
            print(f"{i} : Traitement de la piste : {track.name} - {track.artist.name}") if self._Console else None
            if not self._get_genre_of_track(track):
                prob.append(track)
            i+=1
    
    # Affiche le titre et les genres d'une piste
    def affiche_genre_of_track(self,track) -> None:
        print("===============")
        print(f"Genres du titre : {track.name} - {track.artist.name}")
        if len(self._tracks_and_genre[track])>0:
            for e in self._tracks_and_genre[track]:
                print(e)
        else:
            print("Pas de genre...")
        print("===============\n")
    
    # Renvoie la liste des genres de la playlist
    def get_all_genres(self) -> list[str]:
        res = []
        for genres in self._tracks_and_genre.values():
            utils.appendList(res,genres)
        if len(res)==0 and len(self._tracks_and_genre) > 1:         # On avait pas load les genres...
            self.load_all_genres()
            if len(self._tracks_and_genre.values())>0 and len(self._tracks_and_genre.values()[0])>0: # Il y a bien des genres ? Faut pas tourner à l'infini !
                res = self.get_all_genres()
        return res
    
    # Fonction pour récupérer les pistes qui sont du genre "genre"
    def get_tracks_of_genre(self,genre : str) -> list[tidalapi.Track]:
        res = []
        for track,genres in self._tracks_and_genre.items():
            if genre in genres:
                res.append(track)
        return res
    
    # Fonction qui renvoie la liste des pistes en fonction de leurs genres
    # genres : la liste des genres demandé
    # NbGenreSim : paramètre donnant le nombre de genre en commun que l'on souhaite
    def get_tracks_of_genres(self,genres : list[str], NbGenreSim : int = 1) -> list[tidalapi.Track]:
        res = []
        for genre in genres:
            utils.appendList(res,self.get_tracks_of_genre(genre),True)
        if NbGenreSim>len(genres):
            print(f"AHHH {NbGenreSim} - {len(genres)}")
            NbGenreSim = len(genres)
            print(f"BB {NbGenreSim}")
        toDel = []
        for i in range(len(res)-1,0,-1):                                                   # Dans le cas ou on a NbGenreSim=-1, on supprime tout les titres qui n'ont pas tout les genres
            if ((len(genres)>=NbGenreSim) and (len(utils.Intersection(genres,self._tracks_and_genre[res[i]])) < NbGenreSim)) or (NbGenreSim==-1 and utils.Include(genres,self._tracks_and_genre[res[i]])):
                toDel.append(i)
        for i in toDel:
            res.pop(i)
        return res
    
    # Fonction qui renvoie touts le genres ainsi que leurs nombre d'apparition dans la playlist
    def get_total_genres(self):
        genres = {}
        for g in self.get_all_genres():
            genres[g] = 0
        for gl in self._tracks_and_genre.values():
            for g in gl:
                genres[g] +=1
        return genres
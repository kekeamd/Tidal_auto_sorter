import tidalapi
import playFunctions
import utils
import requests

class TrackAndGenre():
    
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
        return track
    
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
        else:
            datas = resp.json()["included"]
            for i in range (len(datas)):
                try:
                    genres.append(datas[i]["attributes"]["genreName"])
                except Exception as e:
                    print(f"TrackAndGenre : _get_genre_of_track -> Problème lors de la récupération du genre de la piste : {track.name} - {track.artists}")
                    print(e) if self._DEV else None
                    success = False
        self._tracks_and_genre[track] = genres
        return success
    

    # Fonction qui récupère les genres de nos tracks
    def load_all_genres(self) -> None:
        i = 0
        print("Récupération des genres des musiques :") if self._Console else None
        for track in self._tracks_and_genre.keys():
            print(f"{i} : Traitement de la piste : {track.name} - {track.artist.name}") if self._Console else None
            self._get_genre_of_track(track)
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
    # HaveAll : paramètre restrictif, demande la nécessité d'avoir tous les genres fournis
    def get_tracks_of_genres(self,genres : list[str], HaveAll : bool = False) -> list[tidalapi.Track]:
        res = []
        for genre in genres:
            utils.appendList(res,self.get_tracks_of_genre(genre),True)
        if HaveAll:
            for track in res:                                                   # Dans le cas ou on a HaveAll=True, on supprime tout les titres qui n'ont pas tout les genres
                if not (utils.Include(genres,self._tracks_and_genre[track])):
                    res.pop(track)
        return res
    
    
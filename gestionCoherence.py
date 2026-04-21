import json
from Coherence import Coherence
import pathlib
import os

class GestionCoherence:
    
    #   PARAMETRES PAR DEFAUTS, PEUVENT ETRE CHANGER DANS LES FICHIERS ./userdata/coherenceSettings/
    # NbrGenres -> Condition pour le tri par genre : si -1 tous les genres sont obligatoire, sinon prends le nombre de genre
    # Absorbtion[Absrobe & Absorbé] -> Nombre de fois qu'une playlists peut en absorbé une autre ou se faire absorbé
    # intersectionMinimal -> Nombre de musiques en commun nécessaire afin de faire un merge
    # listeMinimal -> Taille de liste minimal accepté
    
    _CorFAIBLE = {'NbrGenres' : 1, 'Absorbtion' : [50,3], 'intersectionMinimal' : 1 , 'listeMinimal' : 5}
    _CorFAIBLE_name = "FAIBLE.json"
    _CorMOYEN = {'NbrGenres' : 2, 'Abso' : [40,2], 'intersectionMinimal' : 2 , 'listeMinimal' : 3}
    _CorMOYEN_name = "MOYEN.json"
    _CorFORT = {'NbrGenres' : -1, 'Abso' : [30,1], 'intersectionMinimal' : 3 , 'listeMinimal' : 1}
    _CorFORT_name = "FORT.json"

    def __init__(self, Path : str | pathlib.Path, coherence : Coherence = None, DEV : bool = False):
        self._path = Path / "coherenceSettings"
        self._DEV = DEV
        self._coherence = None
        self.setCoherence(coherence) if coherence!=None else None

    def getCoherence(self):
        return self._coherence
    
    def setCoherence(self,coherence : Coherence):
        self._coherence = coherence
        try:
            self._load_Coherence()
        except Exception as e:
            print("Problème avec la cohérence, probablement inccorect !")
            print(e)
            self._coherence = None
    
    # Récupère les datas des cohérence à partir des fichiers
    def _load_Coherence(self):
        FAIBLE_PATH = self._path / self._CorFAIBLE_name
        MOYEN_PATH = self._path / self._CorMOYEN_name
        FORT_PATH = self._path / self._CorFORT_name
        if not self._path.exists():                 # Notre dossier existe
            os.mkdir(self._path)
        pathList = [FAIBLE_PATH,MOYEN_PATH,FORT_PATH]
        for i in range(len(pathList)):
            try:
                f = open(pathList[i],'r')
                match i:
                    case 0:
                        self._CorFAIBLE = json.load(f)
                    case 1:
                        self._CorMOYEN = json.load(f)
                    case 2:
                        self._CorFORT = json.load(f)
                f.close()
            except:
                f = open(pathList[i],'w')
                match i:
                    case 0:
                        json.dump(self._CorFAIBLE,f,indent=4)
                    case 1:
                        json.dump(self._CorMOYEN,f,indent=4)
                    case 2:
                        json.dump(self._CorFORT,f,indent=4)
                f.close()
                print(f"{pathList[i]} non existant ou problématique, je le réécris !") if self._DEV else None
    
    def getData(self):
        match self._coherence:
            case Coherence.FAIBLE:
                return self._CorFAIBLE
            case Coherence.MOYEN:
                return self._CorMOYEN
            case Coherence.FORT:
                return self._CorFORT
            case _ :
                raise ValueError(f"GestionCoherence : getData -> Cohérence illogique ou pas set ! {self._coherence}")
    
    # NbrGenres -> Condition pour le tri par genre : si -1 tous les genres sont obligatoire, sinon prends le nombre de genre
    def getNbrGenres(self):
        return self.getData()["NbrGenres"]
    
    # Absorbtion[Absrobe & Absorbé] -> Nombre de fois qu'une playlists peut en absorbé une autre ou se faire absorbé
    def getAbsorbtion(self):
        return self.getData()["Absorbtion"]
    
    # intersectionMinimal -> Nombre de musiques en commun nécessaire afin de faire un merge
    def getintersectionMinimal(self):
        return self.getData()["intersectionMinimal"]
    
    # listeMinimal -> Taille de liste minimal accepté
    def getlisteMinimal(self):
        return self.getData()["listeMinimal"]
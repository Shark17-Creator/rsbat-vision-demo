# RS-BAT Vision — prototype technique

Maison fictive uniquement. Aucun plan ni identifiant RS-BAT dans ce dépôt.

Ouvrir index.html depuis un hébergement HTTPS. Imprimer le repère à 100 %, puis viser Hiro depuis la caméra du téléphone. QR : ouvre la démo, ne géolocalise pas l’ouvrier. Suivi perdu hors champ. Ce prototype ne sert pas à implanter des ouvrages.

A-Frame 1.6.0 et AR.js 3.4.7 chargés à la demande depuis leurs hébergeurs. Repère Hiro fourni par AR.js (https://github.com/AR-js-org/AR.js). Aucune image caméra transmise par le code applicatif.

Côté Apps Script : bouton authentifié dans le planning, contrôle des droits par planningCheck_, puis lien public vers la démonstration, sans jeton ni données de chantier. Les données métier restent dans Apps Script.

À valider sur téléphones physiques : permissions, détection, stabilité, fermeture caméra, retour après verrouillage. La liaison privée des modèles réels et les repères par zone restent à développer après ce test.

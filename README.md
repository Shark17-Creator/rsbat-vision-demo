# RS-BAT Vision
Visualiseur de mur paramétrable et repère Hiro, hébergé sur GitHub Pages.

## Révision 02 : échelle physique
Le moteur AR.js 3.4.7 est conservé localement dans aframe-ar-rsbat-3.4.7.js.
Modification unique du bundle officiel : ajout de C.size=A.data.size avant C.minConfidence=A.data.minConfidence dans arjs-anchor.init.
Le composant transmet ainsi le côté extérieur du marqueur, en mètres, à ARjs.Anchor puis ArMarkerControls et trackPatternMarkerId.
Source : https://github.com/AR-js-org/AR.js/tree/3.4.7
Aucun multiplicateur compensatoire de géométrie. Les dimensions du mur sont en mètres.
Le carré noir doit être mesuré et renseigné dans le champ dédié ; 14 cm est la valeur initiale estimée.

La feuille imprimée ne contient que le titre, le numéro du repère, Hiro et le QR. La géométrie du marqueur est inchangée.

## Vérification
Tests de transmission des paramètres et de proportions réalisés avec le code réel du composant.
La calibration physique et la stabilité restent à vérifier sur téléphone ; aucun suivi spatial persistant hors repère.
Aucune donnée privée de chantier ni clé API.

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

## Révision 03 : deux repères, transformations rigides
Deux feuilles A (Hiro) et B (Kanji) ; carrés noirs 14 cm à impression 100 %, centres espacés de 60 cm, B à droite de A et même orientation. Dimensions modifiables dans la page.
Kanji est reconstruit à partir de la première orientation du fichier pattern officiel AR.js (16×16, plans BGR), avec le même rapport bordure/motif de 0,5.
Les matrices brutes des deux détecteurs sont converties en poses du même repère A. Le modèle est placé directement dans la scène, sans hériter des échelles ni du double lissage des ancres AR.js.
Le lissage matriciel est désactivé. Positions interpolées et rotations interpolées par quaternion normalisé ; échelle du modèle fixée à 1.
Contrôles : deux détections obligatoires, échelle brute proche de 1, désaccord des origines inférieur à 8 cm et des rotations inférieur à 12 degrés, acquisition sur 8 images, rejet des sauts. Ces seuils sont des paramètres expérimentaux, pas une garantie de précision physique. Image de suivi datant de plus de 180 ms : masque du modèle.
Aucune persistance spatiale lorsque les repères sortent du champ. Tests numériques : `THREE_TEST_MODULE=/chemin/three.cjs node test_tracking.cjs` ou installer Three.js pour le test. Essai physique sur iPhone encore requis.

## Révision 04 : cycle de suivi et diagnostic
La boucle RAF initialise le mur directement quand la scène existe, sans dépendance à loaded ni au tick d'un composant de scène personnalisé. Elle lit l'horodatage réel _updatedAt du contexte AR.js pour ne compter que des images analysées distinctes. Le contexte peut être obtenu directement depuis les contrôleurs de repères. Les états A/B sont affichés séparément, ainsi que les erreurs et l'interruption du traitement (500 ms sans image). Le placement à deux feuilles et les contrôles géométriques restent identiques.
Test d'intégration `THREE_TEST_MODULE=/chemin/three.cjs node test_integration.cjs` : boucle de l'application extraite telle quelle, sans événement loaded, acquisition, perte/reprise, arrêt et image périmée. Caméra/détection réelles non validées dans le navigateur cloud sans WebGL.

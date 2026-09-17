# Cadrage — Dashboard YouTube Trending

## Message clé

**Les vidéos qui explosent en vues sont surtout musicales, mais elles engagent
proportionnellement moins leur audience et mettent bien plus de temps à
apparaître en tendance que le reste des vidéos.**

Ce n'est pas juste "voici le dataset YouTube Trending" : c'est une conclusion
actionnable pour quelqu'un qui doit décider quoi publier et quand.

## Audience cible

Une agence marketing digital (ou un créateur) qui prépare le lancement d'une
chaîne YouTube et doit décider : quelle catégorie de contenu viser, et à quoi
s'attendre en termes d'engagement et de délai avant la tendance.

## KPIs (3 maximum)

### 1. Like rate médian — vidéos virales vs reste
- **Vanity** : "le like rate moyen est de X%" pris isolément ne dit rien —
  un chiffre sans point de comparaison ne guide aucune décision.
- **Actionable** : comparé au reste des vidéos, il révèle que la viralité en
  vues n'implique PAS un meilleur engagement relatif. Ça prévient le client
  de confondre "beaucoup de vues" avec "audience engagée", et l'incite à
  suivre le like rate comme indicateur de qualité, pas juste les vues.

### 2. Délai médian avant trending — vidéos virales vs reste
- **Vanity** : "délai moyen de X jours" seul ne dit rien sur la stratégie à
  adopter.
- **Actionable** : le contraste (vidéos virales beaucoup plus lentes à
  apparaître en tendance) aide à calibrer les attentes de calendrier
  éditorial — ne pas s'attendre à un pic immédiat pour un contenu à fort
  potentiel viral.

### 3. Part de la catégorie dominante parmi les vidéos les plus vues
- **Vanity** si présenté seul ("83% sont de la musique") — c'est juste une
  statistique descriptive.
- **Actionable** car comparé à sa part globale dans le dataset (delta), et
  nuancé par le like rate ailleurs dans le dashboard : la catégorie
  dominante en vues n'est pas forcément la plus engageante — la Vue détail
  permet justement de vérifier laquelle l'est.

## Structure prévue

Structure multi-pages (dossier `pages/` de Streamlit), pour montrer l'essentiel
avant le détail plutôt que de tout empiler sur un seul écran :

- **Page 1 — Vue synthèse** (`app.py`) : titre porteur du message clé, puis
  la **zone KPIs** — 3 indicateurs comparant les vidéos "virales" (top 1%
  des vues) vs le reste du dataset, affichés en barres remplies avec delta.
  Vue d'ensemble, sans filtre.
- **Page 2 — Vue détail** (`pages/1_Vue_detail.py`) : la **zone filtres**
  (sidebar — catégorie(s), plage de vues, période, et seuil de viralité
  ajustable) et la **zone détail**, organisée en 3 onglets réactifs aux
  filtres : nuage de points vues/like rate par catégorie, vues médianes ET
  taux de like médian par catégorie (deux graphiques, un par métrique), et
  profil des vidéos virales (donut + comparaisons, repris du notebook
  d'analyse).

Le chargement des données (`data_loader.py`, `@st.cache_data`) est mutualisé
entre les deux pages.

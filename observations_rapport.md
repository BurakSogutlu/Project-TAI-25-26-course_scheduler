# Synthèse des Observations pour le Rapport (Projet INFO-H410)

Ce document rassemble de manière structurée toutes les conclusions tirées de nos expérimentations. Tu peux utiliser ces points directement pour rédiger la section "Analyse et Discussion" de ton rapport.

---

## 1. Constraint Satisfaction Problem (CSP)

### CSP Classique (First Solution)
*   **Avantages :**
    *   **Rapidité sur les instances peu denses :** Jusqu'à 125 cours, l'algorithme est extrêmement rapide (moins de 45 secondes) et trouve des solutions avec **0 backtrack**.
    *   **Efficacité des heuristiques :** C'est le duo `Forward Checking` + `Static Degree` qui permet de guider l'arbre de recherche sans se tromper.
    *   **Qualité initiale :** Comme nous avons détourné l'heuristique `LCV` pour trier les choix par *meilleur soft score*, la toute première solution trouvée est souvent un maximum local excellent (soft score très élevé).
    *   **Garantie :** Les plannings retournés ont systématiquement **0 violation dure**.
*   **Limites :**
    *   **Explosion combinatoire (Scalabilité) :** Dès que la densité de l'instance devient trop forte (ex: 150 cours, 95% de remplissage), les heuristiques ne suffisent plus. Le CSP s'étouffe dans des millions de backtracks et tourne à l'infini.

### CSP Anytime (avec Timeout)
*   **Le concept :** Il trouve la même première solution que le CSP Classique, la sauvegarde, puis force un échec pour explorer le reste de l'arbre en quête d'un meilleur score, jusqu'à ce que le chronomètre l'arrête.
*   **Le Mythe du "Meilleur Score" :** Dans nos graphes, l'Anytime n'a jamais un meilleur score que le First Sol. Pourquoi ? Car trouver une *deuxième* solution valide qui bat la *première solution (déjà triée de manière gloutonne)* prend un temps astronomique sur un arbre gigantesque.
*   **Le vrai avantage (Filet de Sécurité) :** Son utilité réside dans son **Timeout**. Si le CSP classique est lancé sur 150 cours, il fait crasher le système en tournant à l'infini. L'Anytime s'arrêtera proprement au bout de son délai. C'est indispensable pour un logiciel en production.
*   **Le compromis du Timeout :** Nous avons observé que si le Timeout (ex: 30s) est inférieur au temps nécessaire pour trouver la toute première solution (ex: 44s pour l'instance 125), l'Anytime échoue lamentablement en retournant `None`, là où le classique aurait réussi en prenant son temps.

---

## 2. Local Search (Recuit Simulé / Simulated Annealing)

*   **Avantages :**
    *   **Scalabilité exceptionnelle :** C'est le grand vainqueur sur les instances immenses. Il résout l'instance de 150 cours en à peine ~5 secondes.
    *   **Robustesse :** Contrairement au CSP, il ne reste jamais bloqué. Il retourne toujours un planning complet.
*   **Limites :**
    *   **Aucune garantie de validité absolue :** Sur les instances très denses (100+ cours), il a tendance à rester coincé dans des minima locaux. Résultat : il rend un planning très rapidement, mais qui contient quelques violations de contraintes dures (chevauchements).
    *   **Qualité inférieure :** Son Soft Score est systématiquement inférieur à celui du CSP sur les petites et moyennes instances.

---

## 3. Apprentissage par Renforcement (Q-Learning)

*   **Avantages :**
    *   L'agent est capable d'apprendre une politique et de s'améliorer au fil des épisodes sur les petites instances (jusqu'à 30 cours).
*   **Limites Majeures :**
    *   **Espace d'état incontrôlable :** Le problème de planification universitaire a un espace d'état titanesque. Nous avons dû optimiser drastiquement la fonction d'état (passer d'une complexité $O(C^3)$ à $O(C^2)$) juste pour empêcher le programme de s'effondrer sur lui-même.
    *   **Le Biais du Temps d'Exécution :** Sur les graphes, le temps du Q-Learning semble stagner ou diminuer sur les immenses instances. **Ceci est un biais méthodologique forcé.** Pour empêcher l'algorithme de tourner pendant des jours, nous avons artificiellement réduit son nombre d'épisodes d'entraînement (1000 épisodes pour 5 cours... contre seulement 2 épisodes pour 150 cours).
    *   **Conséquence du Biais :** À cause de ce manque d'entraînement sur les grandes instances, l'agent "devine" au hasard, ce qui explique pourquoi ses violations dures explosent et son soft score s'effondre. Le Q-Learning n'est fondamentalement pas adapté à la résolution "from scratch" de gros problèmes combinatoires sans l'aide de Deep Learning (Deep Q-Network).

### Perspectives d'amélioration du Q-Learning (Pour la section "Discussion")
Si le Q-Learning classique (Tabulaire) échoue à construire un planning de A à Z à cause de la malédiction de la dimensionnalité, il pourrait être utilisé de manière **hybride** (ce qui ferait une excellente ouverture pour la fin de ton rapport) :
*   **Comme Hyper-Heuristique (Couplé au Local Search) :** Au lieu de demander à l'agent de placer les cours, on lui donne un planning déjà complet (généré aléatoirement). Ses actions ne seraient plus "Placer le cours X dans la salle Y", mais "Appliquer l'opérateur Swap", "Appliquer l'opérateur Move", ou "Faire un grand saut (Perturbation)". L'agent apprendrait à choisir la meilleure stratégie d'exploration pour le recuit simulé en fonction de la situation.
*   **Comme Heuristique de Choix (Couplé au CSP) :** Au lieu d'utiliser l'heuristique statique MRV ou Degree pour choisir la prochaine variable, l'agent Q-Learning pourrait apprendre quelle variable sélectionner pour maximiser les chances de trouver une solution rapidement sans backtrack.

---

## Conclusion globale à mettre en avant

*   **Petites et Moyennes Instances (< 100 cours) :** Le **CSP** est roi. Il garantit la perfection (0 violation) et un excellent confort (Soft score) en un temps raisonnable.
*   **Grandes Instances Très Denses (> 125 cours) :** Le **Local Search** est le seul viable. Il sacrifie un peu de précision (quelques violations dures) pour garantir une exécution rapide et éviter l'explosion combinatoire.
*   **Q-Learning :** Expérience intéressante académiquement, mais inefficace en pratique pure pour ce type de problème en raison de la malédiction de la dimensionnalité (Curse of Dimensionality).

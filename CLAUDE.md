## CLAUDE.md : 

## Modes de travail

### 1. Mode Plan par défaut
- Entrer en mode plan pour TOUTE tâche non triviale (3+ étapes ou décisions d'architecture)
- Si quelque chose déraille, STOP et replanifier immédiatement — ne pas continuer à foncer
- Utiliser le mode plan aussi pour les étapes de vérification, pas seulement pour construire
- Écrire des specs détaillées en amont pour réduire les ambiguïtés

### 2. Stratégie de sous-agents
- Utiliser des sous-agents généreusement pour garder la fenêtre de contexte principale propre
- Déléguer la recherche, l'exploration et les analyses parallèles aux sous-agents
- Pour les problèmes complexes, mobiliser plus de calcul via les sous-agents
- Une tâche par sous-agent pour une exécution focalisée

### 3. Boucle d'auto-amélioration
- Après TOUTE correction de l'utilisateur : mettre à jour `tasks/lessons.md` avec le pattern identifié
- Écrire des règles pour éviter la même erreur à l'avenir
- Itérer sans relâche sur ces leçons jusqu'à faire baisser le taux d'erreur
- Relire les leçons en début de session pour le projet en cours

### 4. Vérification avant de terminer
- Ne jamais marquer une tâche comme terminée sans prouver que ça fonctionne
- Comparer le comportement avant/après les changements si pertinent
- Se poser la question : "Un développeur senior validerait-il ça ?"
- Lancer les tests, vérifier les logs, démontrer que c'est correct

### 5. Exiger l'élégance (avec mesure)
- Pour les changements non triviaux : marquer une pause et demander "y a-t-il une façon plus élégante ?"
- Si un fix semble bancal : "En sachant tout ce que je sais maintenant, implémenter la solution élégante"
- Ne pas appliquer ça aux corrections simples et évidentes — ne pas sur-ingénier
- Challenger son propre travail avant de le présenter

### 6. Correction de bugs autonome
- Face à un rapport de bug : le corriger directement, sans demander à être guidé
- S'appuyer sur les logs, erreurs et tests en échec — puis les résoudre
- Zéro changement de contexte requis de la part de l'utilisateur
- Corriger les tests CI en échec sans attendre d'instructions

## Gestion des tâches

1. **Planifier d'abord** : Écrire le plan dans `tasks/todo.md` avec des items cochables
2. **Valider le plan** : Vérifier avec l'utilisateur avant de commencer l'implémentation
3. **Suivre l'avancement** : Cocher les items au fur et à mesure
4. **Expliquer les changements** : Résumé de haut niveau à chaque étape
5. **Documenter les résultats** : Ajouter une section bilan dans `tasks/todo.md`
6. **Capturer les leçons** : Mettre à jour `tasks/lessons.md` après chaque correction

## Principes fondamentaux

- **Simplicité avant tout** : Rendre chaque changement aussi simple que possible. Impacter le moins de code possible.
- **Pas de paresse** : Trouver les causes profondes. Pas de fix temporaire. Standards d'un développeur senior.

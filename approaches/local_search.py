import math
import random
import time
from core.problem import CourseScheduleProblem
from core.schedule import Schedule
from core.constraints import ConstraintChecker


def resoudre_hill_climbing(instance_path, iterations=50):
    #Préparation 
    probleme = CourseScheduleProblem.from_json(instance_path)
    verificateur = ConstraintChecker(probleme)
    
    #Solution initiale
    planning_actuel = Schedule(probleme)
    for cours in probleme.courses:
        creneau = random.choice(probleme.timeslots)
        salle = random.choice(probleme.rooms)
        planning_actuel.assign(cours, creneau, salle)

    score_actuel = verificateur.objective(planning_actuel)
    
    print(f"Hill Climbing - Score de départ : {score_actuel:.4f}")

    # amélioration
    for i in range(iterations):
        # On choisit un voisin au hasard (Move ou Swap)
        if random.random() < 0.5:
            c = random.choice(probleme.courses)
            voisin = planning_actuel.move_neighbour(c, random.choice(probleme.timeslots), random.choice(probleme.rooms))
        else:
            c1, c2 = random.sample(probleme.courses, 2)
            voisin = planning_actuel.swap_neighbour(c1, c2)
        
        score_voisin = verificateur.objective(voisin)

        # On n'accepte que le meilleur 
        if score_voisin >= score_actuel:
            planning_actuel = voisin
            score_actuel = score_voisin

    print(f"Hill Climbing - Score final : {score_actuel:.4f}")
    return planning_actuel, score_actuel


def resoudre_local_search(instance_path):
    # chargement et preparation 
    # On récupère les données du problème et l'outil de vérification des contraintes
    probleme = CourseScheduleProblem.from_json(instance_path)
    verificateur = ConstraintChecker(probleme)
    
    # création d'une solution  (Même si elle est mauvaise)
    # On remplit le planning au hasard pour avoir une base 
    planning_actuel = Schedule(probleme)
    for cours in probleme.courses:
        creneau = random.choice(probleme.timeslots)
        salle = random.choice(probleme.rooms)
        planning_actuel.assign(cours, creneau, salle)

   # print("\n PLANNINING INITIALE")
    #planning_actuel.pretty_print()
    score_actuel = verificateur.objective(planning_actuel)
    
    # On garde toujours une trace du meilleur planning trouvé jusqu'ici
    meilleur_planning = planning_actuel.copy()
    meilleur_score = score_actuel

    # parametre Simulated Annealing
    temperature = 10.0      # "L'agitation" initiale pour explorer
    refroidissement = 0.995  # À chaque étape, on diminue l'agitation de 1%
    iterations = 4000       # Nombre d'essais pour s'améliorer

    print(f"Début de la recherche locale et le  Score de départ est  : {score_actuel}")

    # L'amélioration itérative
    for i in range(iterations):
        # probabilité de 50pourcent pour choisir l'action
        if random.random() < 0.5:
            cours_au_hasard = random.choice(probleme.courses)
            nouveau_creneau = random.choice(probleme.timeslots)
            nouvelle_salle = random.choice(probleme.rooms)
            voisin = planning_actuel.move_neighbour(cours_au_hasard, nouveau_creneau, nouvelle_salle)
            type_action = "Move"
        else:
            # On choisit deux cours différents au hasard
            c1, c2 = random.sample(probleme.courses, 2)
            voisin = planning_actuel.swap_neighbour(c1, c2)
            type_action = "Swap"
        score_voisin = verificateur.objective(voisin)
   
        #on vérifie si le changement va etre accepter 
        # Si c'est mieux, on accepte tout de suite !
        # Si c'est moins bon, on peut quand même accepter grâce à la "température" pour eviter d'etre bloquer
     
        diff = score_voisin - score_actuel
        if diff > 0 or (temperature > 0 and random.random() < math.exp(diff / temperature)):
            planning_actuel = voisin
            score_actuel = score_voisin

            # Si c'est le record absolu, on le sauvegarde
            if score_actuel > meilleur_score:
                meilleur_planning = planning_actuel.copy()
               # print("\n meilleur planning actuel")
               # meilleur_planning.pretty_print()
                meilleur_score = score_actuel

        # On refroidit un petit peu
        temperature *= refroidissement

        # Petit message pour suivre l'avancement
        if i % 1000 == 0:
            print(f"Essai {i} : Score actuel = {score_actuel:.2f}")

    return meilleur_planning, meilleur_score

if __name__ == "__main__":
    chemin = "data/medium_instance.json"
    
    # Test Hill Climbing
    start_hc = time.time()
    planning, score_hc = resoudre_hill_climbing(chemin, iterations=1000)
    time_hc = time.time() - start_hc
    
    # Test Simulated Annealing
    start_sa = time.time()
    planning, score_sa = resoudre_local_search(chemin)
    time_sa = time.time() - start_sa
    
    print("\n COMPARISON ")
    print(f"Hill Climbing: Score = {score_hc:.2f}, Time = {time_hc:.2f}s")
    print(f"Simulated Annealing: Score = {score_sa:.2f}, Time = {time_sa:.2f}s")
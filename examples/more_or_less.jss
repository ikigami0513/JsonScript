// Jeu du Plus ou Moins (Guess the Number)

print "--- JEU DU PLUS OU MOINS ---"
print "Je pense à un nombre entre 1 et 100..."

// Génération du nombre mystère
var secret = randint(1, 100)
var attempts = 0

// Boucle infinie
while (1 == 1) {
    var attempts = attempts + 1
    
    // On récupère l'entrée (c'est une string)
    input guess_str "Votre proposition : "
    
    // On convertit en entier (via fonction native ajoutée précédemment)
    var guess = to_int(guess_str)
    
    if (guess == secret) {
        print "🎉 BRAVO ! Trouvé en " + attempts + " coups."
        // C'est ici que le break intervient !
        break
    } else {
        if (guess < secret) {
            print "➡️  C'est PLUS !"
        } else {
            print "⬅️  C'est MOINS !"
        }
    }
}

print "Merci d'avoir joué !"
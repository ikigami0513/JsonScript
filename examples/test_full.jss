// ================================================
//    JSONSCRIPT - ULTIMATE FEATURE TEST
// ================================================

// 1. IMPORTATION DE LIBRAIRIE
// Le compilateur détecte .jss, le compile et l'injecte ici.
import "stdlib/math.jss"

print "--- 1. TEST IMPORT & LOGIQUE ---"
var val1 = 42
var val2 = 15
print "Valeurs : " + val1 + " et " + val2
print "Maximum (via stdlib) : " + max(val1, val2)
print "Est-ce que " + val2 + " est pair ? " + is_even(val2)


print ""
print "--- 2. MATHS AVANCEES & PRIORITES ---"
// Test de la priorité : 10 + (5 * 2) = 20
var calc = 10 + 5 * 2
print "Calcul 10 + 5 * 2 = " + calc

// Utilisation de fonctions natives (sqrt, pow)
var a = 3
var b = 4
// c = racine(a^2 + b^2)
var hyp = sqrt(pow(a, 2) + pow(b, 2))
print "Hypoténuse du triangle (3, 4) = " + hyp


print ""
print "--- 3. BOUCLES & RECURSIVITE ---"
var i = 0
print "Boucle While :"
while (i < 3) {
    print " - Itération " + i
    var i = i + 1
}

// Fonction récursive définie dans le script
func fibonacci(n) {
    if (n <= 1) { return n }
    return fibonacci(n - 1) + fibonacci(n - 2)
}

var fib_target = 6
print "Fibonacci(" + fib_target + ") = " + fibonacci(fib_target)


print ""
print "--- 4. MANIPULATION DE LISTES (STRING SPLIT) ---"
// On simule une liste en découpant une chaîne
var raw_data = "Paris,Londres,New-York,Tokyo"
var cities = split(raw_data, ",")

print "Données brutes : " + raw_data
print "Nombre de villes : " + len(cities)
print "Ville n°2 (index 1) : " + at(cities, 1) // Londres
print "Ville n°4 (index 3) : " + at(cities, 3) // Tokyo


print ""
print "--- 5. PROGRAMMATION ORIENTEE OBJET (POO) ---"

// Classe Parent
class Vehicule(marque) {
    klaxonner() {
        print this.marque + " fait : Tuuut Tuuut !"
    }
}

// Classe Enfant (Héritage)
class VoitureDeSport(marque, vitesse_max) extends Vehicule {
    // Surcharge et utilisation de propriétés spécifiques
    klaxonner() {
        print this.marque + " fait : VROUUUUUM ! (" + this.vitesse_max + " km/h)"
    }
    
    turbo() {
        print "Activation du turbo sur la " + this.marque + " !"
    }
}

var v1 = new Vehicule("Peugeot")
var v2 = new VoitureDeSport("Ferrari", 320)

v1.klaxonner() // Méthode parent
v2.klaxonner() // Méthode enfant surchargée
v2.turbo()     // Méthode enfant spécifique


print ""
print "--- 6. SYSTEME & ENVIRONNEMENT ---"
print "OS Détecté : " + os_name()
print "Heure Système : " + now()
print "Dossier actuel : " + cwd()

print ""
print "=== TEST TERMINE AVEC SUCCES ==="

// stdlib.jss - Bibliothèque Standard

// Retourne le maximum entre a et b
func max(a, b) {
    if (a > b) {
        return a
    }
    return b
}

// Retourne le minimum entre a et b
func min(a, b) {
    if (a < b) {
        return a
    }
    return b
}

// Vérifie si un nombre est pair (renvoie true/false)
func is_even(n) {
    // Le parser gère la priorité : (n % 2) est calculé avant le ==
    return (n % 2) == 0
}

// Vérifie si un nombre est impair
func is_odd(n) {
    return (n % 2) != 0
}

// Calcule la moyenne d'une liste
func average(list) {
    var total = 0
    var size = len(list)
    
    if (size == 0) { return 0 }

    var i = 0
    while (i < size) {
        var val = at(list, i)
        var total = total + val
        var i = i + 1
    }
    
    return total / size
}

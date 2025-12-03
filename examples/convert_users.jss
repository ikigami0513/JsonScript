clear_screen()
print_color("--- CSV CONVERTER TOOL ---", "blue")

var filename = "examples/users.csv"

if (fs_exists(filename) == 0) { // 0 = False en python bool->int parfois, ou False direct
    print_color("Erreur : Fichier introuvable !", "red")
    throw "File not found"
}

print "Lecture de " + filename + "..."
var users = read_csv(filename)

print_color(len(users) + " utilisateurs trouvés.", "green")

// Traitement
var i = 0
while (i < len(users)) {
    var u = at(users, i)
    var old_name = at(u, "name")
    var new_name = upper(old_name)
    
    // On modifie le dict en place (put/set_attr sont similaires sur les dicts)
    put(u, "name", new_name)
    
    print " - Conversion : " + old_name + " -> " + new_name
    var i = i + 1
}

print "Sauvegarde..."
write_csv("users_upper.csv", users)

print_color("Terminé avec succès !", "green")
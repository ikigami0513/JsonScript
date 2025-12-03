print "--- TEST STDLIB AVANCEE ---"

// 1. MANIPULATION DE FICHIERS
var test_dir = "temp_secure_zone"
var secret_file = test_dir + "/secret.txt"

print "Création du dossier..."
fs_mkdir(test_dir)

if (fs_exists(test_dir)) {
    print "✅ Dossier créé."
}

print "Écriture du fichier secret..."
write_file(secret_file, "Ceci est un mot de passe très secret")

// 2. CRYPTOGRAPHIE
print ""
print "--- HASHING & SECURITE ---"

var content = read_file(secret_file)
print "Contenu lu : " + content

var hash = hash_sha256(content)
print "Signature SHA256 : " + hash

var encoded = base64_encode(content)
print "Encodé en Base64 : " + encoded

var decoded = base64_decode(encoded)
if (decoded == content) {
    print "✅ Décodage Base64 réussi."
}

// 3. STRING UTILS
print ""
print "--- ANALYSE DE TEXTE ---"

var email = "  user@example.com  "
var clean_email = trim(email)

print "Email brut : '" + email + "'"
print "Email propre : '" + clean_email + "'"

if (contains(clean_email, "@") == 1) { // 1 pour true
    print "✅ C'est un email valide (contient @)"
}

if (ends_with(clean_email, ".com") == 1) {
    print "✅ C'est un domaine .com"
}

// 4. NETTOYAGE
print ""
print "--- NETTOYAGE ---"
// fs_remove(test_dir) // Décommente pour supprimer le dossier à la fin
print "Fin du test."

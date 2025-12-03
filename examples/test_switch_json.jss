print "--- TEST TO_JSON ---"

var user = {
    "id": 1,
    "name": "Admin",
    "roles": ["read", "write"]
}

// Sérialisation
var json_str = to_json(user)
print "Objet sérialisé : " + json_str


print ""
print "--- TEST SWITCH / CASE ---"

var role = at(at(user, "roles"), 1) // "write"
print "Rôle détecté : " + role

switch (role) {
    case "read":
        print ">> Accès lecture seule."
    case "write":
        print ">> Accès écriture autorisé."
        print ">> (Plus besoin de break !)"
    case "admin":
        print ">> Accès TOTAL."
    default:
        print ">> Accès refusé."
}

print ""
print "--- TEST SWITCH (Calculé) ---"
var x = 10
switch (x + 10) {
    case 10:
        print "C'est 10"
    case 20:
        print "C'est 20 (Correct)"
    default:
        print "Autre"
}

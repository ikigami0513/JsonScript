func test_continue_keyword() {
    print "--- TEST DU MOT-CLÉ CONTINUE ---"
    var count = 0
    
    // NOUVELLE SYNTAXE : for (variable, début, fin, pas) { ... }
    for (i, 1, 6, 1) { 
        print "\n[DÉBUT] Itération " + i
        
        if (i == 3) {
            print ">>> Condition VRAIE (i est 3) : Appel de CONTINUE."
            continue
        }
        
        print ">>> Normal : Instruction après 'continue' exécutée."
        count = count + 1
    }
    
    print "\n--- RÉSULTAT DU TEST ---"
    print "Nombre total d'exécutions complètes du corps de la boucle : " + count
}

test_continue_keyword()

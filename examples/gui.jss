// advanced_gui.jss

gui_title("Application Avancée JsonScript")
gui_size(600, 300)

// Fonction appelée par le bouton pour le dialogue
func save_file_logic() {
    // 1. Demande de confirmation
    var confirmed = gui_confirm("Confirmation", "Voulez-vous enregistrer le fichier ?")
    
    if (confirmed == 1) { // 1 = True
        gui_alert("Dialogue", "Ouverture de la fenêtre d'enregistrement...")
        
        // 2. Ouvre le dialogue de sauvegarde
        var path = gui_save_file("Enregistrer le document", ".txt")
        
        if (len(path) > 0) { // Si l'utilisateur n'a pas annulé
            // 3. Simule l'écriture du fichier (utilisation de la commande existante)
            write_file(path, "Contenu du fichier JSS.")
            gui_alert("Succès", "Fichier enregistré : " + path)
            gui_set("status_label", "text", "Fichier enregistré : " + path)
        } else {
            gui_alert("Annulation", "Enregistrement annulé.")
        }
    } else {
        gui_set("status_label", "text", "Enregistrement ignoré.")
    }
}


// --- 1. Création des Frames (Conteneurs) ---

// Frame principal (parent: racine)
gui_new("main_frame", "Frame", {})
gui_grid("main_frame", 0, 0, {"sticky": "nsew"}) // Un seul Frame principal, prend toute la place

// Frame pour le côté gauche (parent: main_frame)
gui_new("left_panel", "Frame", {"relief": "sunken", "borderwidth": 2}, "main_frame")
gui_grid("left_panel", 0, 0, {"sticky": "ns"})

// Frame pour le côté droit (parent: main_frame)
gui_new("right_panel", "Frame", {"padx": 10, "pady": 10}, "main_frame")
gui_grid("right_panel", 0, 1, {"sticky": "nsew"})


// --- 2. Widgets dans les Frames ---

// Widget dans le panneau gauche
gui_new("left_label", "Label", {"text": "Panneau de Gauche"}, "left_panel")
gui_grid("left_label", 0, 0, {})

// Widget dans le panneau droit (Bouton d'action)
gui_new("action_button", "Button", {"text": "Démarrer Dialogue"}, "right_panel")
gui_grid("action_button", 0, 0, {})

// Label de statut
gui_new("status_label", "Label", {"text": "Prêt."}, "right_panel")
gui_grid("status_label", 1, 0, {"pady": 10})


// --- 3. Binding et Lancement ---
gui_on("action_button", "<Button-1>", "save_file_logic")

gui_show(null)

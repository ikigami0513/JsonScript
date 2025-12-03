// selection_test.jss

gui_title("Widgets de Sélection de JsonScript")
gui_size(800, 600)

func display_selection() {
    // gui_get fonctionne maintenant grâce à la variable de contrôle
    var check_state = gui_get("check_agree", "value") 
    var radio_choice = gui_get("radio_low", "value") // Lit le choix sélectionné dans le groupe radio

    var status = "Etat de la case à cocher: " + check_state
    var choice = "Choix radio: " + radio_choice
    
    gui_set("result_label", "text", status + " | " + choice)
    print status
    print choice
}

// 1. Checkbutton (Row 0)
gui_new("check_label", "Label", {"text": "Options:"})
gui_grid("check_label", 0, 0, {"sticky": "w", "pady": 5, "padx": 5})

// Crée le Checkbutton. Il gère sa propre variable de contrôle interne.
gui_new("check_agree", "Checkbutton", {"text": "J'accepte les conditions"})
gui_grid("check_agree", 0, 1, {"sticky": "w", "pady": 5, "padx": 5})

// 2. Radiobuttons (Row 1)
gui_new("radio_group_label", "Label", {"text": "Choisir le niveau:"})
gui_grid("radio_group_label", 1, 0, {"sticky": "w", "pady": 5, "padx": 5})

// CLÉ : Tous les Radiobuttons du groupe DOIVENT partager le même ID JSS (ici "radio_group")
// Cette ID est utilisée par notre Handler pour stocker la variable de contrôle partagée (tk.StringVar)

// 1. Radiobuttons (Row 1)
// On utilise "LEVEL" comme clé de groupe partagée
gui_new("radio_label", "Label", {"text": "Choisir le niveau:"})
gui_grid("radio_label", 1, 0, {"sticky": "w", "pady": 5, "padx": 5})

// Option 1 : Crée la variable de groupe "LEVEL"
gui_new("radio_low", "Radiobutton", {"text": "Bas", "value": "LOW", "group_id": "LEVEL"}) 
gui_grid("radio_low", 1, 1, {"sticky": "w", "padx": 5})

// Option 2 : Utilise la variable "LEVEL" existante
gui_new("radio_medium", "Radiobutton", {"text": "Moyen", "value": "MEDIUM", "group_id": "LEVEL"})
gui_grid("radio_medium", 1, 2, {"sticky": "w", "padx": 5})

// Option 3 : Utilise la variable "LEVEL" existante
gui_new("radio_high", "Radiobutton", {"text": "Élevé", "value": "HIGH", "group_id": "LEVEL"})
gui_grid("radio_high", 2, 1, {"sticky": "w", "padx": 5})

// 3. Bouton de soumission (Row 3)
gui_new("submit_button", "Button", {"text": "Afficher les résultats"})
gui_grid("submit_button", 3, 0, {"columnspan": 3, "pady": 10})

// 4. Label de résultats (Row 4)
gui_new("result_label", "Label", {"text": "Prêt à tester les sélections."})
gui_grid("result_label", 4, 0, {"columnspan": 3})

// 5. Binding
gui_on("submit_button", "<Button-1>", "display_selection")

// 6. Affichage
gui_show(null)

import queue
import threading
import tkinter as tk
from tkinter import messagebox
from typing import List, Any, Dict, Optional
from jsonscript.exceptions import ReturnValue
from jsonscript.handlers.base import BaseHandler, EvaluatorFunc
from jsonscript.environment import Environment


# Global queue to handle communication from the synchronous JsonScript thread 
# back to the asynchronous Tkinter main thread.
GUI_QUEUE = queue.Queue()


class GUIHandler(BaseHandler):
    # Stockage unique de la fenêtre principale Tkinter
    _root_window: Optional[tk.Tk] = None

    # Stockage des références des widgets par leur nom JSS
    _widgets_registry: Dict[str, tk.Widget] = {} 

    # Registre des variables de contrôle Tkinter
    _control_vars: Dict[str, tk.Variable] = {}
    
    # Référence statique à l'instance de l'environnement pour les callbacks
    _environment: Optional['Environment'] = None
    
    # Référence statique au callback d'évaluation pour exécuter les fonctions JS
    _evaluator_func: Optional[EvaluatorFunc] = None 

    def _get_root(self) -> tk.Tk:
        """Garantit que la fenêtre racine Tkinter n'est créée qu'une seule fois."""
        if GUIHandler._root_window is None:
            GUIHandler._root_window = tk.Tk()
            GUIHandler._root_window.title("JsonScript Application")
        return GUIHandler._root_window

    def can_handle(self, command: str) -> bool:
        return command in {
            "gui_new", 
            "gui_set", 
            "gui_show", 
            "gui_on", 
            "gui_quit",
            "gui_title",
            "gui_size",
            "gui_get",
            "gui_grid",
            "gui_place"
        }
    
    def handle(self, command: str, args: List[Any], env: Any, evaluator: EvaluatorFunc) -> Any:
        # Stockage de l'environnement et de l'évaluateur pour le thread Tkinter
        GUIHandler._environment = env
        GUIHandler._evaluator_func = evaluator

        # Helper pour évaluer les arguments
        def arg(i): return evaluator(args[i], env)
        def arg_str(i): return str(arg(i))

        def get_widget(widget_id):
            widget = GUIHandler._widgets_registry.get(widget_id)
            if not widget:
                raise ValueError(f"Widget ID '{widget_id}' not found.")
            return widget

        # --- gui_new (Création) ---
        if command == "gui_new":
            widget_id = arg_str(0)
            widget_type = arg_str(1).lower()
            properties = arg(2)
            root = self._get_root()

            if widget_id in self._widgets_registry:
                raise ValueError(f"Widget ID '{widget_id}' already exists.")

            # Gestion des variables de contrôle
            control_var = None
            if widget_type in ("checkbutton", "radiobutton"):
                # 1. Extraire la clé du groupe pour usage interne
                group_key = properties.get('group_id', widget_id) 

                # 2. Nettoyer le dictionnaire AVANT de passer à Tkinter
                if 'group_id' in properties:
                    del properties['group_id'] # <--- CORRECTION CRITIQUE : Suppression de l'option custom
                
                # 3. Créer ou Réutiliser la variable de contrôle
                if group_key not in self._control_vars:
                    control_var = tk.StringVar(value=properties.get('value', group_key))
                    self._control_vars[group_key] = control_var
                else:
                    control_var = self._control_vars[group_key]
                
                # 4. Lier la variable à la propriété Tkinter
                properties['variable'] = control_var
            
            # Mappage du type de widget
            if widget_type == "button":
                widget = tk.Button(root, **properties)
            elif widget_type == "label":
                widget = tk.Label(root, **properties)
            elif widget_type == "entry":
                widget = tk.Entry(root, **properties)
            elif widget_type == "checkbutton": 
                widget = tk.Checkbutton(root, **properties)
            elif widget_type == "radiobutton": 
                widget = tk.Radiobutton(root, **properties)
            else:
                raise ValueError(f"Unknown widget type: {widget_type}")

            self._widgets_registry[widget_id] = widget
            if control_var:
                # On enregistre la variable de contrôle uniquement si elle a été créée
                self._control_vars[widget_id] = control_var
            return True

        # --- gui_on (Binding d'événement) ---
        if command == "gui_on":
            # Syntax: gui_on("ID_BUTTON", "<Button-1>", "on_click_func")
            widget_id = arg_str(0)
            event_type = arg_str(1)
            js_func_name = arg_str(2)
            
            widget = GUIHandler._widgets_registry.get(widget_id)
            if not widget:
                raise ValueError(f"Widget '{widget_id}' not found.")
            
            # Création du pont (bridge)
            callback = create_js_callback(js_func_name)
            widget.bind(event_type, callback)
            return True

        # --- gui_show (Lancement) ---
        if command == "gui_show":
            root = self._get_root()
            root.mainloop()
            return True

        # --- gui_set (Mise à jour d'attribut) ---
        if command == "gui_set":
            widget_id = arg_str(0)
            attr = arg_str(1).lower()
            value = arg(2)
            widget = get_widget(widget_id)
            
            # 1. Priorité: Définir la valeur via la variable de contrôle
            if attr == "value" and widget_id in self._control_vars:
                # Utilise la méthode .set() de la variable de contrôle
                self._control_vars[widget_id].set(value)
                return True

            # 2. Cas général: Définir une propriété de configuration
            widget.config(**{attr: value})
            return True

        # --- gui_quit ---
        if command == "gui_quit":
            # Cherche la racine et la ferme (simplification)
            for widget in GUIHandler._widgets_registry.values():
                if isinstance(widget, tk.Tk):
                    widget.quit()
                    return True
            return False
        
        if command == "gui_title":
            # Syntax: gui_title("Nouveau Titre")
            
            # On évalue l'expression pour obtenir le titre (peut être une variable)
            new_title = str(evaluator(args[0], env))
            
            # Récupère la fenêtre racine (qui existe forcément ou est créée ici)
            root = self._get_root() 
            
            # Définit le titre de la fenêtre Tkinter
            root.title(new_title)
            return True
        
        if command == "gui_size":
            # Syntax: gui_size(width, height)
            
            width = int(arg(0))
            height = int(arg(1))
            
            root = self._get_root()
            
            # Utilise la méthode geometry() de Tkinter
            root.geometry(f"{width}x{height}")
            
            return True
        
        if command == "gui_get":
            # Syntax: gui_get("input_id", "value")
            widget_id = arg_str(0)
            prop = arg_str(1).lower()
            widget = get_widget(widget_id)

            # 1. Priorité: Récupérer la valeur de la variable de contrôle pour les widgets d'état
            if widget_id in self._control_vars:
                # Récupère l'état (1/0 pour Checkbutton, string pour Radiobutton)
                return self._control_vars[widget_id].get() 

            # 2. Cas Entry (avec la méthode .get() de Tkinter)
            if prop == "value" and hasattr(widget, 'get'):
                return widget.get()
            
            # 3. Récupérer une autre propriété de configuration
            return widget.cget(prop)
        
        if command == "gui_grid":
            # Syntax: gui_grid("widget_id", row, col, {options...})
            widget_id = arg_str(0)
            row = int(arg_str(1))
            col = int(arg_str(2))
            widget = get_widget(widget_id)

            # Les options sont un dictionnaire optionnel (ex: { "padx": 5, "sticky": "w" })
            options = {}
            if len(args) > 3:
                options = evaluator(args[3], env)

            widget.grid(row=row, column=col, **options)
            return True


def create_js_callback(js_func_name: str, instance_name: str = None, event_type: str = None) -> callable:
    """Crée la fonction Python qui sera appelée par Tkinter lors d'un événement."""

    def python_callback(event=None):
        env = GUIHandler._environment
        evaluator = GUIHandler._evaluator_func
        
        if not env or not evaluator:
            print("Erreur critique: Environnement non chargé pour le callback GUI.")
            return

        # Construction de l'appel JsonScript
        # Si c'est une méthode d'instance, on appelle ["call_method", ["get", instance_name], js_func_name]
        # Si c'est une fonction globale, on appelle ["call", js_func_name]
        
        if instance_name:
            # On simule l'appel de méthode: ["call_method", instance, method]
            raw_call = ["call_method", ["get", instance_name], js_func_name]
        else:
            # Appel de fonction: ["call", function]
            raw_call = ["call", js_func_name]
            
        try:
            # Exécution de l'instruction (déclenchant la logique JS)
            evaluator(raw_call, env)
        except ReturnValue:
            pass # Les retours sont ignorés dans les callbacks
        except Exception as e:
            print(f"Erreur d'exécution JS dans le callback '{js_func_name}': {e}")
            messagebox.showerror("Erreur Script JS", f"Erreur dans le code: {e}")

    return python_callback

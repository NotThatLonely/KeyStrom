import pygame
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import os
import json
import threading
from pynput import keyboard, mouse

# Initialize pygame mixer for sound
pygame.mixer.init()

class KeyStromApp:
    def __init__(self, root):
        self.root = root
        self.root.title("KeyStrom")

        # Set the window size (width x height)
        window_width = 500
        window_height = 500

        # Get the screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Calculate position to center the window
        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)

        # Set the window position and size
        self.root.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")

        # Disable resizing to prevent maximization
        self.root.resizable(False, False)

        # Custom icon (adjust the path to your icon)
        self.root.iconphoto(True, tk.PhotoImage(file="assets/icon/ic.png"))

        self.sound_sets = {}
        self.mouse_sound_sets = {}
        self.selected_sound_set = None
        self.selected_mouse_sound_set = None
        self.key_mappings = {}
        self.mouse_mappings = {}

        # Track key press states
        self.key_states = {}
        self.mouse_button_states = {}

        # Volume levels for keyboard and mouse
        self.keyboard_volume = 1.0  # Default to full volume
        self.mouse_volume = 1.0

        # Default sound directories
        self.keyboard_sound_directory = os.path.join(os.getcwd(), "sound_sets")
        self.mouse_sound_directory = os.path.join(os.getcwd(), "mouse_sounds")

        # Setup the main UI
        self.create_widgets()

        # Load sound sets immediately after the app starts
        self.load_sound_sets()

        # Start global listeners for keyboard and mouse events
        self.start_global_listeners()

    def create_widgets(self):
        """Set up all UI elements with a modern style using ttk widgets."""
        style = ttk.Style()
        style.configure("TButton", padding=6, relief="flat", background="#4CAF50", font=("Helvetica", 12), width=20)
        style.configure("TLabel", font=("Helvetica", 12), background="#f0f0f0")
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TCombobox", font=("Helvetica", 12), padding=5)
        style.configure("TCheckbutton", font=("Helvetica", 12), background="#f0f0f0")

        # Frame for main content
        main_frame = ttk.Frame(self.root)
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Title Label (centralized)
        self.title_label = ttk.Label(main_frame, text="KeyStrom", font=("Helvetica", 18, "bold"))
        self.title_label.grid(row=0, column=0, pady=10, columnspan=2, sticky="n")

        # Sound Set Selection for Keyboard (centralized)
        self.sound_set_label = ttk.Label(main_frame, text="Keyboard:")
        self.sound_set_label.grid(row=1, column=0, pady=5, sticky="w")

        self.selected_sound_set_var = tk.StringVar()
        self.sound_set_menu = ttk.Combobox(main_frame, textvariable=self.selected_sound_set_var, state="readonly", width=30)
        self.sound_set_menu.set("Select Sound Set")
        self.sound_set_menu.grid(row=2, column=0, pady=5, sticky="ew")
        self.sound_set_menu.bind("<<ComboboxSelected>>", self.on_sound_set_selected)

        # Volume control for keyboard
        self.keyboard_volume_label = ttk.Label(main_frame, text="Keyboard Volume:")
        self.keyboard_volume_label.grid(row=3, column=0, pady=5, sticky="w")
        self.keyboard_volume_slider = ttk.Scale(main_frame, from_=0, to=1, value=1, orient="horizontal", command=self.set_keyboard_volume)
        self.keyboard_volume_slider.grid(row=4, column=0, pady=5, sticky="ew")

        # Sound Set Selection for Mouse
        self.mouse_set_label = ttk.Label(main_frame, text="Mouse:")
        self.mouse_set_label.grid(row=5, column=0, pady=5, sticky="w")

        self.selected_mouse_sound_set_var = tk.StringVar()
        self.mouse_set_menu = ttk.Combobox(main_frame, textvariable=self.selected_mouse_sound_set_var, state="readonly", width=30)
        self.mouse_set_menu.set("Select Mouse Sound Set")
        self.mouse_set_menu.grid(row=6, column=0, pady=5, sticky="ew")
        self.mouse_set_menu.bind("<<ComboboxSelected>>", self.on_mouse_sound_set_selected)

        # Volume control for mouse
        self.mouse_volume_label = ttk.Label(main_frame, text="Mouse Volume:")
        self.mouse_volume_label.grid(row=7, column=0, pady=5, sticky="w")
        self.mouse_volume_slider = ttk.Scale(main_frame, from_=0, to=1, value=1, orient="horizontal", command=self.set_mouse_volume)
        self.mouse_volume_slider.grid(row=8, column=0, pady=5, sticky="ew")

        # Debug Mode Checkbox (optional)
        self.debug_mode = tk.BooleanVar(value=False)
        self.debug_check = ttk.Checkbutton(main_frame, text="Debug Mode", variable=self.debug_mode)
        self.debug_check.grid(row=9, column=0, pady=5, sticky="w")

        # Footer with links
        footer_frame = ttk.Frame(self.root)
        footer_frame.pack(pady=10, side="bottom", fill="x", anchor="center")

        footer_text = ttk.Label(footer_frame, text="Made with <3 by NotThatLonely", font=("Helvetica", 10))
        footer_text.pack(side="left", padx=5)

        # Links (replace with actual URLs)
        links_frame = ttk.Frame(footer_frame)
        links_frame.pack(side="right")

        github_link = ttk.Label(links_frame, text="GitHub", font=("Helvetica", 10), foreground="blue", cursor="hand2")
        github_link.bind("<Button-1>", lambda e: self.open_link("https://github.com"))
        github_link.pack(side="left", padx=5)

        youtube_link = ttk.Label(links_frame, text="YouTube", font=("Helvetica", 10), foreground="blue", cursor="hand2")
        youtube_link.bind("<Button-1>", lambda e: self.open_link("https://youtube.com/@NotThatLonely"))
        youtube_link.pack(side="left", padx=5)

        version_link = ttk.Label(links_frame, text="Newest Version", font=("Helvetica", 10), foreground="blue", cursor="hand2")
        version_link.bind("<Button-1>", lambda e: self.open_link("https://example.com/latest-version"))
        version_link.pack(side="left", padx=5)

        website_link = ttk.Label(links_frame, text="Website", font=("Helvetica", 10), foreground="blue", cursor="hand2")
        website_link.bind("<Button-1>", lambda e: self.open_link("https://example.com"))
        website_link.pack(side="left", padx=5)

    def open_link(self, url):
        """Opens the URL in the default web browser."""
        import webbrowser
        webbrowser.open(url)

    def set_keyboard_volume(self, value):
        """Adjust the volume for the keyboard sounds."""
        self.keyboard_volume = float(value)

    def set_mouse_volume(self, value):
        """Adjust the volume for the mouse sounds."""
        self.mouse_volume = float(value)

    def load_sound_sets(self):
        """Loads the available sound sets for keyboard and mouse from the default directories."""
        # Load keyboard sound sets
        self.load_directory(self.keyboard_sound_directory, "keyboard")

        # Load mouse sound sets
        self.load_directory(self.mouse_sound_directory, "mouse")

        # Update the UI
        self.update_sound_set_menu()

    def load_directory(self, directory, device_type):
        """Helper function to load sound packs from a directory."""
        sound_sets = {}
        for folder_name in os.listdir(directory):
            folder_path = os.path.join(directory, folder_name)
            if os.path.isdir(folder_path):
                config_file = os.path.join(folder_path, "config.json")
                if os.path.isfile(config_file):
                    try:
                        with open(config_file, "r") as file:
                            config = json.load(file)
                            sound_sets[folder_name] = config
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to load config for {folder_name}: {e}")
        
        if device_type == "keyboard":
            self.sound_sets = sound_sets
        elif device_type == "mouse":
            self.mouse_sound_sets = sound_sets

    def update_sound_set_menu(self):
        """Update the dropdown menus for keyboard and mouse sound sets."""
        # Update keyboard sound set menu
        sound_set_names = list(self.sound_sets.keys())
        self.sound_set_menu["values"] = sound_set_names

        # Update mouse sound set menu
        mouse_set_names = list(self.mouse_sound_sets.keys())
        self.mouse_set_menu["values"] = mouse_set_names

    def on_sound_set_selected(self, event):
        """Handle keyboard sound set selection."""
        selected_sound_set = self.selected_sound_set_var.get()
        if selected_sound_set in self.sound_sets:
            self.select_sound_set(selected_sound_set)

    def on_mouse_sound_set_selected(self, event):
        """Handle mouse sound set selection."""
        selected_mouse_sound_set = self.selected_mouse_sound_set_var.get()
        if selected_mouse_sound_set in self.mouse_sound_sets:
            self.select_mouse_sound_set(selected_mouse_sound_set)

    def select_sound_set(self, sound_set_name):
        """Load the selected keyboard sound set."""
        self.selected_sound_set = sound_set_name
        self.key_mappings = self.sound_sets[sound_set_name].get("defines", {})

    def select_mouse_sound_set(self, sound_set_name):
        """Load the selected mouse sound set."""
        self.selected_mouse_sound_set = sound_set_name
        self.mouse_mappings = self.mouse_sound_sets[sound_set_name].get("defines", {})

    def play_sound(self, key, mappings, sound_dir, sound_set_name, volume):
        """Play the sound associated with the key for either keyboard or mouse."""
        sound_file = mappings.get(key)
        if not sound_file:
            return

        sound_file_path = os.path.join(sound_dir, sound_set_name, sound_file)
        if os.path.exists(sound_file_path):
            try:
                sound = pygame.mixer.Sound(sound_file_path)
                sound.set_volume(volume)  # Set the volume based on the slider
                sound.play()
                if self.debug_mode.get():
                    print(f"Playing sound for {key}: {sound_file_path} at volume {volume}")
            except Exception as e:
                print(f"Error playing sound: {e}")
        else:
            print(f"Sound file {sound_file_path} not found!")

    def on_key_press_global(self, key):
        """Global key press handler."""
        key_code = None
        if isinstance(key, keyboard.Key):
            # Handle special keys using their Key representation (e.g., Key.space)
            key_code = str(key)
        elif hasattr(key, 'char') and key.char:
            # Handle alphanumeric keys by their character representation
            key_code = key.char

        if key_code and not self.key_states.get(key_code, False):
            self.play_sound(key_code, self.key_mappings, self.keyboard_sound_directory, self.selected_sound_set, self.keyboard_volume)
            self.key_states[key_code] = True  # Mark key as pressed

    def on_key_release_global(self, key):
        """Global key release handler."""
        key_code = None
        if isinstance(key, keyboard.Key):
            key_code = str(key)
        elif hasattr(key, 'char') and key.char:
            key_code = key.char

        if key_code:
            self.key_states[key_code] = False  # Mark key as released

    def on_mouse_click_global(self, x, y, button, pressed):
        """Global mouse click handler."""
        mouse_code = str(button)
        if pressed and not self.mouse_button_states.get(mouse_code, False):
            self.play_sound(mouse_code, self.mouse_mappings, self.mouse_sound_directory, self.selected_mouse_sound_set, self.mouse_volume)
            self.mouse_button_states[mouse_code] = True  # Mark button as pressed
        elif not pressed:
            self.mouse_button_states[mouse_code] = False  # Mark button as released

    def start_global_listeners(self):
        """Starts global listeners for keyboard and mouse events."""
        # Start keyboard listener in a separate thread
        keyboard_listener = keyboard.Listener(on_press=self.on_key_press_global, on_release=self.on_key_release_global)
        keyboard_listener.start()

        # Start mouse listener in a separate thread
        mouse_listener = mouse.Listener(on_click=self.on_mouse_click_global)
        mouse_listener.start()

# Function to run the GUI in a separate thread
def run_app():
    root = tk.Tk()
    app = KeyStromApp(root)
    root.mainloop()

if __name__ == "__main__":
    # Run the application in a separate thread
    app_thread = threading.Thread(target=run_app)
    app_thread.daemon = True  # Allow the app to close when the main program exits
    app_thread.start()

    # Main thread can do other work here, for now, we just wait for the GUI thread
    app_thread.join()

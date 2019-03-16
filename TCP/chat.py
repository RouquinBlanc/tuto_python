from ipywidgets import widgets
from IPython.display import display
import threading
from socket import *

class ChatClient:
    def __init__(self, address, port=9999):
        self.address = address
        self.port = port
        
        # Créer un champ de texte (pour ecrire)
        self.text = widgets.Text(description="Ecrire:", placeholder="Votre commande ici", disabled=True)
        self.text.on_submit(self.handle_submit)
        
        # Créer une zone d'affichage
        self.output = widgets.HTML(placeholder='Pas de message')

        # Créer un bouton pour effacer
        self.clear_button = widgets.Button(description='effacer', disabled=True)
        self.clear_button.on_click(self.effacer) 

        # Créer un bouton pour quitter
        self.quit_button = widgets.Button(description='deconnecter', disabled=True)
        self.quit_button.on_click(self.handle_quit)

        display(
            widgets.HBox([self.text, self.clear_button, self.quit_button]),
            self.output
        )
        
        self.thread = None
        self.sock = None

    def effacer(self, sender):
        self.output.value = ''
    
    def handle_quit(self, sender):
        if self.sock:
            self.sock.send(b'!quit\n')
    
    def handle_submit(self, sender):
        if self.text.value:
            data = self.text.value + '\n'
            self.sock.send(data.encode())
        self.text.value = ''

    def start(self):
        self.thread = threading.Thread(target=self.run)
        self.thread.start()
        
    def stop(self):
        if self.sock:
            self.sock.close()
        self.thread.join()
        
    def run(self):
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.settimeout(3)
        SERVEUR = (self.address, self.port)
        self.output.value += '<i>Connexion à {}...</i><br/>'.format(SERVEUR)
        try:
            self.sock.connect(SERVEUR)
        except IOError as ex:
            self.output.value += '<span style="color:red">Erreur de connexion: {}</span><br/>'.format(ex)
            return

        # Marquer comme connecté et activer les boutons
        self.output.value += '<span style="color:green">Connecté</span><br/>'
        self.clear_button.disabled = False
        self.quit_button.disabled = False
        self.text.disabled = False

        try:
            while True:
                self.sock.settimeout(None)
                msg = self.sock.recv(1024)
                if msg:
                    self.output.value += msg.decode() + '<br/>'
                else:
                    self.output.value += '<span style="color:red">Déconnecté</span><br/>'
                    break
        except Exception as ex:
            self.output.value += '<span style="color:red">Erreur: {}</span><br/>'.format(ex)
        finally:
            self.sock.close()

        self.clear_button.disabled = True
        self.quit_button.disabled = True
        self.text.disabled = True

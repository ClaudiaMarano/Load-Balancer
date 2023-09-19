import socket
import threading
import json
import os
import time

class Server(object):

    def __init__(self):
        self.ip = "127.0.0.1"
        self.port = 5001
        self.server_socket = None


    def creo_socket_server(self):
        """
        Funzione che crea la socket del server e crea un thread che rimane in ascolto per ricevere i comandi dal load balancer
        """
        # creo una socket server
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # collego la socket al server
        self.server_socket.bind((self.ip, self.port))
        # metto in ascolto il server
        self.server_socket.listen()
        print(f"Server in ascolto su {self.ip}:{self.port}")
        self.connetto_il_loadbalancer()



    def connetto_il_loadbalancer(self):
        try:
            while True:
                # Accetta le connessioni in entrata
                balancer_socket, balancer_ip = self.server_socket.accept()
                ricezione_dati = threading.Thread(target=self.ricevo_file_dal_loadbalancer, args=(balancer_socket,))
                ricezione_dati.start()
                ricezione_dati.join()
        except Exception as e:
            print("Errore durante la connessione con il loadbalancer:", e)


    def ricevo_file_dal_loadbalancer(self, balancer_socket):
        try:
            while True:
                file_name = balancer_socket.recv(4096).decode("utf-8")
                if not file_name:
                    break
                # Decodifica il file JSON
                json_data = json.loads(file_name)
                # Estrai il titolo e il contenuto dal file JSON
                titolo = json_data.get("titolo", "")
                contenuto = json_data.get("contenuto", "")

                print(f" File ricevuto correttamente dal server: {titolo}")
                # invia notifica al load balancer di avvenuta ricezione del file
                self.invia_risposte_al_loadbalancer(balancer_socket, titolo)

                # salvo il contenuto del file
                self.salvo_file_ricevuto(titolo, contenuto)

        except Exception as e:
            print("Errore durante la comunicazione con il loadbalancer:", e)
        finally:
            balancer_socket.close()

    def salvo_file_ricevuto(self, titolo, contenuto):

        # Genera un nome di file univoco basato su un timestamp
        timestamp = str(int(time.time()))  # Converti il timestamp in una stringa
        json_filename = f"json_files_1/{timestamp}_{titolo}.json"

        # Verifica se la directory "json_files" esiste, altrimenti creala
        if not os.path.exists("json_files_1"):
            os.makedirs("json_files_1")
            # salvo il contenuto del file
            with open(json_filename, "w", encoding="utf-8") as json_file:
                json_file.write(contenuto)
        else:
            # salvo il contenuto del file in un nuovo file all'interno della directory json_files
            with open(json_filename, "w", encoding="utf-8") as json_file:
                    json_file.write(contenuto)

    def svuota_directory_json_files(self):
        """
        Metodo che svuota il contenuto della directory "json_files_1" ogni volta che si riavvia il codice
        :return: None
        """
        json_files_directory = "json_files_1"
        try:
            for filename in os.listdir(json_files_directory):
                file_path = os.path.join(json_files_directory, filename)
                if os.path.isfile(file_path) and filename.endswith(".json"):
                    os.remove(file_path)
        except Exception as e:
            print(f"Errore durante lo svuotamento della directory JSON: {e}")


    def invia_risposte_al_loadbalancer(self, balancer_socket, titolo):
        """
                Metodo che invia la risposta al load balancer di avvenuta ricezione del file

                :param balancer_socket: socket del load balancer
                :param titolo: titolo del file ricevuto
                :return: None

                """

        message_to_client = f" File ricevuto correttamente dal server 1: {titolo}"
        balancer_socket.send(message_to_client.encode("utf-8"))



if __name__ == "__main__":
    server=Server()
    server.svuota_directory_json_files()
    server.creo_socket_server()

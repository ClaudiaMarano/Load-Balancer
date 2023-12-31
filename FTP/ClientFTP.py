import socket
import sys
import os
import threading
import random
import time
import json

class Client(object):
    def __init__(self):
        """
        Costruttore della classe Client
        """
        self.client_socket = None
        self.loadBalancer_ip = "127.0.0.1"
        self.loadBalancer_port = "60004"
        self.filepath = None
        self.file_da_inviare = []
        self.counter_richieste = 0


    def avvio_client(self):
        """
        Metodo che avvia il client e i thread di interfacciamento con l'utente e di invio file
        :return: None
        """
        self.avvio_client_socket()
        interfaccia = threading.Thread(target=self.interfaccia_utente)
        invio_file_al_loadbalancer = threading.Thread(target=self.invia_file_al_loadbalancer)
        interfaccia.start()
        invio_file_al_loadbalancer.start()
        interfaccia.join()
        invio_file_al_loadbalancer.join()

    def avvio_client_socket(self):
        """
        Metodo che avvia la socket del client e la connette al load balancer
        :return: None
        """
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect(("127.0.0.1", 60002))
            print(f"Connessione al server {self.loadBalancer_ip}:{self.loadBalancer_port} stabilita.")
        except:
            print(f"Errore durante la connessione al server: {socket.error}")
            sys.exit(1)


    def interfaccia_utente(self):
        """
        Metodo di interfaccia con l'utente, che richiede in input il comando da eseguire.
        Se il comando è "FTP", viene richiesto il numero di file da trasferire ai server, i quali vengono
        scelti randomicamente tra i file contenuti nella cartella "file"

        :return: None
        """
        while True:
            time.sleep(1)
            lista_file = os.listdir('./file/')  # Creo una lista con tutti i nomi dei file contenuti nella cartella "file"
            print("La lista dei file disponibili è: ", lista_file)
            if len(lista_file) == 0:  # se la cartella è vuota blocca il codice e restituisce l'errore
                raise Exception("La cartella non ha file al suo interno.")
            comando = input(" Digita il comando:  ")
            if comando == 'exit':  # se inserisco exit, si chiude la connessione
                print("Chiusura della connessione con il server...")
                break
            if comando == 'FTP':
                try:
                    numero_file = int(input('Inserisci il numero di file da trasferire: '))
                    self.scegli_file_da_inviare(numero_file)
                except Exception as e:
                    print("Errore nella scrittura dell'input; riprova: ", e)
            else:
                print("Errore nella scrittura dell'input; riprova. ")


    def scegli_file_da_inviare(self, numero_file):
        """
        Metodo che crea la lista dei file randomici da inviare ai server

        :param numero_file:
        :return: None
        """
        for numero in range(numero_file):
            nome_file_scelto = self.scegli_file_random()  # scelgo randomicamente un file da inviare
            filepath = './file/' + nome_file_scelto
            self.file_da_inviare.append(filepath)  # lo aggiungo alla lista

    def scegli_file_random(self):
        """
        Metodo che sceglie randomicamente un file dalla lista dei file considerata

        :return: file_casuale
        """
        # prendo la lista dei file fra cui scegliere
        lista_file = os.listdir('./file/')
        # scelgo casualmente uno fra i file nella lista
        file_casuale = random.choice(list(lista_file))
        return file_casuale

    def invia_file_al_loadbalancer(self):
        """
        Metodo che invia il file JSON al load balancer

        :return: None
        """
        try:
            while True:
                if len(self.file_da_inviare) != 0:
                    filepath = self.file_da_inviare[0]
                    self.file_da_inviare.pop(0)
                    self.invia_file_scelto(filepath)
        except socket.error as error:
            print(f"Errore di comunicazione con il loadbalancer: {error}")
            sys.exit(1)


    def invia_file_scelto(self, filepath):
        """
        Metodo che svolge operazioni sul file scelto per inviarlo al load balancer

        :param filepath: filepath del file da inviare
        :return: None
        """

        with open(filepath, 'r', encoding='utf-8') as file_json:  # apro il file JSON e lo converto in un dizionario
            json_data = json.load(file_json)
        json_data["request_type"] = 'file_di_testo' # aggiungo una chiave che identifica il tipo di richiesta
        json_data_to_send = json.dumps(json_data)  # converto in una stringa per poterlo mandare attraverso la socket
        self.client_socket.send(json_data_to_send.encode())
        time.sleep(0.3)
        self.counter_richieste += 1


if __name__ == "__main__":
    client = Client()
    client.avvio_client()

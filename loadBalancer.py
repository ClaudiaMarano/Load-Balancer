# -*- coding: utf-8 -*-
"""
Implementazione del load balancer
"""
import threading
import socket
import logging



def round_robin_method():
    pass


class LoadBalancer(object):

    def __init__(self):
        """
        Costruttore della classe loadBalancer
        """
        # porta in cui si mette in ascolto il server
        self.port = 5001
        self.ip = '127.0.0.1'
        # lista che tiene  conto dei client collegati con il loadBalancer 
        self.clients = []
        """(da implementare) il loadbalancer memorizza le richieste dei client qualora,
        in caso di errore di trasmissione dei comandi al server, 
        quest'ultimo inivii la richiesta al loadbalancer di ricevere nuovamente i compiti"""
        self.richieste = {}  # la chiave è ip del client, argomento nome richieste 
        self.servers = ["127.0.0.1", "127.0.0.1", "127.0.0.1"]
        self.port_server = [5003, 5004, 5005]
        self.current_server_index = 0
        self.current_server_port_index = 0

        # registro attività loadBalancer
        self.log_file = 'loadbalancer.log'
        logging.basicConfig(filename=self.log_file, level=logging.INFO, format='%(levelname)s - %(message)s')

    def avvio_loadbalancer(self):
        """
        funzione che aavvia i metodi del loadbalancer, nel caso apre e chiude thread per gestire comunicazioni con client
        e server
        """
        pass

    def gestione_comunicazione_client(self, client_socket):
        """
        Funzione che gestisce la comunicazione con il client:
            il server riceve i dati dal client e invia una risposta di avvenuta connessione;
            in seguito invierà il comando ad un server per elaborare la richiesta
        Returns
        -------
        None.
        """
        logging.info(f'Client connesso: {client_socket.getpeername()}')

        while True:
            try:
                # il loadBalancer riceve i dati dal client
                data = client_socket.recv(4096)
                message = data.decode("utf-8")
                if message.strip() == "exit": #strips leva gli spazi bianchi
                    print(f'{client_socket.getpeername()} si sta disconnettendo dal loadbalancer')
                    logging.info(f'Disconnessione da {client_socket.getpeername()}')
                    exit_response = "Disconnessione avvenuta con successo"
                    client_socket.send(exit_response.encode())
                    self.clients.remove(client_socket)
                    client_socket.close()
                    break
                else:
                    print("Messaggio ricevuto dal client: {}".format(message))
                    logging.info(f'Richiesta ricevuta dal Client {client_socket.getpeername()}:{message}')

                    # DEVO CHIAMARE LA FUNZIONE CHE INOLTRA LA RICHIESTA AD UN SERVER CON MECCANISMO ROUND ROBIN
                    self.route_message(client_socket, data)
            except:
                print("C'è stato un errore")


    def round_robin(self):
        server_address = self.servers[self.current_server_index]
        self.current_server_index = (self.current_server_index + 1) % len(self.servers)
        server_port = self.port_server[self.current_server_port_index]
        self.current_server_port_index = (self.current_server_port_index + 1) % len(self.port_server)
        return server_address, server_port

    def route_message(self, client_socket, data):
        try:
            server_address, server_port=self.round_robin()

            logging.info(f'Inoltro richiesta del Client {client_socket.getpeername()} al server {server_address}:{server_port}')

            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.connect((server_address, server_port))
            # data = client_socket.encode(message)
            # data = message.encode()
            server_socket.sendall(data)
            response = server_socket.recv(1024)
            server_socket.close()
            client_socket.send(response)
        except:
            print("C'è stato un errore")
    

    def creazione_socket_loadBalancer(self):

        """
        Funzione che crea la socket TCP del loadBalancer per connetterlo all'host ed ai server

        (da modificare)

        Returns
        -------
        None.
        """

        # Creazione della socket del server
        balancer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Binding della socket all'host e alla porta
        balancer_socket.bind((self.ip, self.port))
        balancer_socket.listen()
        print("Server di load balancing in ascolto su {}:{}".format(self.ip, self.port))
        self.connessione_client(balancer_socket)

    def connessione_client(self,balancer_socket):
                
        """
        Funzione che accetta le connessioni in entrata e le gestisce 

        """

        while True:
            # Accetta le connessioni in entrata
            client_socket, client_ip = balancer_socket.accept()
            # Aggiunge il client alla lista dei client connessi
            self.clients.append(client_socket)
            # Commento di riuscita connessione con il client
            print("Connessione accettata da {}:{}".format(client_ip[0], client_ip[1]))
            # client_socket.send('alias?'.encode("utf-8"))
            # alias = client_socket.recv(1024)
            # clients.append(client)
            # print(clients)
            # client_socket.send("ora sei connesso!".encode("utf-8"))
            # Avvia un thread separato per gestire il client
            client_thread = threading.Thread(target=self.gestione_comunicazione_client, args=(client_socket,))
            client_thread.start()
            # se il client si disconnette, termina il thread
            if client_socket not in self.clients:
                print(self.clients)
                client_thread.join()
        # self.gestione_comunicazione_client(client_socket)

    def monitoraggio_server(self):
        """
        metodo o insieme di metodi che ricevono e salvano le informazioni dello status (numero di richieste,
        operativo o non operativo, carico computazionale solo se troviamo funzioni che ci consentono di osservarlo) di ogni sever  
        in tempi regolari
        """

      

        pass

    def gestione_comunicazione_server(self):
        """
        funzione che invia e distribuisce le richieste(tramite la funzione di algortimo nel nostro caso il round robin).
        manda il segnale di chiusura della richiesta, reinvia il risulatato della richiesta

        """

    # def route_message(self, client_socket, message):
    #     server_address = self.servers[self.current_server_index]
    #     self.current_server_index = (self.current_server_index + 1) % len(self.servers)
    #     server_port = self.port_server[self.current_server_port_index]
    #     self.current_server_port_index = (self.current_server_port_index + 1) % len(self.port_server)

    #     server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     server_socket.connect((server_address, server_port))
    #     data = client_socket.encode(message)
    #     server_socket.sendall(data)
    #     response = server_socket.recv(1024)
    #     server_socket.close()
    #     client_socket.send(response)


if __name__ == '__main__':
    load_balancer = LoadBalancer()
    load_balancer.creazione_socket_loadBalancer()




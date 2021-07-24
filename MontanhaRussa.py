import queue
import threading
import time
import random
import logging

logging.basicConfig(level=logging.INFO, format='\n\t ------  %(asctime)s  - %(message)s -------\n')
logger = logging.getLogger(__name__)

sem_entrada = threading.Semaphore()
sem_fila = threading.Semaphore()
sem_volta = threading.Semaphore()
sem_saida = threading.Semaphore()



FilaPassageiros = queue.Queue()
FilaCarros = []
ListaTempo = []
ContadorExit = 0
CarExit = False
Assentos = 4 
n = 92
m = 2


# n = 148, m = 3, C = 4,  Te = 1 seg, Tm = 10 seg, Tp = 1 a 3 seg.
class MontanhaRussa(threading.Thread):
    def __init__(self, NumCarros, NumPassageiros):
        self.NumCarros = NumCarros
        self.NumPassageiros = NumPassageiros
        threading.Thread.__init__(self)
    def run(self):
            logger.info("Montanha Russa".upper())
            self.CriarCarros()
            print()
            self.CriarPassageiros()
            while True:
                 if CarExit:
                    break
            for i in range(len(FilaCarros)):
                thread =FilaCarros[i]
                thread.join()
                print("\n\t Carro " + str(thread.id +1 ) + " foi encerrado")
                print("\t Tempo de utilização do carro {} : ".format(thread.id+1) + str(10*thread.contadorVolta/(thread.tempoFinal - thread.tempoInicial)))
                print()           
    def CriarPassageiros(self): 
        for i in range(self.NumPassageiros):
            time.sleep(random.randint(1,3))
            print("Passageiro " + str(i+1) + " está na fila")
            passageiro = Passageiro(i)
            FilaPassageiros.put(passageiro)
            passageiro.start()
    def CriarCarros(self):
        for i in range(self.NumCarros):
            carro = Carro(i)
            FilaCarros.append(carro)
            carro.start()

class Carro(threading.Thread): 
    def __init__(self,id):
        self.id =id
        self.FilaAssentos = queue.Queue(maxsize = Assentos)
        self.validateVolta = False
        self.validateEntrada = False
        self.tempoInicial = time.time()
        self.tempoFinal = 0
        self.contadorVolta = 0
        threading.Thread.__init__(self) 
    def run(self):
        print("Carro " + str(self.id +1) + " Disponível")
        while True: 
            self.VoltaMontanhaRussa()
            if ContadorExit ==(n/Assentos):
                global CarExit
                CarExit = True
                break
        self.tempoFinal = time.time()
        # global tempoFinalCarros
        # tempoFinalCarros = tempoFinalCarros + (self.tempoFinal - self.tempoInicial)
       
    def VoltaMontanhaRussa(self):
        if (self.FilaAssentos.qsize() ==  Assentos) and self.validateEntrada == False and self.validateVolta == False:
            self.contadorVolta = self.contadorVolta + 1 
            carro = FilaCarros.pop(0)
            self.validateEntrada = True
            print("\n --> Inicio Volta do  carro " +str(self.id+1))
            print()
            # print(FilaCarros)
            time.sleep(10)
            print("\n <-- Fim Volta do  carro " +str(self.id+1))
            FilaCarros.append(carro)
            # print(FilaCarros)
            self.validateVolta = True
            global ContadorExit
            ContadorExit += 1
            print()

    def entraPassageiro(self):
        # print("------ ENTRADA PASSAGEIROS -----------")
        for i in range(Assentos):
            passageiro = FilaPassageiros.get()
            if i == 0:
                passageiro.tempoFinalFila = time.time()
                aux = passageiro.tempoFinalFila  - passageiro.tempoinicialFila
                ListaTempo.append(aux) 
            print("passageiro " + str(passageiro.id +1) + " Embarcou no carro " + str(self.id+1) )
            self.FilaAssentos.put(passageiro)
        time.sleep(1)

    def saiPassageiro(self):
        # print("-------- SAIDA PASSAGEIROS -----------")
        
        for i in range(Assentos):
            passageiro = self.FilaAssentos.get()
            print("passageiro " + str(passageiro.id +1) + " Desembarcou do carro " + str(self.id+1))
            passageiro.stop()
        time.sleep(1)
        self.validateVolta = False
        self.validateEntrada = False 



class Passageiro(threading.Thread):
    def __init__(self,id):
        self.id = id
        self.stop_thread = False
        self.tempoinicialFila = time.time()
        self.tempoFinalFila = 0 
        threading.Thread.__init__(self)
    def run(self):
        while True:
            if FilaCarros: 
                sem_fila.acquire()
                if FilaCarros: 
                    if  FilaPassageiros.qsize() >= Assentos: 
                        if FilaCarros[0].FilaAssentos.full() == False and  FilaCarros[0].validateVolta == False and FilaCarros[0].validateEntrada == False:
                            sem_entrada.acquire()
                            if FilaCarros : 
                                FilaCarros[0].entraPassageiro()
                            sem_entrada.release()
                sem_fila.release()  
            # if FilaCarros:
                sem_volta.acquire()
                if FilaCarros:
                    if FilaCarros[-1].validateVolta == True and FilaCarros[-1].validateEntrada == True:
                             if FilaCarros[-1].FilaAssentos.qsize() == Assentos:
                                sem_saida.acquire()
                                FilaCarros[-1].saiPassageiro()
                                sem_saida.release()
                sem_volta.release()

            if self.stop_thread:
                break
    def stop(self):
        self.stop_thread = True


def main():
    MR = MontanhaRussa(m,n)
    MR.start()
    MR.join()
    print()
    print("\t Tempo mínimo de espera dos passageiros na fila : " + str(min(ListaTempo)))
    print("\t Tempo máximo de espera dos passageiros na fila : " + str(max(ListaTempo)))
    media = sum(ListaTempo)/len(ListaTempo)
    print("\t Tempo médio de espera dos passageiros na fila :" + str(media))
    logger.info("Montanha Russa Fechada".upper())
if __name__ == '__main__':
    main()
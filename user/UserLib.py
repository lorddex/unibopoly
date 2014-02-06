# def rolldice():
#     n = random.randint(1,6) + random.randint(1,6)
#     move(n)

# def build(num):
#     # inserire tripla <Street, numberOfHouses, num>
#     # inserire tripla <Person, HasContract, nome/id della via>
#     # scalare i soldi: new_cashBalance = cashBalance - (purchaseCost*num) 
#     # aggiornare tripla <Person cashBalance  new_cashBalance>
#     # cambio turno    

# def buy:
#     # inserire la tripla <Person HasContract nome/id della stazione/societa'>
#     # scalare i soldi: new_cashBalance = cashBalance - (purchaseCost*num) 
#     # aggiornare tripla <Person cashBalance  new_cashBalance>)
#     # cambio turno    


# def move(n):
#     # nuovo_boxId = vecchio_boxID+n
#     # aggiornare tripla <Person IsInBox nuovo_boxId>
#     # mostro boxName
#     # ricevo dal server le azioni disponibili
#     # lancio il metodo opportuno 
    
# def paytoowner:
#     # aggiorno bilancio owner 
#     # aggiorno bilancio mio
#     # cambio turno

# def takeprobcard:
#     # scelgo in modo random un cardID
#     # mostro il corrispondente cardText
#     # eseguo il corrispondente cardAction (che potrebbe includere anche la chiamata del metodo wait(n) se la carta dice che deve fermarsi per qualche turno)

# def takehitchcard:
#     # scelgo in modo random un cardID
#     # mostro il corrispondente cardText
#     # eseguo il corrispondente cardAction

# def goto(id_box,n):
#     # aggiornare tripla <Person IsInBox Box>
#     # mostro boxName
#     # (in questo caso non dovrebbero esserci azioni disponibili al player, di solito bisogna fermarsi n turni o non fare nulla)
#     # richiamiamo wait(n) (wait(0) setta il flag a 0 quindi non blocca il player) 
#     # cambio turno

# def earn(n):
#     # aggiorna bilancio player (aumenta di n)
#     # aggiorna bilancio cassa (diminuisce di n)
#     # passa il turno

# def earnall(n):
#     # aggiorna bilancio degli altri (diminuiscono tutti di n)
#     # aggiorna bilancio player (aumenta di n*num_player)
#     # cambio turno

# def pay(n):
#     # aggiorna bilancio player (diminuisce di n)
#     # aggiorna bilancio cassa (aumenta di n)
#     # passa il turno

# def payall(n):
#     # aggiorna bilancio degli altri (aumentano tutti di n)
#     # aggiorna bilancio player (diminuisce di n*num_player)
#     # cambio turno

# def wait(n):
#     # setta un flag pari ad n il server ogni volta che deve assegnare
#     # il turno ad un player, legge questo tag e se e' maggiore di 0,
#     # lo decrementa e passa il turno al prossimo player

# def jailbreak(n):
#     # goto(ID_jailbreak)
#     # wait(n)

# def update: # aggiorna le azioni disponibili al client


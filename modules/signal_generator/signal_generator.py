# modules/symbol_data_fetcher/symbol_data_fetcher.py
# Kahden ekan potential-listalaisen ja isoimman 24h prosenttien omaavien kanssa pitää olla varoivainen, pitää harkita käyttää 1x niissä
# Laitetaan tähän Kolikkokohtaisen conffin luonti ja sinne muokkattavat: Käytetäänkö diverceä ja momentumia ja millä thresholildilla, muut asetukset voinee laittaa yleisiksi
# Jos laitetaan RSI-rajauksia, niiden ei saa vaikuttaa RSI-kirjauksiin, muutoin kuin niihin vaa laitetaan sitten joku not to use merkintä
# Ei laiteta mitään RSI rajauksia vielä tässä vaiheessa, ennenkuin kaikki tarvittavat RSI-tilastoinnit on tehty, ehkä ei ollenkaan vielä tässä vaiheessa
# Tän modulin pitää ottaa jo long-onlyt ja short-onlyt huomioon ja siivota logista niitä vastaan sotivat
#   

def main():

    args.func()

if __name__ == "__main__":
    main()

# BIGD Projektarbeit: Lebensmittelwarnung

Dieses Projekt soll die Daten der Website [Lebensmittelwarnung.de](Lebensmittelwarnung.de)
mittels eines Python Skripts täglich auf neue Einträge prüfen.
Neue Einträge werden mittels diesem Skript dann direkt auch an Kafka
übergeben. Von dort aus sollen die Daten noch veranschaulicht werden
und weitergegeben werden.

## Setup

1.

```
git clone --single-branch --branch no_mysql https://github.com/derRiesenOtter/BIGD.git no_mysql
cd BIGD
```

3.

```
sudo docker compose up -d
```

# BIGD Projektarbeit: Lebensmittelwarnung

Dieses Projekt soll die Daten der Website [Lebensmittelwarnung.de](Lebensmittelwarnung.de)
mittels eines Python Skripts stündlich auf neue Einträge prüfen.
Neue Einträge werden mittels diesem Skript dann direkt auch an Kafka
übergeben. Von dort aus sollen die Daten dann über ein weiteres Python
Skript an ElasticSearch weitergegeben und dann mittels Kibana
ausgewerten werden.

## Setup

1. GitHub Repository klonen

```sh
git clone https://github.com/derRiesenOtter/BIGD.git Lebensmittelwarnungen
cd Lebensmittelwarnungen
```

2. Über Docker compose Zookeeper, Kafka, ElasticSearch und Kibana starten

```sh
sudo docker compose up -d
```

3. Python Producer Skript starten

```sh
python3 Lebensmittelwarnung.py
```

4. Python Consumer Skript starten

```sh
python3 elasticsearch-connector.py
```

## Zugriff auf Datenvirtualisierung

Bei eingeschalteter VPN kann Kibana über

```
http://143.93.91.37:5601
```

aufgerufen werden.

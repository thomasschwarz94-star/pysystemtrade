import os
import yaml

def ib_defaults():
    """
    Robust IB connection defaults loader.
    Lädt Werte aus private/private_config.yaml,
    oder nutzt sinnvolle Defaults für Paper Trading.
    """

    base_path = os.path.expanduser("~/systemtrade/pysystemtrade/private")
    yaml_file = os.path.join(base_path, "private_config.yaml")

    defaults = {
        "ib_ipaddress": "127.0.0.1",
        "ib_port": 7497,
        "ib_account": "DU1234567",
        "ib_client_id": 101,
    }

    # YAML-Datei prüfen
    if not os.path.exists(yaml_file):
        print(f"⚠️  Keine private_config.yaml gefunden unter {yaml_file}. Verwende Defaults.")
        return defaults

    try:
        with open(yaml_file, "r") as f:
            config_data = yaml.safe_load(f) or {}
    except Exception as e:
        print(f"❌ Fehler beim Laden von {yaml_file}: {e}")
        return defaults

    broker_config = config_data.get("broker", {})

    final_config = {
        "ib_ipaddress": broker_config.get("host", defaults["ib_ipaddress"]),
        "ib_port": broker_config.get("port", defaults["ib_port"]),
        "ib_account": broker_config.get("account", defaults["ib_account"]),
        "ib_client_id": broker_config.get("client_id", defaults["ib_client_id"]),
    }

    print("✅ IB Defaults erfolgreich geladen:", final_config)
    return final_config
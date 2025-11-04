import os
import yaml
from sysdata.config.configdata import Config

def get_production_config():
    """
    Lädt die Produktionskonfiguration aus der privaten YAML-Datei,
    wenn vorhanden. Fällt sonst auf Default-Konfiguration zurück.
    """
    try:
        # Standardpfad zur privaten Config
        base_path = os.path.expanduser("~/systemtrade/pysystemtrade/private")
        yaml_path = os.path.join(base_path, "private_config.yaml")

        config = Config.default_config()

        if os.path.exists(yaml_path):
            with open(yaml_path, "r") as f:
                yaml_data = yaml.safe_load(f) or {}
                # Nur falls Config-Objekt update_from_dict unterstützt
                if hasattr(config, "update_from_dict"):
                    config.update_from_dict(yaml_data)
                else:
                    print("⚠️ Config.update_from_dict() nicht vorhanden, überspringe YAML merge.")
        else:
            print(f"⚠️ Keine private_config.yaml unter {yaml_path} gefunden. Verwende Defaults.")

        return config

    except Exception as e:
        print(f"❌ Fehler beim Laden der Produktionskonfiguration: {e}")
        return Config.default_config()
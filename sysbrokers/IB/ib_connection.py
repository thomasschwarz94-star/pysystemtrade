import time
from ib_insync import IB
from sysbrokers.IB.ib_connection_defaults import ib_defaults
from syscore.exceptions import missingData
from syscore.constants import arg_not_supplied
from syslogging.logger import *
from sysdata.config.production_config import get_production_config


class connectionIB:
    """
    Handles Interactive Brokers (IB) connection using ib_insync.
    """

    def __init__(self, client_id: int, ib_ipaddress=None, ib_port=None, account=arg_not_supplied, log=None):
        """
        Initialize the IB connection safely, using defaults if not provided.
        """
        self.client_id = client_id
        self.log = log or get_logger("connectionIB")

        defaults = ib_defaults()
        ipaddress = ib_ipaddress or defaults.get("ib_ipaddress", "127.0.0.1")
        port = ib_port or defaults.get("ib_port", 7497)

        # Fallback-Logik für leere Werte
        if not ipaddress:
            ipaddress = "127.0.0.1"
            self.log.warning("No IP address found, using default 127.0.0.1")
        if not port:
            port = 7497
            self.log.warning("No port found, using default 7497 (Paper Trading)")

        self._ib_connection_config = dict(ipaddress=ipaddress, port=port, client=client_id)

        self._log = get_logger(
            "connectionIB",
            {
                TYPE_LOG_LABEL: "INIT",
                BROKER_LOG_LABEL: "IB",
                CLIENTID_LOG_LABEL: client_id,
            },
        )

        try:
            self._init_connection(ipaddress=ipaddress, port=port, client_id=client_id, account=account)
        except Exception as e:
            self._log.critical(f"IB connection failed: {e}")
            raise

    def _init_connection(self, ipaddress: str, port: int, client_id: int, account=arg_not_supplied):
        """
        Establish connection to TWS or IB Gateway.
        """
        ib = IB()

        try:
            if account is arg_not_supplied:
                account = get_broker_account()
        except missingData:
            self.log.error("Broker account ID not found in private config — may cause issues.")
            ib.connect(ipaddress, port, clientId=client_id)
        else:
            ib.connect(ipaddress, port, clientId=client_id, account=account)

        time.sleep(2)
        self._ib = ib
        self._account = account
        self.log.info(f"Connected to IB at {ipaddress}:{port} with client_id {client_id}")

    @property
    def ib(self):
        return self._ib

    def get_log(self):
        return self._log

    def __repr__(self):
        return f"IB broker connection {self._ib_connection_config}"

    def client_id(self):
        return self._ib_connection_config["client"]

    def close_connection(self):
        """
        Close the IB connection safely.
        """
        self.log.debug(f"Terminating {self._ib_connection_config}")
        try:
            self.ib.disconnect()
            self.log.info("IB connection closed.")
        except BaseException:
            self.log.warning("Trying to disconnect IB client failed. Ensure process is killed.")


def get_broker_account() -> str:
    """
    Retrieve the broker account ID safely.
    Falls back to private_config.yaml or ib_defaults() if missing.
    """
    try:
        production_config = get_production_config()
        account_id = production_config.get_element("broker_account")
        if account_id:
            return account_id
    except Exception as e:
        print(f"⚠️ Warnung: Produktionskonfiguration konnte nicht geladen werden ({e})")

    # Fallback auf private_config oder ib_defaults
    try:
        from sysbrokers.IB.ib_connection_defaults import ib_defaults
        cfg = ib_defaults()
        if "ib_account" in cfg:
            print(f"ℹ️ Verwende Fallback-Account aus ib_defaults: {cfg['ib_account']}")
            return cfg["ib_account"]
    except Exception as e:
        print(f"⚠️ Konnte auch keine Fallback-Konfiguration laden ({e})")

    raise ValueError("❌ Kein gültiges Brokerkonto gefunden – prüfe private/private_config.yaml")

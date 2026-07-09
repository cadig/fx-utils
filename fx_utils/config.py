"""Loads OANDA credentials and account definitions from the gitignored config/ directory."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import yaml
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = REPO_ROOT / "config"
CREDENTIALS_PATH = CONFIG_DIR / "credentials.env"
ACCOUNTS_PATH = CONFIG_DIR / "accounts.yaml"

VALID_ENVIRONMENTS = {"practice", "live"}


@dataclass(frozen=True)
class Account:
    id: str
    alias: str


@dataclass(frozen=True)
class Settings:
    token: str
    environment: str
    accounts: list[Account]
    default_alias: str | None

    def account_for(self, alias: str | None = None) -> Account:
        target = alias or self.default_alias
        if target is None:
            if len(self.accounts) == 1:
                return self.accounts[0]
            raise ValueError(
                "No account alias specified and no default_alias set in accounts.yaml"
            )
        for account in self.accounts:
            if account.alias == target:
                return account
        raise ValueError(
            f"Unknown account alias '{target}'. Known aliases: "
            f"{[a.alias for a in self.accounts]}"
        )


def load_settings() -> Settings:
    if not CREDENTIALS_PATH.exists():
        raise FileNotFoundError(
            f"Missing {CREDENTIALS_PATH}. Copy config/credentials.example.env to "
            "config/credentials.env and fill in your OANDA PAT."
        )
    if not ACCOUNTS_PATH.exists():
        raise FileNotFoundError(
            f"Missing {ACCOUNTS_PATH}. Copy config/accounts.example.yaml to "
            "config/accounts.yaml and fill in your sub-account ids."
        )

    load_dotenv(CREDENTIALS_PATH)
    token = os.environ.get("OANDA_TOKEN", "").strip()
    environment = os.environ.get("OANDA_ENVIRONMENT", "practice").strip().lower()

    if not token or token == "your-personal-access-token-here":
        raise ValueError(f"OANDA_TOKEN not set in {CREDENTIALS_PATH}")
    if environment not in VALID_ENVIRONMENTS:
        raise ValueError(
            f"OANDA_ENVIRONMENT must be one of {VALID_ENVIRONMENTS}, got '{environment}'"
        )

    with ACCOUNTS_PATH.open() as f:
        raw = yaml.safe_load(f) or {}

    accounts = [Account(id=a["id"], alias=a["alias"]) for a in raw.get("accounts", [])]
    if not accounts:
        raise ValueError(f"No accounts defined in {ACCOUNTS_PATH}")

    return Settings(
        token=token,
        environment=environment,
        accounts=accounts,
        default_alias=raw.get("default_alias"),
    )

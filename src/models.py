from dataclasses import dataclass
from typing import List, Optional


SearchUrl = str


@dataclass
class Accommodation:
    id: Optional[int]
    title: Optional[str]


@dataclass
class SearchResults:
    search_url: str
    count: Optional[int]
    accommodations: List[Accommodation]


@dataclass
class Notification:
    message: str


@dataclass
class UserConf:
    conf_title: Optional[str]
    telegram_id: str
    search_url: str

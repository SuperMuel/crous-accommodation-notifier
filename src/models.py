from typing import List, Optional

from pydantic import HttpUrl, BaseModel


class Accommodation(BaseModel):
    id: int | None
    title: str | None
    price: float | str | None
    overview_details: str | None = None
    image_url: HttpUrl | None = None


class SearchResults(BaseModel):
    search_url: HttpUrl
    count: Optional[int]
    accommodations: List[Accommodation]


class Notification(BaseModel):
    message: str


class UserConf(BaseModel):
    conf_title: Optional[str]
    telegram_id: str
    search_url: HttpUrl

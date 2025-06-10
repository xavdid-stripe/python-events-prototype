# don't look behind the curtain...

import json
from dataclasses import asdict, dataclass, field
from typing import List, Literal, NoReturn, Optional, Union


@dataclass
class RelatedObject:
    id: str
    type: str


@dataclass
class BaseThinEvent:
    id: str
    type: str

    # Used for this dogfooding so I only have to define events once
    def _dump(self) -> str:
        # these bad types are fine, child classes have them
        return json.dumps(
            asdict(
                GenericThinEvent(
                    self.id,
                    self.type,  # type: ignore
                    self.related_object if hasattr(self, "related_object") else None,  # type: ignore
                )
            )
        )


# the manual class today
@dataclass
class GenericThinEvent(BaseThinEvent):
    id: str
    type: str
    related_object: Optional[RelatedObject] = None

    @staticmethod
    def _from_str(body: str) -> "GenericThinEvent":
        o = json.loads(body)

        return GenericThinEvent(
            o["id"],
            o["type"],
            related_object=RelatedObject(**o["related_object"])
            if o.get("related_object")
            else None,
        )


@dataclass
class Order:
    id: str
    created: str
    num_items: int
    cost_cents: int
    delivery_date: str


@dataclass
class OrderShippedData:
    shipping_service: str


@dataclass
class OrderShippedPushedEvent(BaseThinEvent):
    related_object: RelatedObject
    type: Literal["order.shipped"] = field(default="order.shipped", init=False)

    def pull(self) -> "OrderShippedEvent":
        return _DATABASE[self.id]

    def fetch_related_object(self) -> Order:
        return _DATABASE[self.related_object.id]


@dataclass
class OrderShippedEvent(OrderShippedPushedEvent):
    data: OrderShippedData


@dataclass
class OrderDeliveryAttemptedData:
    success: bool
    attempt_num: int
    delivery_location: str


@dataclass
class OrderDeliveryAttemptedPushedEvent(BaseThinEvent):
    related_object: RelatedObject
    type: Literal["order.delivery_attempted"] = field(
        default="order.delivery_attempted", init=False
    )

    def pull(self) -> "OrderDeliveryAttemptedEvent":
        return _DATABASE[self.id]

    def fetch_related_object(self) -> Order:
        return _DATABASE[self.related_object.id]


@dataclass
class OrderDeliveryAttemptedEvent(OrderDeliveryAttemptedPushedEvent):
    data: OrderDeliveryAttemptedData


@dataclass
class OrderLostData:
    last_seen_city: str


@dataclass
class OrderLostPushedEvent(BaseThinEvent):
    type: Literal["order.lost"] = field(default="order.lost", init=False)

    def pull(self) -> "OrderLostEvent":
        return _DATABASE[self.id]


@dataclass
class OrderLostEvent(OrderLostPushedEvent):
    data: OrderLostData


@dataclass
class Movie:
    id: str
    title: str
    release_year: int


@dataclass
class MovieStartedPushedEvent(BaseThinEvent):
    related_object: RelatedObject
    type: Literal["movie.started"] = field(default="movie.started", init=False)

    def pull(self) -> "MovieStartedEvent":
        return _DATABASE[self.id]

    def fetch_related_object(self) -> Movie:
        return _DATABASE[self.related_object.id]


@dataclass
class MovieStartedData:
    date: str


@dataclass
class MovieStartedEvent(MovieStartedPushedEvent):
    data: MovieStartedData


@dataclass
class MovieCompletedPushedEvent(BaseThinEvent):
    related_object: RelatedObject
    type: Literal["movie.completed"] = field(default="movie.completed", init=False)

    def pull(self) -> "MovieCompletedEvent":
        return _DATABASE[self.id]

    def fetch_related_object(self) -> Movie:
        return _DATABASE[self.related_object.id]


@dataclass
class MovieCompletedData:
    user: str
    rating: int


@dataclass
class MovieCompletedEvent(MovieCompletedPushedEvent):
    data: MovieCompletedData


PushedThinEvents = Union[
    OrderShippedPushedEvent,
    OrderDeliveryAttemptedPushedEvent,
    OrderLostPushedEvent,
    MovieStartedPushedEvent,
    MovieCompletedPushedEvent,
]
ThinEvents = Union[
    OrderShippedEvent,
    OrderDeliveryAttemptedEvent,
    OrderLostEvent,
    MovieStartedEvent,
    MovieCompletedEvent,
]


class CactusClient:
    def parse_event_v1(self, body: str) -> "GenericThinEvent":
        return GenericThinEvent._from_str(body)

    def parse_event_v2(self, body: str) -> PushedThinEvents:
        e = json.loads(body)
        id_ = e["id"]
        if e["related_object"]:
            rel = RelatedObject(e["related_object"]["id"], e["related_object"]["type"])
        else:
            rel = RelatedObject("ig", "nored")

        type_ = e["type"]
        if type_ == "order.shipped":
            return OrderShippedPushedEvent(id_, rel)
        if type_ == "order.delivery_attempted":
            return OrderDeliveryAttemptedPushedEvent(id_, rel)
        if type_ == "order.lost":
            return OrderLostPushedEvent(id_)
        if type_ == "movie.started":
            return MovieStartedPushedEvent(id_, rel)
        if type_ == "movie.completed":
            return MovieCompletedPushedEvent(id_, rel)

        raise ValueError(f'unexpected thin event type: "{type_}"')

    def retrieve_event(self, id_: str) -> BaseThinEvent:
        if not id_.startswith("evt_"):
            raise ValueError(f"unable to fetch event with invalid id: {id_}")

        try:
            return _DATABASE[id_]
        except KeyError:
            raise ValueError(f"404: event {id_} not found")

    def retireve_order(self, id_: str) -> "Order":
        if not id_.startswith("ord_"):
            raise ValueError(f"unable to fetch order with invalid id: {id_}")

        try:
            return _DATABASE[id_]
        except KeyError:
            raise ValueError(f"404: order {id_} not found")

    def retireve_movie(self, id_: str) -> "Movie":
        if not id_.startswith("mov_"):
            raise ValueError(f"unable to fetch movie with invalid id: {id_}")

        try:
            return _DATABASE[id_]
        except KeyError:
            raise ValueError(f"404: movie {id_} not found")


class CactusHandler:
    def handle(self, body: str) -> bool:
        event = CactusClient().parse_event_v2(body)

        if event.type == "order.shipped":
            return self.on_order_shipped(event)

        if event.type == "order.delivery_attempted":
            return self.on_order_delivery_attempted(event)

        if event.type == "order.lost":
            return self.on_order_lost(event)

        if event.type == "movie.started":
            return self.on_movie_started(event)

        if event.type == "movie.completed":
            return self.on_movie_completed(event)

        self.on_other(event)

    def on_order_shipped(self, thin_event: OrderShippedPushedEvent):
        return self.on_other(thin_event)

    def on_order_delivery_attempted(
        self, thin_event: OrderDeliveryAttemptedPushedEvent
    ):
        return self.on_other(thin_event)

    def on_order_lost(self, thin_event: OrderLostPushedEvent):
        return self.on_other(thin_event)

    def on_movie_started(self, thin_event: MovieStartedPushedEvent):
        return self.on_other(thin_event)

    def on_movie_completed(self, thin_event: MovieCompletedPushedEvent):
        return self.on_other(thin_event)

    def on_other(self, thin_event: BaseThinEvent) -> NoReturn:
        raise NotImplementedError(f"No implemented handler for {thin_event.type}")


_EVENTS: List[ThinEvents] = [
    OrderShippedEvent(
        "evt_441", RelatedObject("ord_452", "order"), OrderShippedData("usps")
    ),
    OrderDeliveryAttemptedEvent(
        "evt_631",
        RelatedObject("ord_452", "order"),
        OrderDeliveryAttemptedData(True, 2, "front porch"),
    ),
    OrderLostEvent("evt_849", OrderLostData("Boulder")),
    MovieStartedEvent(
        "evt_509", RelatedObject("mov_261", "movie"), MovieStartedData("2025-06-01")
    ),
    MovieCompletedEvent(
        "evt_606", RelatedObject("mov_261", "movie"), MovieCompletedData("usr_223", 4)
    ),
]
_DATABASE = {
    **{e.id: e for e in _EVENTS},
    "ord_452": Order("ord_452", "2025-05-09", 5, 300, "2025-06-09"),
    "mov_261": Movie("mov_261", "Kung Fu Panda", 2008),
}

INCOMING_EVENTS = [e._dump() for e in _EVENTS]

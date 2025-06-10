# Cactus Docs

This is a full list of all the object types and event data that you could receive in your webhook handler, plus what's available on a Cactus client.

## Objects

We send events related to the the following object types:

```py
class Movie:
    id: str
    title: str
    release_year: int
```

```py
class Order:
    id: str
    created: str
    num_items: int
    cost_cents: int
    delivery_date: str
```

## Events

We sent events based on changes to certain object in our database.

### Event Types

With our new V2 event parsing system, we've got classes for every event type. We send you the "pushed" version and you can "pull" the full version. They're identical **except** the pull version includes the event's `Data`

| type                       | related object | data properties                               |
| -------------------------- | -------------- | --------------------------------------------- |
| `order.shipped`            | `Order`        | `shipping_service`                            |
| `order.delivery_attempted` | `Order`        | `success`, `attempt_num`, `delivery_location` |
| `order.lost`               | None           | `last_seen_city`                              |
| `movie.started`            | `Movie`        | `date`                                        |
| `movie.completed`          | `Movie`        | `user`, `rating`                              |

### Instance Methods

Each "pushed" event supports the following methods:

```py
def pull(self):
    """
    returns the full event type corresponding to this push event
    """

def fetch_related_object(self):
    """
    retrieves the related object by id, if applicable
    """
```

## Client

The client is a convenient way to fetch data about your CactusCorp integration. It's got the following shape:

```py
class CactusClient:
    def parse_event_v1(self, body: str) -> GenericThinEvent:
        ...

    def parse_event_v2(self, body: str) -> PushedThinEvents:
        ...

    def retrieve_event(self, id_: str) -> BaseThinEvent:
        ...

    def retireve_order(self, id_: str) -> Order:
        ...

    def retireve_movie(self, id_: str) -> Movie:
        ...
```

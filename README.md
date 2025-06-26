# Python Events Prototype

![](./misc/cactus.jpg)

Welcome to your first day at the Cactus Corporation! As you probably know, we've got two main product offerings: a shipping business and a movie streaming service.

To help our users keep track of the state of their account, we've recently launched CactusEvents. These are small webhook payloads that get sent when something changes in the user's account.

Initial user response has been good, but we strive to be the sharpest needle in the cactus and we haven't won yet. Specifically, we want to improve the experience of handling incoming events and are looking for fresh-eyed feedback.

## Docs

Cactus Corp sends "thin" events to our users, which contain minimal info but provide tools to fetch the full event data. The initial payload looks like this:

```json
{
  "id": "evt_123",
  "type": "order.shipped",
  "related_object": {
    "id": "ord_456",
    "type": "order"
  }
}
```

> [!IMPORTANT]
> Not all events types have a related object. See the table below for more information.

There's a corresponding `Event` object you can retrieve (or "pull") from the Cactus API. It's identical as the thin event, but it includes the event's `data`:

```json
{
  "id": "evt_123",
  "type": "order.shipped",
  "related_object": {
    "id": "ord_456",
    "type": "order"
  },
  "data": {
    "shipping_service": "usps"
  }
}
```

### Related Objects

We send events related to the the following object types:

```py
class Order:
    id: str
    created: str
    num_items: int
    cost_cents: int
    delivery_date: str
```

```py
class Movie:
    id: str
    title: str
    release_year: int
```

### Event Types

With our new V2 event parsing system, we've got classes for every event type. We send you the "pushed" version and you can "pull" the full version. They're identical **except** the pull version includes the event's `Data`

| type                       | related object | data properties                               |
| -------------------------- | -------------- | --------------------------------------------- |
| `order.shipped`            | `Order`        | `shipping_service`                            |
| `order.delivery_attempted` | `Order`        | `success`, `attempt_num`, `delivery_location` |
| `order.lost`               | None           | `last_seen_city`                              |
| `movie.started`            | `Movie`        | `date`                                        |
| `movie.completed`          | `Movie`        | `user`, `rating`                              |

#### Instance Methods

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

### Client

The CactusClient is a convenient way to fetch data from CactusCorp. It handles authentication, retries, etc. It's got the following shape:

```py
class CactusClient:
    @deprecated
    def parse_event_v1(self, body: str) -> GenericThinEvent:
        ...

    def parse_event_v2(self, body: str) -> PushedThinEvents:
        ...

    def retrieve_event(self, id_: str) -> BaseThinEvent:
        ...

    def retrieve_order(self, id_: str) -> Order:
        ...

    def retrieve_movie(self, id_: str) -> Movie:
        ...
```

## Part 1

Today, you'll be using your cactus expertise to help a user fix bugs in their webhook handling code. It's been throwing runtime errors and they're struggling to resolve them. They've also been ignoring a lot of in-editor warnings, so that's probably related.

Please:

1. Swap `parse_event_v1()` to `parse_event_v2()`.
2. Remove manual `cast` calls.
3. Resolve any type errors.
4. Resolve any runtime errors.
5. Add a new handler branch for the `movie.completed` event. It should print the user's rating and the movie's title. Bear in mind that some data is on the event itself while other data is on the related object.

## Part 2

In the pursuit of even better event handling, we're working on a prototype `CactusHandler` that will make event handling _even_ easier. We're focusing on eliminating the manual `cast`s and abstracting away some of the complexity that comes with handling events.

It's an inheritance-based design. The `handle` function takes the incoming request body and calls the matching callback. For instance:

```py
from cactus_sdk import CactusHandler

class MyHandler(CactusHandler):
    def on_some_event(self, thin_event: SomePushedEvent):
        print('handling "some.event"!')

    def on_other(self, thin_event: BaseThinEvent):
        print('handling unrecognized event')

MyHandler().handle('{"type": "some.event"}')
```

For part 2, we'd like to migrate our handler from part 1 to this newer style and see how they compare. When you're done, we'll talk about this new approach and compare the two.

## Part 2.5

Another design we've been considering is a decorator-based approach (instead of inheritance + overrides):

```py
from cactus_sdk import CactusHandler

handler = CactusHandler()

@handler.on_some_event
def my_custom_func(event: AccountCreated):
    print(event.created)
```

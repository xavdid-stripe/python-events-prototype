from typing import cast

from cactus_sdk import (
    INCOMING_EVENTS,
    CactusClient,
    CactusHandler,
    OrderDeliveryAttemptedEvent,
)

"""
Instructions:

1. Replace the `event_handler` with one built into `MyHandler`. It should behave exactly like the code from part 1. Consider starting by moving your existing code into the class's `on_other` method.
2. Ensure there are no runtime errors
3. remove the `event_handler` function; it's no longer needed
"""

client = CactusClient()


class MyHandler(CactusHandler):
    pass  # TODO: implement me!


handler = MyHandler()


def event_handler(body: str):
    thin_event = client.parse_event_v2(body)

    if thin_event.type == "order.shipped":
        order_id = thin_event.related_object.id
        order = client.retrieve_order(order_id)
        print(f"  Created a database record for {order.id} w/ {order.num_items=}")

    elif thin_event.type == "order.delivery_attempted":
        event = cast(OrderDeliveryAttemptedEvent, client.retrieve_event(thin_event.id))
        print(
            f"  Order {event.related_object.id} has been delivered after {event.data.attempt_num} attempt(s)!"
        )

    elif thin_event.type == "order.lost":
        event = thin_event.pull()
        print(
            f"  An order was last seen in {event.data.last_seen_city}... we have no additional information"
        )

    elif thin_event.type == "movie.started":
        movie_id = thin_event.related_object.id
        movie = client.retrieve_movie(movie_id)
        print(f"  Someone started watching {movie.title}")

    elif thin_event.type == "movie.completed":
        event = thin_event.pull()
        movie = thin_event.fetch_related_object()
        print(
            f"User {event.data.user} just finished {movie.title} ({movie.release_year}) and rated it {event.data.rating} stars."
        )

    else:
        raise ValueError(f'unhandled event with type "{thin_event.type}"')


if __name__ == "__main__":
    for idx, body_str in enumerate(INCOMING_EVENTS):
        print(f"\n== parsing event {idx}")
        try:
            handler.handle(body_str)
        except:
            print("  failed to handle:", body_str, "\n")
            raise

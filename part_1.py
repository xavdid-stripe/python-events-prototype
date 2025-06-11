from typing import cast

from cactus_sdk import INCOMING_EVENTS, CactusClient, OrderLostEvent, OrderShippedEvent

"""
Instructions:

1. Swap `parse_event_v1()` to `parse_event_v2()`.
2. Resolve any type errors.
3. Resolve any runtime errors.
4. Add a new handler branch for the `movie.started` event. It should print the user's rating and the movie' title. Bear in mind that some data is on the event itself while other data is on the related object.
"""

client = CactusClient()


def event_handler(body: str):
    # STEP 1: CHANGE THIS METHOD CALL TO `parse_event_v2`
    thin_event = client.parse_event_v1(body)

    if thin_event.type == "order.shiped":
        order_id = thin_event.related_object.id  # fixme
        order = client.retrieve_order(order_id)
        print(f"  Created a database record for {order.id} w/ {order.num_items=}")

    elif thin_event.type == "order.delivery_attempted":
        event = cast(OrderShippedEvent, client.retrieve_event(thin_event.id))
        print(
            f"  Order {event.related_object.id} has been delivered after {event.data.attempt_num} attempt(s)!"  # fixme
        )

    elif thin_event.type == "order.lost":
        order_id = thin_event.related_object.id  # fixme
        event = cast(OrderLostEvent, client.retrieve_event(thin_event.id))
        order = client.retrieve_order(order_id)
        print(
            f"  An order was last seen in {event.data.last_seen_city}... we have no additional information"
        )

    elif thin_event.type == "movie.started":
        movie_id = thin_event.related_object.id  # fixme
        movie = client.retrieve_order(movie_id)
        print(f"  Someone started watching {movie.title}")  # fixme

    else:
        raise ValueError(f'unhandled event with type "{thin_event.type}"')


if __name__ == "__main__":
    for idx, body_str in enumerate(INCOMING_EVENTS):
        print(f"\n== parsing event {idx}")
        try:
            event_handler(body_str)
        except:
            print("  failed to handle:", body_str, "\n")
            raise

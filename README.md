# Python Events Prototype

![](./misc/cactus.jpg)

Welcome to your first day at the Cactus Corporation! As you probably know, we've got two main product offerings: a shipping business and a movie streaming service.

To help our users keep track of the state of their account, we've recently launched CactusEvents. These are small webhook payloads that get sent when something changes in the user's account.

Initial user response has been good, but we strive to be the sharpest needle in the cactus and we haven't won yet. Specifically, we want to improve the experience of handling incoming events and are looking for fresh-eyed feedback.

Cactus Corp sends "thin" events to our users, which contain minimal info but provide tools to fetch the full event data. You can read more in the `DOCS.md` file.

## Part 1

Our webhook handler has been throwing runtime errors. We've been ignoring a lot of in-editor warnings, so that's probably related.

Can you use the new parsing method (`parse_event_v2()`) and remove all the type checker errors (noted by `fixme` comments) and runtime errors? Also, we don't want any of those manual `cast` calls - all the types should be present in the data.

Lastly, we'd love to handle events with the type `movie.completed`. Print out what rating the user gave and the title of the movie.

## Part 2

In the pursuit of even better event handling, we're working on a prototype `CactusHandler` that will make event handling _even_ easier. We're focusing on eliminating the manual `cast`s and abstracting away some of the complexity that comes with handling events.

It's an inheritance-based design. The `handle` function takes the incoming request body and calls the matching callback. For instance:

```py
from cactus_sdk import CactusHandler

class MyHandler(CactusHandler):
    def on_some_event(self, thin_event: SomePushedEvent):
        print('handling some.event!')

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

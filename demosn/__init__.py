"""This module contains multiple demos showing how to interact with the tags.
All demos assume that a working and turned on tag is close to your raspberry pi.
A general note, if the connections seem very slow, check if another user accidentaly is
already connected to the tag you are trying to work with.
They are all prefilled with one specific tag-ma. This will have to be changed to the
MAC-adress your current tag has. Your current tag-MAC has to be inserted into the get_tag_by_mac() method.


All demos are strucutred in a similar way to another.
The first step is always to create a new asyncio eventloop in which the whole communication will
be handled.
On the mainloop the run_until_complete method gets called and this method gets the hub.discover_tags() callback,
with a 5-second timeout as parameter.
When all the tags in the area are discovered, one of them get selected by the MAC-adress 
you provide.

On this selected tag all special operations, which are to be shon in a given demo, are executed.

So in general the loop is:
1. Create an Event-loop.
2. Find the tags near to you.
3. Grab one of the found tags by the MAC-adress.
4. Do the special operation you want a demonstration of. 
"""
###
FAQ
###


Is this a good idea?
--------------------

I don't know! I think it's interesting. I also think it should be done in a way
that doesn't require too much investment and risk, which is why I chose to do
it in a way that can be transparently (or explicitly if necessary) translated
back into "normal" ``unittest.TestCase``\s.

I think the latter is also a good demo of what you can do with import hooks
(path hooks), which can be confusing or magick-y but hopefully also do some
good.


Why does it only support transformation in Python 3.3?
------------------------------------------------------

Mostly since the Python import stack has mostly been done and redone a few
times over its lifetime, most recently in the form of ``importlib``. Python
3.3 has a bunch of useful things that make it easy to do what ``Ivoire`` needs
to do. Until I get a chance to try out the backports of it, it's going to need
to be Python 3.3+.


This isn't like RSpec.
----------------------

You're right, it probably isn't. To be honest, I haven't used RSpec much
personally, but I respect that it makes a few Ruby programmers I know excited
about testing, and I also like the way its tests look, so I figure there may be
some benefit in having something that imitates it in some small way.

If there's something specific that you think should be implemented though, feel
free to implement or suggest it!


That last one wasn't a question.
--------------------------------

Well boo you.


What are some good complimentary libraries to use?
--------------------------------------------------

Michael Foord's `mock <http://www.voidspace.org.uk/python/mock/>`_, which is 
now in the standard library starting with Python 3.3 as the ``unittest.mock``
library.

I'm also keeping an eye on things like `vcrpy
<https://github.com/kevin1024/vcrpy>`_, which I've seen lots of suites use in
Ruby.


Where's all the monkey patching?
--------------------------------

There is none. This is a piece of RSpec I don't like. It works in Ruby, where
the surrounding culture seems OK with it, but it's not something that's
generally done in Python, and though this is an imitation of a Ruby library, I
very much am in favor of sticking to idiomatic Python when doing so.

That said, though I don't recommend it, there are RSpec imitation libraries in
Python that do do the monkey patching, and if you look around you should be
able to find one.


Why didn't you build on top of more of the objects unittest already provides?
-----------------------------------------------------------------------------

It was quicker to prototype by building from scratch. If this has any success,
things will ultimately be moved to be built more on top of ``unittest``, at
least wherever that's feasible. (It's not feasible to use
``unittest.TestCase.run`` for instance.)


How come the README doesn't have some cool lineart in it?
---------------------------------------------------------

I don't know but if you have one please send it over, I love me a good piece of
lineart as much as the next guy.
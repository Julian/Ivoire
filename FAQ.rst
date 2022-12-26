###
FAQ
###


Is this a good idea?
--------------------

I don't know! I think it's interesting. I also think it should be done in a way
that doesn't require too much investment and risk, which is why I chose to do
it in a way that also can be transparently (or explicitly if necessary)
translated back into "normal" ``unittest.TestCase``\s, so that existing tools
can make use of the specs.

For what it's worth, I think the latter is also a good demo of a simple thing
you can do with import hooks (path hooks), which can be confusing or magick-y
but hopefully also do some good.

To be a bit more specific, I like the renaming and refocusing that BDD tries to
promote, and that's a thing that just adding new vocabulary like ``describe``
and ``it`` can accomplish in a small way. That being said, Python isn't
as suited for writing DSLs in it's own syntax as much as Ruby is.

In Ivoire's standalone mode this means that specs suffer from some pretty big
problems if you're not careful. Since ``with`` statements don't introduce
new scopes, your tests aren't isolated at the language level from each other,
so you need to be extra careful there. This is a non-issue in transformation
mode, thankfully (though that has other smaller disadvantages).


Why does it only support transformation in Python 3.3?
------------------------------------------------------

Mostly since the Python import stack has been done and redone a few times over
its lifetime, most recently in the form of ``importlib``. Python 3.3 has a
bunch of useful things that make it easy to do what Ivoire needs to do without
reimplementing things like ``__import__``. So, until I get a chance to try out
the backports of ``importlib``, it's going to need to be Python 3.3+ for that.


This isn't like RSpec.
----------------------

You're right, it probably isn't. To be honest, I haven't used RSpec much
personally, but I respect that it makes a few Ruby programmers I know excited
about testing, and I also like the way its tests look, so I figure there may be
some benefit in having something that imitates it in even some small way.

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


How come the README doesn't have some cool lineart in it?
---------------------------------------------------------

I don't know but if you have some please send it over. I love me a good piece
of lineart as much as the next guy.

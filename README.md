ideawheel
=========

A wheel of ideas for creators.  Build ideas up from stubs and then post creative
works inspired by those ideas to share with other creators.

This is a work in progress; issues are set up for an [Alpha milestone][alpha]

Dependencies
------------
* Python and pip, or a virtualenv with the same
* SQLite3
* Make
* libssl-dev (needed for building scrypt)

Developing
----------

    make deps
    make basedb
    make devserver

Hack away!  Be sure to run `make check` before creating a pull-request to ensure
that tests pass, flake8 is happy, and code coverage stays at a reasonable level.


Developing
----------

Ideawheel is totally open to pull requests from anyone.  Get in touch through
Github, email, or join us at #ideawheel on Freenode.

[alpha]: https://github.com/OpenFurry/ideawheel/milestones/Alpha

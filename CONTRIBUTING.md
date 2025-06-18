
Contributing code
=================

How to contribute
-----------------

The preferred way to contribute to jams is to fork the 
[main repository](http://github.com/marl/jams/) on
GitHub:

1. Fork the [project repository](http://github.com/marl/jams):
   click on the 'Fork' button near the top of the page. This creates
   a copy of the code under your account on the GitHub server.

2. Clone this copy to your local disk:

          $ git clone git@github.com:YourLogin/jams.git
          $ cd jams 

3. Create a branch to hold your changes:

          $ git checkout -b my-feature

   and start making changes. Never work in the ``master`` branch!

4. Work on this copy on your computer using Git to do the version
   control. When you're done editing, do:

          $ git add modified_files
          $ git commit

   to record your changes in Git, then push them to GitHub with:

          $ git push -u origin my-feature

Finally, go to the web page of the your fork of the jams repo,
and click 'Pull request' to send your changes to the maintainers for
review. This will send an email to the committers.

(If any of the above seems like magic to you, then look up the 
[Git documentation](http://git-scm.com/documentation) on the web.)


Note
----
This document was gleefully borrowed from [scikit-learn](http://scikit-learn.org/).

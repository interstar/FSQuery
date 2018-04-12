
## FSQuery (File System Query)

Working with the file system in Python isn't exactly difficult.

But it *is* verbose. And a low level way of talking to a complex tree of directories and files of different types.

FSQuery is a tiny Python library inspired by JQuery designed to let you query and manipulate a tree in the file system the way JQuery lets you query and manipulate the DOM.

### Quickstart


### Things you can do with FSQuery 

Create a query starting at a path and list it

        from fsquery import FSQuery

        fsq = FSQuery(path)
        for n in fsq :
            print n


Find *files* that match a particular criteria

        fsq = FSQuery(path).Match(".js$")
        for n in fsq :
            print n


Note that FSQuery matches using an ordinary regex, so you can use regex elements in it. But be careful not to put bad regex in, it will crash.

Add a FileOnly() call, to constrain the output to show only files (not directories)

        fsq = FSQuery("../..").Match(".js$").FileOnly()  
        for n in fsq :
            print n

You can also explicitly match just file extensions.

        fsq = FSQuery("../..").Ext("css").FileOnly()  
        for n in fsq :
            print n

Filter out a directory you aren't interested in, using NoFollow.

        fsq = FSQuery("../..").Match(".js$").NoFollow("vendor").FileOnly()  
        for n in fsq :
            print n


Finally, of course, it's very useful (though somewhat slow) to be able to look inside the files and see what they contain.

        fsq = FSQuery("../..").NoFollow("vendor").Ext("py").Contains("GNU Lesser General Public License").FileOnly()
        for n in fsq :
            print n.abs


Note that you can add as many NoFollows and Matches and Contains as you like. NoFollows are filters that are only applied to directories. Matches and Contains are filters that are only applied to files. Note also that, although you have added a FileOnly() to a query this doesn't affect the pattern matches on the directory names. 

Note also that if you add two Ext() constraints these will fight (no file can have two extensions at the same time) and your query will return nothing.


### FSNodes

From the previous examples, you'll notice that what is returned by FSQuery are FSNodes. FSNodes provide several further useful attributes and methods.

`FSNode.abs` is the absolute name of the file or node. 

Eg.

        fsq = FSQuery("../..").Match(".js$").NoFollow("vendor").FileOnly()  
        for n in fsq :
            print n.abs
            
will lists the returned nodes as ordinary text (as if running `find` in Unix)

`FSNode.open_file` will, if the FSNode is a file, open it for reading and return a file handle. It throws an exception if the FSNode is a directory.

Eg.

        fsq = FSQuery("../..").NoFollow("vendor").Ext("py").FileOnly()
        for n in fsq :
            print n.abs
            for line in n.open_file() :
                print line.rstrip()
            print "______________"
     



`FSNode.children()` will return the immediate children of the node.

`FSNode.spawn_query()` creates a new FSQuery, starting at this FSNode. 


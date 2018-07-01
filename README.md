
## FSQuery (File System Query)

Working with the file system in Python isn't exactly difficult.

But it *is* verbose. And a low level way of talking to a complex tree of directories and files of different types.

FSQuery is a tiny Python library inspired by JQuery designed to let you query and manipulate a tree in the file system the way JQuery lets you query and manipulate the DOM.

### Quickstart

Install from PyPI

    pip install fsquery 


[On PyPI](https://pypi.org/project/fsquery/)
 
### Things you can do with FSQuery 

Create a query starting at a path and list it

        from fsquery import FSQuery

        fsq = FSQuery(path)
        for n in fsq :
            print n

When you iterate through an `FSQuery`, you get objects of class `FSNode` back. FSNodes have a useful `.abs` property which is the full path name of the file or directory they represent.


Find *files* that match a particular criteria

        fsq = FSQuery(path).Match(".js$")
        for n in fsq :
            print n.abs


Note that FSQuery matches using an ordinary regex, so you can use regex elements in it. But be careful not to put bad regex in, it will crash.

Add a FileOnly() call, to constrain the output to show only files (not directories)

        fsq = FSQuery(path).Match(".js$").FileOnly()  
        for n in fsq :
            print n.abs

You can also explicitly match just file extensions.

        fsq = FSQuery(path).Ext("css").FileOnly()  
        for n in fsq :
            print n.abs

Filter out a directory you aren't interested in, using NoFollow.

        fsq = FSQuery(path).Match(".js$").NoFollow("vendor").FileOnly()  
        for n in fsq :
            print n.abs


Finally, of course, it's very useful (though somewhat slow) to be able to look inside the files and see what they contain.

        fsq = FSQuery(path).NoFollow("vendor").Ext("py").Contains("GNU Lesser General Public License").FileOnly()
        for n in fsq :
            print n.abs


Note that you can add as many NoFollows and Matches and Contains as you like. NoFollows are filters that are only applied to directories. Matches and Contains are filters that are only applied to files. Note also that, although you have added a FileOnly() to a query this doesn't affect the pattern matches on the directory names. 

Note also that if you add two Ext() constraints these will fight (no file can have two extensions at the same time) and your query will return nothing.

### Command Liners

The FSQuery object has a `pp()` method which actually does the looping and printing for you.

This makes FSQuery useful for *one-liners* run directly on the command line like this.

        python -c 'from fsquery import FSQuery; FSQuery(".").Ext("html").FileOnly().pp()'



### FSNodes

`FSNode.changed()` returns a formatted time-stamp of when the file was last changed. (Uses `os.path.getmtime`)

`FSNode.open_file()` will, if the FSNode is a file, open it for reading and return a file handle. It throws an exception if the FSNode is a directory.

Eg.

        fsq = FSQuery(path).NoFollow("vendor").Ext("py").FileOnly()
        for n in fsq :
            print n.abs
            for line in n.open_file() :
                print line.rstrip()
            print "______________"
     


`FSNode.children()` will return a list of the immediate children of the node. (As new FSNodes)

`FSNode.spawn_query()` creates a new FSQuery, starting at this FSNode. 


### Processing and Shadowing

There's another way to process all the nodes in the query.

You can create a custom class to process the nodes, which has two methods : `process_dir` and `process_file`.

For example :

        class Processor :
            def process_dir(self,fsNode) :
                print("this is a dir : %s" % fsNode)
            def process_file(self,fsNode) :
                print("this is a file : %s" % fsNode)

        fsq.process_each(Processor())
        
This is potentially useful if you want to process files and directories differently (so you can't use FilesOnly or DirOnly in the query). And might be more elegant in certain situations. You can reuse the same Processor with different queries.

However, a far more radical, and very useful thing that you often want to do with directories of files is to make some kind of derivative "copy" or transformation of them. Here we use FSQuery's `shadow` functionality.

`shadow`, like `process_each` takes a custom processor class, and runs it through a query result.

However, when shadowing, FSQuery is not just iterating through the original query result, is is also building up an isomorphic, shadow result that is hooked on to a different root. At each step of the iteration, your Processor class is presented with the original FSNode from the original location, and a "shadow node", at an identical relative location, but from a different root.

Here's a simple example :

Say we have a simple directory structure hanging under `o`

    > find o
    o
    o/a
    o/a/c
    o/a/c/hello.txt
    o/b
    o/b/hello.txt
 

We now run the following example code :

        class Shadower :
        
            def process_dir(self,node,shadow_node) :
                print node.abs
                print shadow_node.abs
                print
                shadow_node.mk_dir()
                
            def process_file(self,node,shadow_node) :
                pass
                            
        fsq = FSQuery("o")
        fsq.shadow("x",Shadower())
        
The Shadower has two methods `process_dir` and `process_file` to handle directories and files directly. Currently `process_file` does nothing.

Note that these methods now take two arguments : the original node, and a new shadow_node created by the shadow functionality of FSQuery. When we call the `shadow` method of FSQuery, you see we give it two arguments. A new root directory, in this case, `x`, and an instance of the Shadower class.

Here's the result.

        PATH/o
        PATH/x
        
        PATH/o/a
        PATH/x/a
        
        PATH/o/a/c
        PATH/x/a/c
        
        PATH/o/b
        PATH/x/b

Here you see that the the paths in the shadow_node are the same as the path of the original node, except the root of the query `o` is now replaced by the alternative root `x`

We also called the method `mk_dir` on each shadow node, which conveniently created the appropriate directory under the new root `x`

        > find x
        x
        x/a
        x/a/c
        x/b

You'll see that this has successfully cloned the directory structure matching the query. It hasn't, of course, copied the files. Let's do that :

        class Shadower :
        
            def process_dir(self,node,shadow_node) :
                print node.abs
                print shadow_node.abs
                print
                shadow_node.mk_dir()
                
            def process_file(self,node,shadow_node) :
                content = node.open_file().read()
                shadow_node.write_file(shadow_node.abs,content)
                            
        fsq = FSQuery("o")
        fsq.shadow("x",Shadower())
  
 
We use two more convenience functions on FSNode, `open_file` to open the file represented by the node. And `write_file` to write to a file of that name. Now we see we've successfully cloned the directories.

        > find x
        x
        x/a
        x/a/c
        x/a/c/hello.txt
        x/b
        x/b/hello.txt

Of course, shadow is running through a standard FSQuery result, so if we had restricted that result, using our usual NoFollow, Match, or even Contains queries, we would be processing only that query result.

And, of course, you don't need to limit yourself to just copying one directory. Depending on your Shadower class, this can be used for a wide variety of functionality. 

## Known Issues

### Currently FSQuery ignores symbolic links. 

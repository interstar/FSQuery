import os
import re 

class FSNode :
    def __init__(self,path_s, depth=0) :
        self.abs = os.path.abspath(path_s)
        self.depth = depth

    def dirname(self) :
        "Path to this node"
        return os.path.dirname(self.abs)
    
    def basename(self) :
        "Filename or directory name"
        return os.path.basename(self.abs)
        
    def ext(self) : 
        "File extension, where separated by a . Returns an empty string if the file has no name"
        if not "." in self.basename() : return ""
        return self.basename().split(".")[-1]

    def isdir(self) :
        "True if this FSNode is a directory"
        return os.path.isdir(self.abs)

    def children(self) :
        "If the FSNode is a directory, returns a list of the children"
        if not self.isdir() : raise "FSQuery tried to return the children of a node which is not a directory : %s" % self.abs
        return [FSNode(self.abs + "/" + x,self.depth+1) for x in os.listdir(self.abs)]
        
    def spawn_query(self) :
        """Create a new FSQuery, starting from this node"""
        return FSQuery(self.abs)
        
    def write_file(self,fName,content) :
        """If this FSNode is a directory, write a file called fName containing content inside it"""
        if not self.isdir() : raise "FSQuery tried to add a file in a node which is not a directory : %s" % self.abs
        with open("%s/%s"%(self.abs,fName),"w") as f :
            f.write(content)
    
    def open_file(self) :
        """If this FSNode is a file, open it for reading and return the file handle"""
        if self.isdir() : raise "FSQuery tried to open a directory as a file : %s" % self.abse        
        return open(self.abs)
        
    def contains(self,pat) :
        r = re.compile(pat)
        with self.open_file() as f :
            for line in f :
                if r.search(line) :
                    return True
        return False
        
    def __str__(self) :
        return "[FSNode : %s (isdir? %s)]"% (self.abs, self.isdir())
            


class FSQuery :
    def __init__(self,root_s) :
        self.init_path = root_s
        self.dir_includes = []
        self.file_includes = []
        self.return_criteria = []
        
    def all(self, fsNode, filters) :
        for f in filters :
            if not f(fsNode) : return False
        return True
   
    def check_dir(self,fsNode) :
        return self.all(fsNode,self.dir_includes)
    
    def check_file(self,fsNode) :
        return self.all(fsNode,self.file_includes)
            
    def check_return(self,fsNode) :
        return self.all(fsNode,self.return_criteria)

    def make_file_include(self,f) :
        "Add the function f as a test for including the FSNode representing a file in the query results."
        self.file_includes.append(f)
        return self
        
    def make_dir_include(self,f) :
        """Add the function f as a test for including the FSNode representing a directory both during the query and in showing its results.

Directories excluded by this filter are not searched."""
        self.dir_includes.append(f)
        return self
    
    def make_return(self,f) :
        "Add the function f as a test for showing the FSNode in the final results. This has no effect "
        self.return_criteria.append(f)
        return self
        
    def walk(self,depth=0,fsNode=None) :
        """Note, this is a filtered walk"""
        if not fsNode :
            fsNode = FSNode(self.init_path,0)
            
        if fsNode.isdir() :
            if self.check_dir(fsNode) :
                if self.check_return(fsNode) :
                    yield fsNode                
                for n in fsNode.children() :
                    for n2 in self.walk(depth+1,n) :
                        if self.check_return(n2) :
                            yield n2
        else :
            if self.check_file(fsNode) :
                if self.check_return(fsNode) :
                    yield fsNode
        raise StopIteration
        
    def foreach(self,visitor) :
        for w in self.walk() :
            visitor(w)

    def process_each(self,visitor) :
        for w in self.walk() :
            if w.isdir() :
                visitor.process_dir(w)
            else :
                visitor.process_file(w)

    def __iter__(self) :
        return (w for w in self.walk())
                
    def clone(self) :
        q = FSQuery(self.init_path)
        q.dir_includes = self.dir_includes[:]
        q.file_includes = self.file_includes[:]
        q.return_criteria = self.return_criteria[:]
        return q
        
    # From here on are the normal methods you'd expect a user to call.
    
    def Match(self,pat) :
        r = re.compile(pat)
        def match(fsNode) :        
            return r.search(fsNode.basename())
        self.make_file_include(match)
        return self
    
    def Ext(self,ext) :
        return self.make_file_include(lambda n : n.ext() == ext)

    def Contains(self,pat) :
        return self.make_file_include(lambda n : n.contains(pat))
        
    def NoFollow(self,pat) :
        r = re.compile(pat)
        def match(fsNode) :
            bn = fsNode.basename()
            if bn == "" :
                bn = fsNode.abs
            return not r.search(bn)
        self.make_dir_include(match)
        return self
        
    def DirContains(self,f) :
        """ Matches dirs that have a child that matches filter f"""
        def match(fsNode) :
            if not fsNode.isdir() : return False 
            for c in fsNode.children() :
                if f(c) : return True
            return False
        return self.make_return(match)

    def FileOnly(self) :
        def match(fsNode) :
            return not fsNode.isdir()
        self.make_return(match)
        return self
        
    def DirOnly(self) :
        self.make_return(lambda fsn : fsn.isdir())
        return self
        

if __name__ == '__main__' :
    fsq = FSQuery("o")
    def f(x) : print(x)
    fsq.foreach(f)

    class Processor :
        def process_dir(self,fsNode) :
            print("this is a dir : %s" % fsNode)
            fsNode.write_file("new3.txt","This has been made properly")
        def process_file(self,fsNode) :
            pass
            
    fsq.NoFollow("b")        
    fsq.process_each(Processor())

    print "__________________________________________________------------------------------------------------------------"
    

    fsq = FSQuery("../..").NoFollow("vendor").FileOnly().Ext("css")
    for n in fsq :
        print n.abs, n.ext()
        
    print "----------------------------------------_______________________________---------------------------------------"
    

        
    fsq = FSQuery("../..").NoFollow("vendor").DirContains(lambda n : n.ext() == "py")
    for n in fsq :
        print n.abs
        if n.isdir() :
            print ["%s"%c.basename() for c in n.children()]
            

    print "----------------------------------------_______________________________---------------------------------------"
    fsq = FSQuery("../..").NoFollow("vendor").Ext("py").Contains("GNU Lesser General Public License").FileOnly()
    for n in fsq :
        print n.abs
        #for line in n.open_file() :
        #    print line.rstrip()
        #print "_________________________________________________________________________________________"
    
    

    

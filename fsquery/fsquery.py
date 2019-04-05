import os
import re 
import datetime

from shutil import copyfile

class CopyShadower :

    def process_dir(self,node,shadow_node) :
        print(("shadowing dir %s to %s " % (node.abs,shadow_node.abs)))
        shadow_node.mk_dir()
        
    def process_file(self,node,shadow_node) :
        print(("copying %s to %s" % (node.abs,shadow_node.abs)))
        copyfile(node.abs, shadow_node.abs)
        print("done")
        
class FSNode :
    def __init__(self,path_s, root, depth) :
        self.abs = os.path.abspath(path_s)
        self.depth = depth
        self.root=os.path.abspath(root)

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
        
    def relative(self) :
        return self.abs.replace(self.root,"")

    def ts_changed(self) :
        "TimeStamp of last changed time / date"
        return os.path.getmtime(self.abs)
        
    def changed(self) :
        "Formatted last changed time / date"
        return "%s"%datetime.datetime.fromtimestamp(self.ts_changed())
        
    def isdir(self) :
        "True if this FSNode is a directory"
        return os.path.isdir(self.abs)

    def islink(self) :
        "Is it a symbolic link?"
        return os.path.islink(self.abs)

    def children(self) :
        "If the FSNode is a directory, returns a list of the children"
        if not self.isdir() : raise Exception("FSQuery tried to return the children of a node which is not a directory : %s" % self.abs)
        return [FSNode(self.abs + "/" + x,self.root,self.depth+1) for x in os.listdir(self.abs)]
        
    def spawn_query(self) :
        """Create a new FSQuery, starting from this node"""
        return FSQuery(self.abs)
        
    def write_file(self,fullName,content) :
        with open(fullName,"w") as f :
            f.write(content)
            
    def add_file(self,fName,content) :
        """If this FSNode is a directory, write a file called fName containing content inside it"""
        if not self.isdir() : raise Exception("FSQuery tried to add a file in a node which is not a directory : %s" % self.abs)
        self.write_file("%s/%s"%(self.abs,fName),content)        
        

    def open_file(self) :
        """If this FSNode is a file, open it for reading and return the file handle"""
        if self.isdir() : raise Exception("FSQuery tried to open a directory as a file : %s" % self.abs)
        return open(self.abs, encoding='ISO-8859-1')

    def mk_dir(self) :
        """If this FSNode doesn't currently exist, then make a directory with this name."""
        if not os.path.exists(self.abs) :
            os.makedirs(self.abs)
        
    def contains(self,pat) :
        r = re.compile(pat)
        with self.open_file() as f :
            for line in f :
                if r.search(line) :
                    return True
        return False

    def get_child(self,pat) :
        if not self.isdir() : raise Exception("FSQuery tried to get a child in a node which is not a directory : %s" % self.abs)
        r = re.compile(pat)
        for c in self.children() :
            if r.search(c.basename()) : return c
        return False

    def contains_file(self,pat) :
        if not self.isdir() : raise Exception("FSQuery tried to check filenames in a node which is not a directory : %s" % self.abs)
        c = self.get_child(pat)
        if c : return True
        else : return False        
        
    def get_parent(self) :
        return FSNode(os.path.dirname(self.abs),self.root,self.depth-1)
        
    def clone(self,new_root) :
        return FSNode(new_root+"/"+self.relative(),new_root,self.depth)
        
    def __str__(self) :
        return "[<FSNode : %s , rel: %s , depth %s , isdir? %s>]"% (self.abs, self.relative(), self.depth, self.isdir())
            


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
            fsNode = FSNode(self.init_path,self.init_path,0)
            
        if fsNode.isdir() :
            if self.check_dir(fsNode) :
                if self.check_return(fsNode) :
                    yield fsNode                
                for n in fsNode.children() :
                    if n.islink() :
                        # currently we don't follow links
                        continue
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

    def shadow(self,new_root,visitor) :
        """ Runs through the query, creating a clone directory structure in the new_root. Then applies process"""
        for n in self.walk() :
            sn = n.clone(new_root)
            if n.isdir() :
                visitor.process_dir(n,sn)
            else :
                visitor.process_file(n,sn)

                
    def clone(self) :
        q = FSQuery(self.init_path)
        q.dir_includes = self.dir_includes[:]
        q.file_includes = self.file_includes[:]
        q.return_criteria = self.return_criteria[:]
        return q
 

    def pp(self) :
        for n in self.__iter__() :
            print((n.abs))

        
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
    from .fsquery import FSQuery, FSNode
    
    fsq = FSQuery("/home/USER/CODE").Ext("py").NoFollow("\.git").FileOnly()
    for node in fsq :
        print((node.abs))

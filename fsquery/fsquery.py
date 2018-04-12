import os
import re 

class FSNode :
    def __init__(self,path_s, depth=0) :
        self.abs = os.path.abspath(path_s)
        self.depth = depth

    def dirname(self) :
        return os.path.dirname(self.abs)
    
    def basename(self) :
        return os.path.basename(self.abs)

    def isdir(self) :
        return os.path.isdir(self.abs)

    def children(self) :
        return [FSNode(self.abs + "/" + x,self.depth+1) for x in os.listdir(self.abs)]
        
    def spawn_query(self) :
        return FSQuery(self.abs)
        
    def add_file(self) :
        if self.isdir() : raise "FSQuery tried to add a file in a node which is not a directory : %s" % self.abs
        with open(fsNode.abs + "/new2.txt","w") as f :
            f.write("this is new")
        
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
        self.file_includes.append(f)
        return self
        
    def make_dir_include(self,f) :
        self.dir_includes.append(f)
        return self
    
    def make_return(self,f) :
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
        
    def Match(self,pat) :
        r = re.compile(pat)
        def match(fsNode) :        
            return r.search(fsNode.basename())
        self.make_file_include(match)
        return self
    
    def NoFollow(self,pat) :
        r = re.compile(pat)
        def match(fsNode) :
            bn = fsNode.basename()
            if bn == "" :
                bn = fsNode.abs
            return not r.search(bn)
        self.make_dir_include(match)
        return self

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
            with open(fsNode.abs + "/new2.txt","w") as f :
                f.write("this is new")
        def process_file(self,fsNode) :
            pass
            
    fsq.NoFollow("b")        
    fsq.process_each(Processor())

    fsq = FSQuery("../..").Match(".js$").FileOnly()  
    for n in fsq :
        print n
        

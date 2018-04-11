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
        
    def __str__(self) :
        return "%s (%s)"% (self.abs, self.isdir())
            


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
    fsq = FSQuery("/mnt/f/old_development/small_experiments").NoFollow("sudoku").NoFollow("test-rn")
    fsq2 = fsq.clone()
    fsq.FileOnly().Match(".py$")
    fsq2.DirOnly().make_dir_include(lambda fsn : fsn.depth < 3)
    def f(x) : print(x)
    fsq.foreach(f)
    print("------------------------------------------------")
    fsq2.foreach(f)
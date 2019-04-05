from setuptools import setup

setup(name='fsquery',
      version='0.2.1',
      description='File System Query.       Working with the file system is too verbose. Let\'s make it more like JQuery.',
      long_description="""File System Query. 

Working with the file system is too verbose. 
      
FSQuery provides a way of thinking about the file system inspired by JQuery.
      
An FSQuery is created from a particular director with a number of terms added as modifiers. 
      
A simple example : 
      
    from fsquery import FSQuery
    
    fsq = FSQuery("/home/myaccount").NoFollow(".git").Ext(".py").FileOnly()
    for n in fsq :
        print(n.abs)
      

This FSQuery searches all directories under /home/myaccount, except directories with ".git" in their name.

It matches files with a ".py" extension. And the FileOnly() suppresses returning directories.

See more documentation on the [GitHub page](https://github.com/interstar/FSQuery).
      """,
      long_description_content_type='text/markdown',
      url='https://github.com/interstar/FSQuery',
      author='Phil Jones',
      author_email='interstar@gmail.com',
      license='MIT',
      packages=['fsquery'],
      classifiers=['Development Status :: 3 - Alpha',
                   'Intended Audience :: Developers'],
      zip_safe=False)

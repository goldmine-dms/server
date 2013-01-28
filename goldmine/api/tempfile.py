#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import string
import datetime
import codecs

from goldmine import *
from goldmine.db import db
from goldmine.models import *
from goldmine.controller import *

@apimethod.auth
def get(filename):
    """
    Requests a temporary file
    """
    
    directory = get_user_dir(user)
    
    try:
        return file(directory + valid_filename(filename), 'r').read()
    except Exception, e:
        raise TypeError(e.strerror)


@apimethod.auth
def pull(filename):
    """
    Requests a temporary file and deletes it afterwards
    """
    
    directory = get_user_dir(user)
    
    try:
        data = file(directory + valid_filename(filename), 'r').read()
        os.unlink(directory + valid_filename(filename))
        return data
    except Exception, e:
        raise TypeError(e.strerror)

@apimethod.auth
def info(filename):
    """
    Requests info about a temporary file
    """
    
    directory = get_user_dir(user)
    
    try:
        stat = os.stat(directory + valid_filename(filename))
        atime = stat.st_atime
        mtime = stat.st_mtime
        ctime = stat.st_ctime
        size = stat.st_size

        return {
            "name": filename, "id": filename,
            "accessed": str(datetime.datetime.fromtimestamp(atime)),
            "modified": str(datetime.datetime.fromtimestamp(mtime)),
            "created": str(datetime.datetime.fromtimestamp(ctime)),
            "size": size
        }


    except Exception, e:
        raise TypeError(e.strerror)
        
@apimethod.auth
def all():
    """
    List of all temporary files
    """
    directory = get_user_dir(user)
    files = os.listdir(directory)
    
    return [{"name": x, "id": x} for x in files]
    

@apimethod.auth
def create(data, filename):
    """
    Create a temporary file for the user
    
    data:       (string)    The data to write to the file
                (list)      A list of data inputs to each of the files 
                            mentioned in filename
                            
    filename:   (string)    The name of the file to write
                (list)      A list of filenames
                
    The filename is modified if it contains illegal characters outside
    of the sets: [a-z], [A-Z], [0-9] and ("-", "_", ".")
    """

    success_files = []
    
    directory = get_user_dir(user)
    
        
    if type(filename) in (unicode, str):
        data = [data]
        filename = [filename]
    
    if len(filename) is not len(data):
        raise TypeError("Data and filename must have the same number of elements")
        
    for idx, data_to_write in enumerate(data):

        # only valid filenames
        filename[idx] = valid_filename(filename[idx])
          
        f = codecs.open(directory + filename[idx], "w", "utf-8")
        f.write(data_to_write)
        f.close()
        
        success_files.append(filename[idx])
        
    return success_files

@apimethod.auth
def delete(filename):
    """
    Delete a temporary file
    """
    
    directory = get_user_dir(user)
    
    try:
        os.unlink(directory + valid_filename(filename))
    except Exception, e:
        raise TypeError(e.strerror)
        
    
def get_user_dir(user):
    
    dir_base = config()["tempfile"]["directory"]
    dir_uuid = str(user.id)
       
    if not dir_base.endswith(os.sep):
        dir_base += os.sep
        
    directory = dir_base + dir_uuid + os.sep
    
    if not os.path.exists(directory):
        os.makedirs(directory)

    return directory


def valid_filename(filename):
    valid_chars = "-_.%s%s" % (string.ascii_letters, string.digits)
    return ''.join(c for c in filename if c in valid_chars) 

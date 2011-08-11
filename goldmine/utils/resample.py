#!/usr/bin/env python
#-*- coding:utf-8 -*-

import numpy

def mean_binning(data, stepsize=None, numbins=None, dim=None, 
                       mastercolumn=0, mastermax=None, mastermin=None,
                       nanthreshold=0.5, supersample=False):
    """ Do a mean binnning of the dataset  
    
    data:           a numpy 2d array
    stepsize:       the size of the steps in the new rebinning
                        (this mode centers the endpoints to get 
                        a fixed number bins)
    numbins:        the number of bins (overrides stepsize)
    dim:            the dimension to do the binning along (None means largest)
    mastercolumn:   the column to use as master (default 0)
    mastermax:      the maximum value needed
    mastermin:      the minimum value needed
    nanthreshold:   the amount of nans in a bin to make it a nan
    supersample:    interpolate data between samples
    
    Stepsize or numbins must be provided.
    """

    if data.ndim != 2:
        raise TypeError("Data must be 2-d")

    # if autodim, find largest dimension
    if dim is None:
        dim = 0 if numpy.size(data, 0) > numpy.size(data, 1) else 1
        
    datalen = numpy.size(data, dim)
        
    if dim == 1:
        data = data.transpose()
        
    if stepsize is None and numbins is None:
        raise Exception("Must provide either stepsize or numbins")
        
    # Sort data on mastercolumn
    sortorder = data.argsort(axis=0)[:, mastercolumn]
    data = data[sortorder,:]
    
    if mastermin is None:
        mastermin = data[0,0]
    
    if mastermax is None:
        mastermax = data[-1,0]
    
    # Using a stepsize
    if stepsize is not None:
        numbins = ((mastermax - mastermin)/stepsize) + 1
        extra = ((numbins - int(numbins))*stepsize)/2
        mastermin += extra
        mastermax -= extra
        numbins = int(numbins)
        
    # If trying to supersample, and supersampling not activated,
    # return the original dataset
    if supersample is False and numbins > datalen:
        if dim == 1:
            data = data.transpose()
        return data
        
    (bins, binwidth) = numpy.linspace(mastermin, mastermax, num=numbins, retstep=True)
    
    binhalf = binwidth/2.0
    
    master = data[:, mastercolumn]
    
    outdata = numpy.empty([numbins,numpy.size(data, 1)])
    
    
    localend = 0
    
    for [idx, bin] in enumerate(bins):
        (binmin, binmax) = (bin-binhalf, bin+binhalf)


        # Non-optimized:       
        #extract = numpy.all([(master > binmin),(master <= binmax)], 0)
        #local = data[extract,:]

        # Optimized extract of values, due to previous sort     
        localstart = localend
        while localend < datalen and data[localend, 0] <= binmax:
            localend += 1 
        local = data[localstart:localend, :]
                   
        
        sums = numpy.nansum(local, 0)
        
        nans = numpy.isnan(local)
        nancount = (nans == True).sum(0)
        nonnancount = (nans == False).sum(0)
        
        row = sums/nonnancount
        
        nancover = nancount.astype(numpy.float)/(nonnancount+nancount)
        nanindex = (nancover > nanthreshold)
        
        # if the nancover is more than threshold, 
        # convert that point into a NaN
        row[nanindex] = numpy.NaN
        
        # set the index element to the bin instead of mean master value
        # for large bins for evenly spaced data, these should be almost the 
        # same, except for the endpoint
        row[0] = bin
        
        outdata[idx,:] = row
    
    if dim == 1:
        outdata = outdata.transpose()

    return outdata



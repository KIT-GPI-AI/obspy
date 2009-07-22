# -*- coding: utf-8 -*-


class Stats(dict, object):
    """
    A stats class which behaves like a dictionary.
    
    You may the following syntax to change or access data in this class:
      >>> stats = Stats()
      >>> stats.network = 'BW'
      >>> stats['station'] = 'ROTZ'
      >>> stats.get('network')
      'BW'
      >>> stats['network']
      'BW'
      >>> stats.station
      'ROTZ'
      >>> x = stats.keys()
      >>> x.sort()
      >>> x[0:3]
      ['network', 'station']
    """

    def is_attr(self, attr, typ, default, length=False, assertation=False,
                verbose=False):
        """
        True if attribute of certain type and optional length exists
        
        Function is probably most useful for checking if necessary
        attributes are provided, e.g. when writing seismograms to file

        >>> p=Stats()
        >>> p.julsec = 0.0
        >>> p.is_attr('julsec',float,1.0)
        True
        >>> p.is_attr('julsec',int,123)
        False
        >>> p.julsec
        123
        """
        # Check if attribute exists
        if not attr in self.keys():
            if assertation:
                assert False, "%s attribute of Seismogram required" % attr
            if verbose:
                print "WARNING: %s attribute of Seismogram missing",
                print "forcing", attr, "=", default
            setattr(self, attr, default)
            return False
        # Check if attribute is of correct type
        if not isinstance(getattr(self, attr), typ):
            if assertation:
                msg = "%s attribute of Seismogram not of type %s"
                assert False, msg % (attr, typ)
            if verbose:
                msg = "WARNING: %s attribute of Seismogram not of type %s"
                print msg % (attr, typ),
                print "forcing", attr, "=", default
            setattr(self, attr, default)
            return False
        # Check if attribute has correct length
        if (length):
            if (len(getattr(self, attr)) != length):
                if assertation:
                    msg = "%s attribute of Seismogram is != %i"
                    assert False, msg % (attr, length)
                if verbose:
                    msg = "%s attribute of Seismogram is != %i"
                    print msg % (attr, length)
                setattr(self, attr, default)
                return False
        # If not test failed
        return True

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, dict.__repr__(self))

    def __setitem__(self, key, value):
        super(Stats, self).__setattr__(key, value)
        return super(Stats, self).__setitem__(key, value)

    def __getitem__(self, name):
        return super(Stats, self).__getitem__(name)

    def __delitem__(self, name):
        super(Stats, self).__delattr__(name)
        return super(Stats, self).__delitem__(name)

    __getattr__ = __getitem__
    __setattr__ = __setitem__
    __delattr__ = __delitem__

    def copy(self, init={}):
        return Stats(init)

    def __deepcopy__(self, *args, **kwargs):
        st = Stats()
        st.update(self)
        return st


if __name__ == '__main__':
    import doctest
    doctest.testmod(exclude_empty=True)

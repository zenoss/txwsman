class BaseStrategy(object):

    def __init__(self):
        self._item_count = 0

    @property
    def count_summary(self):
        return '{0} items'.format(self._item_count)



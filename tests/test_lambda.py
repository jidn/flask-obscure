import itertools
import pytest
import helper
from helper import FILTERS, METHODS, make_filters


@pytest.mark.parametrize('filter_,method',
                         itertools.product(FILTERS, METHODS))
def test_all_filters(filter_, method):
    filters = make_filters(FILTERS, method)
    func = __builtins__[filter_[3:]]
    assert func(254) == filters[filter_](254)

from .marshal_flyer import marshal_flyer
from .example_flyer import EXAMPLE_FLYER, EMPTY_FLYER, EMPTY_PAGE_FLYER


def marshal_example_flyers():
    marshal_flyer(EXAMPLE_FLYER, 'test_example_flyer')
    marshal_flyer(EMPTY_FLYER, 'test_empty_flyer')
    marshal_flyer(EMPTY_PAGE_FLYER, 'test_empty_page_flyer')


if __name__ == '__main__':
    marshal_example_flyers()

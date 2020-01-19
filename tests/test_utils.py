from csvblend import utils


def test_hash_function():
    result0 = utils.hash_function(" 於 some Va  l  ue ")
    assert result0 == "3801952491"
    result1 = utils.hash_function("")
    assert result1 == "0"
    result2 = utils.hash_function(" ")
    assert result2 == "3916222277"

from tomlfunc import read_toml, get_inputs
from workflow import kaizu_generation

def test_1():
  assert True

def test_read_toml():
    a = read_toml("./test.toml")
    assert a != None
    assert a["title"] == "scopyon"
    #print(a["generation"])
    assert a["generation"]["inputs"]["num_samples"] == 1
    assert a["generation"]["outputs"]["artifacts"] == "./artifacts"

def test_get_inputs():
    a = get_inputs("./test.toml")
    assert a["num_samples"] == 1

def test_kaizu_generation():
    a = get_inputs("./test.toml")
    output = kaizu_generation(a)
    assert type(output) == str

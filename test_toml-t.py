from tomlfunc import read_toml
from function_list import kaizu_generation

def test_1():
  assert True

def test_read_toml():
    a = read_toml("./params.toml")
    assert a != None
    assert a["title"] == "scopyon"
    print(a["generation"]["inputs"])
    #print(a["generation"])
    assert a["generation"]["inputs"]["num_samples"] == 1
    assert a["generation"]["outputs"]["artifacts"] == "./artifacts"

# def test_get_inputs():
#     a = read_toml("./params.toml")
#     assert a["generation"]["inputs"]["num_samples"] == 1
#     # a = read_toml("./params.toml")
#     # assert a["num_samples"] == 1
    
def test_kaizu_generation():
    a = read_toml("./params.toml")
    output = kaizu_generation(a)
    assert type(output) == str

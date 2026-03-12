import pydantic
print(f"Pydantic Version: {pydantic.VERSION}")
try:
    from pydantic import BaseModel
    class Test(BaseModel):
        foo: str
    t = Test(foo="bar")
    if hasattr(t, "model_dump"):
        print("model_dump exists")
    else:
        print("model_dump DOES NOT exist")
except Exception as e:
    print(f"Error: {e}")

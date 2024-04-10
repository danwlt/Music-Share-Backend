from fastapi import FastAPI
from bson.objectid import ObjectId
import pymongo

app = FastAPI()

myclient = pymongo.MongoClient(
    "mongodb://root:secret@mongodb:27017/?retryWrites=true&w=majority")
mycol = myclient["music_share"]
cursor = mycol["posts"]


def check_elements(list1, list2):
    return set(list1).issubset(set(list2))


@app.post("/post")
async def add_post(values: dict):
    try:
        expected_keys = {"username", "song", "artist", "imgLink"}
        if values.keys() == expected_keys:
            values["likes"] = 0
            cursor.insert_one(values)
            return {"message": "success"}
        else:
            return {"message": "error"}
    except Exception as e:
        print(e)
        return {"message": "error"}


@app.post("/like")
async def add_like(values: dict):
    try:
        expected_keys = {"id"}
        if values.keys() == expected_keys:
            filter = {"_id": ObjectId(values["id"])}
            update = {"$inc": {"likes": 1}}
            cursor.update_one(filter, update)
            return {"message": "success"}
        else:
            return {"message": "error"}
    except Exception as e:
        print(e)
        return {"message": "error"}


@app.post("/unlike")
async def add_like(values: dict):
    try:
        expected_keys = {"id"}
        if values.keys() == expected_keys:
            filter = {"_id": ObjectId(values["id"])}
            update = {"$inc": {"likes": -1}}
            cursor.update_one(filter, update)
            return {"message": "success"}
        else:
            return {"message": "error"}
    except Exception as e:
        print(e)
        return {"message": "error"}


@app.get("/getPost/{request_count}")
async def get_posts(request_count: int):
    skip_count = (request_count - 1) * 5

    try:
        values = cursor.find().sort('_id', -1).skip(skip_count).limit(5)

        posts = list(values)

        if len(posts) > 0:
            for value in posts:
                value["_id"] = str(value["_id"])
                print(value["_id"])

            return {"message": "success", "posts": posts}
        else:
            return {"message": "success", "posts": []}

    except Exception as e:
        print(e)
        return {"message": "error"}


@app.get("/getPosts")
async def get_posts_by_id(type: str = "new", id: str = None):
    try:
        if type == "old":
            if id is not None:
                values = cursor.find({"_id": {"$lt": ObjectId(id)}}).limit(5)
                posts = list(values)
                posts.reverse()
            else:
                values = cursor.find().sort('_id', -1).limit(5)
                posts = list(values)
        elif type == "new":
            if id is not None:
                values = cursor.find({"_id": {"$gt": ObjectId(id)}})
                posts = list(values)
            else:
                return
        else:
            return {"message": "error, you can only use the types old and new"}

        if len(posts) > 0:
            for value in posts:
                value["_id"] = str(value["_id"])
                print(value["_id"])

            return {"message": "success", "posts": posts}
        else:
            return {"message": "success", "posts": []}

    except Exception as e:
        print(e)
        return {"message": "error"}


@app.get("/getOwnPosts/{username}")
async def get_own_posts(username: str):
    try:
        values = cursor.find({"username": username})

        posts = list(values)

        if len(posts) > 0:
            for value in posts:
                value["_id"] = str(value["_id"])
                print(value["_id"])

            return {"message": "success", "posts": posts}
        else:
            return {"message": "success", "posts": []}

    except Exception as e:
        print(e)
        return {"message": "error"}


@app.delete("/delete")
async def delete_post(values: dict):
    try:
        expected_keys = {"id"}
        if values.keys() == expected_keys:
            cursor.delete_one({"_id": ObjectId(values["id"])})
            return {"message": "success"}
        else:
            print("Unexpected Keys")
            return {"message": "error"}
    except Exception as e:
        print(e)
        return {"message": "error"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


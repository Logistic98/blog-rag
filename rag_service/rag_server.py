# -*- coding: utf-8 -*-

import uvicorn

if __name__ == "__main__":
    uvicorn.run("fastapi_app:app", host="0.0.0.0", port=18888)

import zlib

import httpx
from sanic import Sanic
from sanic.log import logger
from sanic_cors import CORS

app = Sanic("GeminiProxy")
CORS(app)

# 代理路径
PROXY_PATH = "/stream_proxy"
# 目标地址
TARGET_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:streamGenerateContent"

PROXY_URL = "http://127.0.0.1:1087"  # 本地代理地址


@app.route(PROXY_PATH + '/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
async def proxy(request, path):
    responseStream = await request.respond(content_type='application/json')
    url = TARGET_URL
    try:
        async with httpx.AsyncClient(proxies=PROXY_URL) as client:
            async with client.stream("POST", url, json=request.json, params={'key': request.args.get("key")}) as resp:
                # decompressor = zlib.decompressobj(16 + zlib.MAX_WBITS)
                # for chunk in r.iter_raw():
                #     print(chunk)
                async for chunk in generate_response(resp):
                    try:
                        # data = decompressor.decompress(chunk)
                        # data = chunk.decode()
                        # if not data:
                        #     continue
                        # print(data)
                        await responseStream.send(chunk)
                        # print(data.decode().strip())
                        # js = json.loads(data.decode().strip())
                        # print(js)
                        # print("----------------------------------------------------")
                    except Exception as e:
                        print(f"Decompression error: {e}")
    except Exception as e:

        logger.error(e)

    await responseStream.eof()
    return responseStream


async def generate_response(resp):
    async for chunk in resp.aiter_bytes():
        yield chunk


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)

import httpx
import asyncio

async def check_lever():
    print("Starting check...")
    async with httpx.AsyncClient() as client:
        try:
            print("Making request...")
            response = await client.get('https://api.lever.co/v0/postings/netflix?mode=json')
            print(f'Status: {response.status_code}')
            print(f'Content-Type: {response.headers.get("content-type")}')
            print(f'Content length: {len(response.text)}')
            print('First 500 chars:')
            print(repr(response.text[:500]))
        except Exception as e:
            print(f'Error: {e}')
            import traceback
            traceback.print_exc()

print("Running check...")
asyncio.run(check_lever())
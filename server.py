import asyncio
import json
import websockets

connected = {}
rooms = {}

async def handler(ws, path):
    player_id = None
    try:
        async for msg in ws:
            data = json.loads(msg)
            if data["type"] == "auth":
                player_id = data["player_id"]
                connected[player_id] = ws
                print(f"[+] {player_id} connected")
            elif data["type"] == "create_room":
                room_id = str(len(rooms) + 1)
                rooms[room_id] = [player_id]
                await ws.send(json.dumps({"type": "room_created", "room_id": room_id}))
            elif data["type"] == "join_room":
                rid = data["data"]["room_id"]
                if rid in rooms:
                    rooms[rid].append(player_id)
                    await ws.send(json.dumps({"type": "room_joined", "room_id": rid}))
            elif data["type"] in ["move", "shoot"]:
                rid = data.get("room_id")
                if rid in rooms:
                    for pid in rooms[rid]:
                        if pid != player_id and pid in connected:
                            await connected[pid].send(json.dumps(data))
    except:
        pass
    finally:
        if player_id:
            connected.pop(player_id, None)

start = websockets.serve(handler, "0.0.0.0", 8080)
print("[SERVER] Running on port 8080")
asyncio.get_event_loop().run_until_complete(start)
asyncio.get_event_loop().run_forever()

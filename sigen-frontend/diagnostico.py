import httpx
import asyncio

async def main():
    print("Iniciando diagnóstico de puertos...")
    
    # 1. FastAPI (8002)
    print("\n[1] Verificando FastAPI Backend (Puerto 8002)...")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get("http://localhost:8002/docs", timeout=5.0)
            print(f"  ✅ OK: FastAPI responde en el puerto 8002 (Status: {resp.status_code})")
    except Exception as e:
        print(f"  ❌ ERROR: FastAPI NO responde en 8002. ¿Está corriendo? Detalles: {type(e).__name__}")

    # 2. Reflex Backend (8001)
    print("\n[2] Verificando Reflex Backend Interno (Puerto 8001)...")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get("http://localhost:8001/ping", timeout=5.0)
            print(f"  ✅ OK: Reflex Backend responde en 8001 (Status: {resp.status_code})")
    except Exception as e:
        print(f"  ❌ ERROR: Reflex Backend NO responde en 8001. Detalles: {type(e).__name__}")

    # 3. Reflex Frontend (3000)
    print("\n[3] Verificando Reflex Frontend (Puerto 3000)...")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get("http://localhost:3000", timeout=5.0)
            print(f"  ✅ OK: Reflex Frontend responde en 3000 (Status: {resp.status_code})")
    except Exception as e:
        print(f"  ❌ ERROR: Frontend NO responde en 3000. Detalles: {type(e).__name__}")

if __name__ == "__main__":
    asyncio.run(main())

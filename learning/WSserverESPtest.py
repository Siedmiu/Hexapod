import asyncio
import websockets
import logging
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("WebSocketServer")

connected_clients = set()

def format_numbers_to_hex(message_str):
    try:
        data = json.loads(message_str)
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, int):
                    data[key] = f"0x{value:X}"
        return json.dumps(data)
    except:
        return message_str

async def handle_client(websocket):
    """
    Obsługa połączeń klientów.
    
    Args:
        websocket: Połączenie WebSocket
    """
    client_address = websocket.remote_address[0]
    
    connected_clients.add(websocket)
    
    logger.info(f"Nowy klient połączony z {client_address}")
    
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                
                if isinstance(data, dict) and data.get("type") == "ping":
                    logger.debug(f"Otrzymano ping od klienta {client_address}")
                    continue
                
                logger.info(f"Otrzymano wiadomość od klienta {client_address}: {format_numbers_to_hex(message)}")
                
                await broadcast_message(message, websocket)
            
            except json.JSONDecodeError:
                logger.warning(f"Otrzymano nieprawidłowy format JSON od klienta {client_address}: {message}")
    
    except websockets.exceptions.ConnectionClosed as e:
        logger.info(f"Połączenie klienta {client_address} zamknięte: {e}")
    except Exception as e:
        logger.error(f"Błąd obsługi klienta {client_address}: {e}")
    finally:
        connected_clients.remove(websocket)
        logger.info(f"Klient {client_address} rozłączony")

async def broadcast_message(message, sender=None):
    """
    Przekazuje wiadomość do wszystkich klientów oprócz nadawcy.
    
    Args:
        message: Wiadomość do przekazania
        sender: Klient wysyłający wiadomość (wykluczony z rozgłoszenia)
    """
    clients_to_send = [ws for ws in connected_clients if ws != sender]
    
    if clients_to_send:
        logger.info(f"Przekazywanie wiadomości do {len(clients_to_send)} klientów: {format_numbers_to_hex(message)}")
        for client in clients_to_send:
            try:
                await client.send(message)
            except Exception as e:
                logger.error(f"Błąd przekazywania wiadomości: {e}")

async def start_server():
    """
    Uruchomienie serwera WebSocket.
    """
    host = "0.0.0.0"  # Nasłuchuj na wszystkich interfejsach sieciowych
    port = 8765
    
    server = await websockets.serve(handle_client, host, port)
    logger.info(f"Serwer WebSocket uruchomiony na {host}:{port}")
    
    await server.wait_closed()

if __name__ == "__main__":
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        logger.info("Serwer zatrzymany przez użytkownika")
    except Exception as e:
        logger.error(f"Błąd serwera: {e}")

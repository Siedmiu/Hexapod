# test_websocket.py - samodzielny skrypt testowy
import websocket
import time

def test_esp_websocket():
    try:
        print("Łączenie z ESP32...")
        ws = websocket.WebSocket()
        ws.connect("ws://192.168.229.80:80/ws")
        print("Połączono! Wysyłanie wiadomości testowej...")
        
        test_message = "hello_from_simple_test_script"
        ws.send(test_message)
        print(f"Wysłano: {test_message}")
        
        # Opcjonalnie możesz dodać odbieranie odpowiedzi
        response = ws.recv()
        print(f"Odebrano odpowiedź: {response}")
        
        time.sleep(1)
        ws.close()
        print("Test zakończony pomyślnie.")
        return True
    except Exception as e:
        print(f"Błąd podczas testu: {e}")
        return False

if __name__ == "__main__":
    test_esp_websocket()
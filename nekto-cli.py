import time, datetime
import pika
import threading
import json
import sys
import platform

def send_message(room='teste'):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', credentials=pika.PlainCredentials('py', 'python')))
    channel = connection.channel()
    channel.queue_declare(queue='chat_queue')
    channel.queue_bind(queue='chat_queue', exchange='chat', routing_key=room)
    
    time.sleep(1)

    try: 
        while True:
            message = input(' >> ')

            channel.basic_publish(
                exchange='chat',
                routing_key=room,
                body=json.dumps({ 
                                    'user': user, 
                                    'message': message, 
                                    'time': str(datetime.datetime.now().strftime('%H:%M'))
                                })
            )
    except KeyboardInterrupt:
        print("Exiting chat...")
        connection.close()
        sys.exit(0)

def receive_message(room, user):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', credentials=pika.PlainCredentials('py', 'python')))
        channel = connection.channel()
        channel.queue_declare(queue='chat_queue')
        channel.queue_bind(queue='chat_queue', exchange='chat', routing_key=room)

        print(" >> Now you are at \033[1m", room, "\033[0m. It's time to chat!")
        print(" >> To exit press Ctrl+C")
        print(" --------------------------------------- ")

        def callback(ch, method, properties, body):
            message_payload = json.loads(body)
            if message_payload['user'] == user: return
            
            print(f" [{message_payload['time']}]\033[1m {message_payload['user']}\033[0m said: {message_payload['message']}")

        channel.basic_consume(queue='chat_queue', on_message_callback=callback, auto_ack=True)
        channel.start_consuming()

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":

    print(" ------------------------------------------------- ")
    print("                 _    _                   _ _  ")
    print("      _ __   ___| | _| |_ ___         ___| (_) ")
    print("     | '_ \ / _ | |/ | __/ _ \ _____ / __| | | ")
    print("     | | | |  __|   <| || (_) |_____| (__| | | ")
    print("     |_| |_|\___|_|\_\\\__\___/       \___|_|_| \n")
    print(" ------------------------------------------------- ")
    print(" >> @mateusolorenzatti")
    print(" >> Version 1.0")
    print(" >> Env")
    print("     - OS ", platform.system(), platform.release())
    print("     - Python ", sys.version)
    print("     - Rabbitmq 3.12.12")
    print("     - Erlang 25.3.2.8")
    print(" ------------------------------------------------- ")

    user = input(' >> Insert your user name: ')
    room = input(' >> Insert your room: ')

    print(" ------------------------------------------------- ")

    # Start a thread to send messages
    send_thread = threading.Thread(target=send_message, args=(room,))
    send_thread.daemon = True
    send_thread.start()

    # Start a thread to receive messages
    receive_thread = threading.Thread(target=receive_message, args=(room,user,))
    receive_thread.daemon = True
    receive_thread.start()

    # Join the threads to prevent the main thread from exiting
    send_thread.join()
    receive_thread.join()

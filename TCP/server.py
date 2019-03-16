import asyncio
import functools
import logging

logger = logging.getLogger(__name__)

user_cnt = 0

HELP = "%Commandes: !help, !quit, !join:pseudo, !list\n"


def broadcast(room, msg):
    for pseudo, writer in room.values():
        writer.write(msg)


def unicast(room, msg, users):
    for pseudo, writer in room.values():
        if pseudo not in users:
            continue
        writer.write(msg)


async def handle_client(room, reader, writer):
    global user_cnt

    user = f"eleve_{user_cnt}"
    user_cnt += 1
    logger.info(f'client {user} connected')

    pseudo = None

    try:
        welcome = f"%bienvenue {user} sur le serveur de chat d'ISN! Entrez la commande !help pour plus d'aide\n"
        writer.write(welcome.encode())

        while True:
            line = await reader.readline()

            if not line:
                break

            msg = line.decode().strip()
            logger.info('msg from %s: %s', user, msg)

            if msg.startswith('!'):
                # Command msg
                if msg == '!quit':
                    # User wants to quit
                    break

                elif msg == '!help':
                    # Show help message
                    writer.write(HELP.encode())

                elif msg.startswith('!join:'):
                    if pseudo:
                        writer.write(f'%vous êtes déjà connecté en tant que {pseudo}\n'.encode())
                    else:
                        # Join the chat with given pseudo
                        choice = msg.split(':', 1)[1]

                        if choice in [p for p, w in room.values()]:
                            writer.write(f'%pseudo deja utilisé!\n'.encode())
                        else:
                            pseudo = choice
                            logger.info('user %s joining as: %s', user, pseudo)
                            writer.write(f'%vous avez rejoint le chat en tant que {pseudo}\n'.encode())
                            broadcast(room, f'%utilisateur {pseudo} a rejoint le chat\n'.encode())
                            room[user] = (pseudo, writer)

                elif msg == '!list':
                    # List current chat users
                    l = [p for p, w in room.values()]
                    writer.write(f'%utilisateurs: {", ".join(l)}\n'.encode())

                else:
                    # Invalid command
                    writer.write(f'%commande non valide: {msg}\n'.encode())

            elif msg.startswith('@'):
                # Unicast message
                if pseudo is None:
                    writer.write(f'%il faut joindre le chat avant de parler\n'.encode())

                elif ':' not in msg:
                    writer.write(f'%message unicast non valide: {msg}\n'.encode())

                else:
                    dest, msg = msg[1:].split(':', 1)
                    msg = f'{pseudo}>{msg}\n'.encode()
                    if not any (p for p, w in room.values() if p == dest):
                        writer.write(f'%destinataire non valide: {dest}\n'.encode())
                    else:
                        unicast(room, msg, [pseudo, dest])
            else:
                # Broadcast message
                if pseudo is None:
                    writer.write(f'%il faut joindre le chat avant de parler\n'.encode())
                else:
                    msg = f'{pseudo}>{msg}\n'.encode()
                    broadcast(room, msg)

    finally:
        logger.info(f'client {user} disconnecting')
        room.pop(user, None)
        if pseudo:
            broadcast(room, f'%utilisateur {pseudo} a quitté le chat\n'.encode())
        writer.close()


async def main():
    """
    Main function, may be called from shotcut command
    """
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--logging', type=int, default=10, help='python logging level')
    parser.add_argument('-a', '--address', default='0.0.0.0', help='server address')
    parser.add_argument('-p', '--port', type=int, default=9999, help='server port')
    args = parser.parse_args()

    logging.basicConfig()
    logger.setLevel(args.logging)

    logger.info('start serving on port %s', args.port)
    room = {}
    server = await asyncio.start_server(functools.partial(handle_client, room), host=args.address, port=args.port)

    try:
        await server.serve_forever()
    finally:
        server.close()


if __name__ == '__main__':
    asyncio.run(main())
